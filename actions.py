"""Business logic and actions for GreenBin application."""
from nicegui import ui
import asyncio
import random
import models
import state
import routing
from structures.priority_queue import PriorityQueue

# Global reference to refresh_ui function, to be set by app.py
_refresh_ui_callback = None

# Set the UI refresh callback function
def set_refresh_ui_callback(callback):
    global _refresh_ui_callback
    _refresh_ui_callback = callback

# Trigger UI refresh
def refresh_ui():
    if _refresh_ui_callback:
        _refresh_ui_callback()

# ---------- Utility / Business Logic ----------

def show_popup(message, type="info"):
    """Show a popup dialog with a message."""
    color = "blue"
    if type == "positive": color = "green"
    elif type == "negative": color = "red"
    elif type == "warning": color = "orange"
    
    ui.notify(message, type=type if type in ['positive', 'negative', 'warning', 'info'] else 'info', color=color)

# Save all application state to storage
def save_all():
    state.save_all()

# ---------- Actions & domain functions ----------

# Dispatch and empty a bin, logging the collection
def dispatch_bin_logic(bin_id, silent=False, refresh=True, skip_undo=False):
    bin_obj = state.bins_map.get(bin_id)
    if not bin_obj:
        if not silent:
            show_popup("Bin not found", type="negative")
        return
    prev_fill = bin_obj.fill_level
    bin_obj.fill_level = 0
    record = {
        "timestamp": models.get_iso_timestamp(),
        "bin_id": bin_id,
        "type": bin_obj.waste_type,
        "area": f"{bin_obj.lat:.4f},{bin_obj.lon:.4f}",
        "status": "Collected",
        "prev_fill": prev_fill,
        "source": "request"  # Track that this came from a request
    }
    state.history.append(record)
    # store undo info on stack (action, payload) - unless skip_undo is True
    if not skip_undo:
        state.request_stack.append(("dispatch", record))
    save_all()
    if not silent:
        show_popup(f"Dispatched and emptied {bin_id}", type="positive")
    if refresh:
        refresh_ui()

# Create a new collection request for a specific bin
def request_collection_action(bin_id):
    if not state.bins_map.get(bin_id):
        show_popup("Bin ID not found", type="negative")
        return
    
    # Check if a request already exists for this bin
    if any(r.bin_id == bin_id for r in state.requests):
        show_popup(f"Request already exists for {bin_id}", type="warning")
        return
    
    req = models.CollectionRequest(bin_id=bin_id)
    state.requests.append(req)
    # Log to history
    state.history.append({
        "bin_id": bin_id,
        "timestamp": models.get_iso_timestamp(),
        "status": "Request Processed",
        "action": "Created",
        "type": next((b.waste_type for b in state.bins if b.id == bin_id), "Unknown")
    })
    state.request_stack.append(("request_add", req))
    save_all()
    show_popup(f"Request added for {bin_id}", type="positive")
    refresh_ui()

# Process the next pending collection request
def process_request_action():
    if not state.requests:
        show_popup("No pending requests", type="info")
        return
    req = state.requests.pop(0)
    # Log to history
    state.history.append({
        "bin_id": req.bin_id,
        "timestamp": models.get_iso_timestamp(),
        "status": "Request Processed",
        "action": "Processed",
        "type": getattr(state.bins_map.get(req.bin_id), "waste_type", "Unknown")
    })
    # dispatch the bin
    dispatch_bin_logic(req.bin_id)
    save_all()
    refresh_ui()

# Undo the last action (dispatch, request, update, or add bin)
def undo_last_action():
    if not state.request_stack:
        show_popup("Nothing to undo", type="info")
        return
    
    action, payload = state.request_stack.pop()
    
    if action == "dispatch":
        # payload is history record
        entry = payload
        # Restore fill level
        b = state.bins_map.get(entry["bin_id"])
        if b:
            b.fill_level = entry.get("prev_fill", 0)
            # Remove from history
            if entry in state.history:
                state.history.remove(entry)
            save_all()
            show_popup(f"Undo: Restored {b.id} to {b.fill_level}%", type="info")
            
    elif action == "request_add":
        # payload is request object - undo creating a request
        req = payload
        if req in state.requests:
            state.requests.remove(req)
            save_all()
            show_popup(f"Undo: Removed request for {req.bin_id}", type="info")
    
    elif action == "request_approve":
        # payload is request object - restore it to the queue and undo the dispatch
        req = payload
        state.requests.append(req)
        # Also need to undo the bin dispatch
        b = state.bins_map.get(req.bin_id)
        if b:
            # Find the most recent dispatch entry for this bin
            for entry in reversed(state.history):
                if entry.get("bin_id") == req.bin_id and entry.get("status") == "Collected":
                    b.fill_level = entry.get("prev_fill", 0)
                    state.history.remove(entry)
                    break
        save_all()
        show_popup(f"Undo: Restored request for {req.bin_id} and undid dispatch", type="info")
    
    elif action == "request_reject":
        # payload is request object - restore it to the queue
        req = payload
        state.requests.append(req)
        save_all()
        show_popup(f"Undo: Restored request for {req.bin_id}", type="info")
            
    elif action == "update_fill":
        # payload is (bin_id, old_fill)
        bid, old_fill = payload
        b = state.bins_map.get(bid)
        if b:
            b.fill_level = old_fill
            save_all()
            show_popup(f"Undo: Restored {bid} fill to {old_fill}%", type="info")
            
    elif action == "add_bin":
        # payload is bin_id
        bid = payload
        b = state.bins_map.get(bid)
        if b:
            state.bins.remove(b)
            state.bins_map.remove(bid)
            save_all()
            show_popup(f"Undo: Removed bin {bid}", type="info")
    refresh_ui()

# Run the urgent collection sequence asynchronously
async def run_urgent_collection_sequence(ordered_bins, client):
    with client:
        count = 0
        for b in ordered_bins:
            dispatch_bin_logic(b.id, silent=True, refresh=True)
            count += 1
            ui.notify(f"Priority Collection: Bin {b.id} emptied", type="positive")
            await asyncio.sleep(2.5)
            
        show_popup(f"Priority Collection: Collected {count} bins based on priority.", type="positive")

# Collect all urgent bins (>=80% full) using priority queue
async def collect_urgent_action():
    # 1. Identify Critical Bins (>= 80%)
    # 2. Add to Priority Queue (Max-Heap based on fill level)
    pq = PriorityQueue()
    critical_bins = []
    
    for b in state.bins:
        if b.fill_level >= 80:
            pq.push(b)
            critical_bins.append(b)
            
    if not critical_bins:
        show_popup("No critical bins (>=80%) to collect", type="info")
        return

    # 3. Pop from PQ to get collection order (highest fill first)
    ordered_bins = []
    while len(pq) > 0:
        ordered_bins.append(pq.pop())
        
    
    # 5. Dispatch in optimized order (Background Task)
    # Capture client context
    client = ui.context.client
    asyncio.create_task(run_urgent_collection_sequence(ordered_bins, client))

# Collect all non-empty bins using priority queue
async def collect_all_bins_action():
    # 1. Add ALL bins to Priority Queue (Max-Heap based on fill level)
    pq = PriorityQueue()
    all_bins = []
    
    for b in state.bins:
        if b.fill_level > 0: # Only collect non-empty bins
            pq.push(b)
            all_bins.append(b)
            
    if not all_bins:
        show_popup("No bins to collect", type="info")
        return

    # 2. Pop from PQ to get collection order (highest fill first)
    ordered_bins = []
    while len(pq) > 0:
        ordered_bins.append(pq.pop())
        
    # 3. Dispatch in optimized order (Background Task)
    client = ui.context.client
    asyncio.create_task(run_urgent_collection_sequence(ordered_bins, client))

# Add a new bin to the system
def add_bin_action(id, btype, lat, lon, fill):
    try:
        # Check for duplicate ID
        if state.bins_map.get(str(id)):
            show_popup(f"Bin ID {id} already exists", type="warning")
            return

        new_bin = models.Bin(id=str(id), waste_type=btype, lat=float(lat), lon=float(lon), fill_level=int(fill))
        state.bins.append(new_bin)
        state.bins_map.set(str(id), new_bin)
        state.request_stack.append(("add_bin", str(id)))
        save_all()
        save_all()
        show_popup(f"Bin {id} added", type="positive")
        refresh_ui()
    except Exception as e:
        show_popup(f"Error adding bin: {e}", type="negative")

# Update the fill level of a specific bin
def update_fill_action(bin_id, new_fill):
    b = state.bins_map.get(bin_id)
    if not b:
        show_popup("Bin not found", type="negative")
        return
    old_fill = b.fill_level
    b.fill_level = int(new_fill)
    
    # Log to history
    state.history.append({
        "bin_id": bin_id,
        "timestamp": models.get_iso_timestamp(),
        "status": "Updated",
        "prev_fill": old_fill,
        "new_fill": new_fill,
        "type": b.waste_type
    })
    
    state.request_stack.append(("update_fill", (bin_id, old_fill)))
    save_all()
    save_all()
    show_popup(f"Updated {bin_id} to {new_fill}%", type="positive")
    refresh_ui()

# Simulate IoT sensor updates for all bins
def simulate_updates_action():
    ui.notify("Simulating updates...", type="info")
    print("Simulating updates...")
    updates_count = 0
    for b in state.bins:
        old_fill = b.fill_level
        b.simulate_iot_update()
        if b.fill_level != old_fill:
            state.history.append({
                "bin_id": b.id,
                "timestamp": models.get_iso_timestamp(),
                "status": "IoT Update",
                "prev_fill": old_fill,
                "new_fill": b.fill_level,
                "type": b.waste_type
            })
            updates_count += 1
    save_all()
    print(f"Updates saved. {updates_count} bins updated. Showing popup.")
    show_popup(f"Simulated IoT updates for {updates_count} bins", type="info")
    refresh_ui()
