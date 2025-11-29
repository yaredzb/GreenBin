from nicegui import ui, app
from views import dashboard, bins as bins_view, requests as requests_view, history as history_view, dispatch as dispatch_view, facilities as facilities_view, predictions as predictions_view
from views.components import create_stat_card
from collections import deque
import datetime
import random
import os
import pandas as pd
import models
from models.facility import Facility
import storage
import routing
from structures.avl_tree import AVLTree
from structures.priority_queue import PriorityQueue
from structures.hash_map import HashMap
from structures.graph import Graph
from algorithms.sorting import merge_sort
from algorithms.searching import search_by_substring, linear_search
from structures.min_heap import MinHeap

# ---------- State & Data ----------
bins = storage.load_bins()
requests = storage.load_requests()
history = storage.load_history()
facilities = storage.load_facilities()
request_stack = deque()
current_view = "dashboard"  # Initialize current view

# AVL Tree for Facility Lookup (Key: Facility ID)
facilities_avl = AVLTree()
for f in facilities:
    facilities_avl.insert(f.id, f)

# seed sample bins if empty (keeps previous logic)
if not bins:
    for i in range(1, 21):
        b_id = f"B{100 + i}"
        b_type = random.choice(["Household", "Industrial", "Recyclable", "Organic"])
        b_lat = 25.2048 + random.uniform(-0.04, 0.04)
        b_lon = 55.2708 + random.uniform(-0.04, 0.04)
        b_fill = random.randint(0, 95)
        bins.append(models.Bin(id=b_id, waste_type=b_type, lat=b_lat, lon=b_lon, fill_level=b_fill))
    storage.save_bins(bins)

# seed facilities if empty
if not facilities:
    for i in range(1, 6):
        f_id = f"F{100 + i}"
        f_lat = 25.2048 + random.uniform(-0.02, 0.02)
        f_lon = 55.2708 + random.uniform(-0.02, 0.02)
        f_cap = random.randint(1000, 5000)
        f_eff = round(random.uniform(50.0, 99.9), 1)
        new_f = Facility(id=f_id, lat=f_lat, lon=f_lon, capacity=f_cap, efficiency=f_eff)
        facilities.append(new_f)
        facilities_avl.insert(new_f.id, new_f)
    storage.save_facilities(facilities)

# Build road network graph for Dijkstra's algorithm
road_graph = Graph()

def build_road_network():
    """Build road network connecting bins and facilities."""
    global road_graph
    road_graph = Graph()
    
    # Add all bins and facilities as nodes
    for b in bins:
        road_graph.add_node(b.id, b.lat, b.lon)
    for f in facilities:
        road_graph.add_node(f.id, f.lat, f.lon)
    
    # Connect each bin to its 3 nearest neighbors
    all_nodes = [(b.id, b.lat, b.lon) for b in bins] + [(f.id, f.lat, f.lon) for f in facilities]
    
    for node_id, lat, lon in all_nodes:
        # Find 3 nearest neighbors
        distances = []
        for other_id, other_lat, other_lon in all_nodes:
            if node_id != other_id:
                dist = routing.calculate_distance(lat, lon, other_lat, other_lon) * 111  # km
                distances.append((dist, other_id))
        
        distances.sort()
        for dist, neighbor_id in distances[:3]:
            road_graph.add_edge(node_id, neighbor_id, dist)
    
    # Ensure each bin has direct connection to nearest facility
    for b in bins:
        nearest_facility = min(facilities, 
                              key=lambda f: routing.calculate_distance(b.lat, b.lon, f.lat, f.lon))
        dist = routing.calculate_distance(b.lat, b.lon, nearest_facility.lat, nearest_facility.lon) * 111
        road_graph.add_edge(b.id, nearest_facility.id, dist)

build_road_network()

# UI state
current_view = "dashboard"   # dashboard, bins, requests, history, dispatch, facilities, predictions
content_container = None

DEPOT_LAT = 25.2048
DEPOT_LON = 55.2708

def get_distance_to_depot(lat, lon):
    return routing.calculate_distance(lat, lon, DEPOT_LAT, DEPOT_LON) * 111 # approx km

# ---------- Utility / Business Logic ----------

def show_popup(message, type="info"):
    """Show a popup dialog with a message."""
    with ui.dialog() as dialog, ui.card():
        ui.label(message).classes("text-lg font-medium mb-4")
        with ui.row().classes("w-full justify-end"):
            ui.button("OK", on_click=dialog.close).classes("bg-blue-600 text-white")
    dialog.open()

def save_all():
    storage.save_bins(bins)
    storage.save_requests(requests)
    storage.save_history(history)
    storage.save_facilities(facilities)

# ---------- Actions & domain functions ----------
def dispatch_bin_logic(bin_id):
    bin_obj = next((b for b in bins if b.id == bin_id), None)
    if not bin_obj:
        show_popup("Bin not found", type="negative")
        return
    prev_fill = bin_obj.fill_level
    bin_obj.fill_level = 0
    record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "bin_id": bin_id,
        "type": bin_obj.waste_type,
        "area": f"{bin_obj.lat:.4f},{bin_obj.lon:.4f}",
        "status": "Collected",
        "prev_fill": prev_fill,
        "source": "request"  # Track that this came from a request
    }
    history.append(record)
    # store undo info on stack (action, payload)
    request_stack.append(("dispatch", record))
    save_all()
    ui.notify(f"Dispatched and emptied {bin_id}", color="positive")
    refresh_ui()

def request_collection_action(bin_id):
    if not any(b.id == bin_id for b in bins):
        show_popup("Bin ID not found", type="negative")
        return
    req = models.CollectionRequest(bin_id=bin_id)
    requests.append(req)
    request_stack.append(("request_add", req))
    save_all()
    show_popup(f"Request added for {bin_id}", type="positive")
    refresh_ui()

def process_request_action():
    if not requests:
        show_popup("No pending requests", type="info")
        return
    req = requests.pop(0)
    # dispatch the bin
    dispatch_bin_logic(req.bin_id)
    save_all()
    refresh_ui()

def undo_last_action():
    if not request_stack:
        show_popup("Nothing to undo", type="info")
        return
    act, payload = request_stack.pop()
    if act == "request_add":
        # payload is CollectionRequest instance
        if payload in requests:
            requests.remove(payload)
            save_all()
            show_popup(f"Undid request for {payload.bin_id}", type="info")
    elif act == "dispatch":
        # payload is the history record
        # restore fill level
        rec = payload
        b = next((x for x in bins if x.id == rec["bin_id"]), None)
        if b:
            b.fill_level = rec.get("prev_fill", 0)
            # remove last matching history entry
            for i in range(len(history)-1, -1, -1):
                if history[i].get("bin_id") == rec["bin_id"] and history[i].get("timestamp") == rec["timestamp"]:
                    history.pop(i)
                    break
            save_all()
            show_popup(f"Undo: Restored {b.id} to {b.fill_level}%", type="info")
    elif act == "update_fill":
        # payload is (bin_id, old_fill)
        bid, old_fill = payload
        b = next((x for x in bins if x.id == bid), None)
        if b:
            b.fill_level = old_fill
            save_all()
            show_popup(f"Undo: Restored {bid} fill to {old_fill}%", type="info")
    elif act == "add_bin":
        # payload is bin_id
        bid = payload
        b = next((x for x in bins if x.id == bid), None)
        if b:
            bins.remove(b)
            save_all()
            show_popup(f"Undo: Removed bin {bid}", type="info")
    refresh_ui()

def collect_urgent_action():
    # 1. Identify Critical Bins (>= 85%)
    # 2. Add to Priority Queue (Max-Heap based on fill level)
    pq = PriorityQueue()
    critical_bins = []
    
    for b in bins:
        if b.fill_level >= 80:
            pq.push(b)
            critical_bins.append(b)
            
    if not critical_bins:
        show_popup("No critical bins (>=80%) to collect", type="info")
        return

    # 3. Pop from PQ to get collection order (highest fill first)
    # We will use this order to determine which bins to route
    ordered_bins = []
    while len(pq) > 0:
        ordered_bins.append(pq.pop())
        
    # 4. Route Optimization (Dijkstra / Nearest Neighbor)
    # Start from Depot (25.2048, 55.2708)
    depot_lat, depot_lon = 25.2048, 55.2708
    optimized_path_coords = routing.optimize_route(depot_lat, depot_lon, ordered_bins)
    
    # 5. Dispatch in optimized order
    
    count = 0
    for b in ordered_bins:
        dispatch_bin_logic(b.id)
        count += 1
        
    show_popup(f"Priority Collection: Collected {count} critical bins. Route optimized.", type="positive")
    refresh_ui()

def add_bin_action(id, btype, lat, lon, fill):
    try:
        new_bin = models.Bin(id=str(id), waste_type=btype, lat=float(lat), lon=float(lon), fill_level=int(fill))
        bins.append(new_bin)
        request_stack.append(("add_bin", str(id)))
        save_all()
        save_all()
        show_popup(f"Bin {id} added", type="positive")
        refresh_ui()
    except Exception as e:
        show_popup(f"Error adding bin: {e}", type="negative")

def update_fill_action(bin_id, new_fill):
    b = next((x for x in bins if x.id == bin_id), None)
    if not b:
        show_popup("Bin not found", type="negative")
        return
    old_fill = b.fill_level
    b.fill_level = int(new_fill)
    request_stack.append(("update_fill", (bin_id, old_fill)))
    save_all()
    save_all()
    show_popup(f"Updated {bin_id} to {new_fill}%", type="positive")
    refresh_ui()

# ---------- UI helper components ----------

def status_badge(fill_level):
    # 0% - empty, 1-25% low load, 25-50% -medium load, 50-75% - high load, 85% -100 critical
    # Note: 75-85 is undefined in prompt, assuming High Load covers 50-85
    if fill_level >= 85:
        return ui.label("CRITICAL").classes("px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold")
    if fill_level >= 50:
        return ui.label("HIGH LOAD").classes("px-2 py-1 bg-orange-100 text-orange-700 rounded-full text-xs")
    if fill_level >= 25:
        return ui.label("MEDIUM").classes("px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs")
    if fill_level > 0:
        return ui.label("LOW").classes("px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs")
    return ui.label("EMPTY").classes("px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs")

# ---------- Rendering / Views ----------
def navigate_to(view_name):
    global current_view
    current_view = view_name
    refresh_ui()

def refresh_ui():
    """Clear and re-render the content container."""
    global content_container
    refresh_sidebar()  # Update sidebar to show active tab
    if content_container:
        content_container.clear()
        with content_container:
            if current_view == "dashboard":
                dashboard.render_dashboard(
                    bins, history, requests, 
                    collect_urgent_action, dispatch_bin_logic, 
                    save_all, refresh_ui
                )
            elif current_view == "bins":
                bins_view.render_bin_registry(
                    bins, 
                    open_add_bin_dialog, 
                    open_update_fill_dialog, 
                    dispatch_bin_logic
                )
            elif current_view == "requests":
                requests_view.render_requests(
                    requests,
                    undo_last_action,
                    process_request_action,
                    lambda bid: requests_view.process_specific_request(bid, requests, request_stack, save_all, dispatch_bin_logic, refresh_ui),
                    lambda bid: requests_view.reject_specific_request(bid, requests, save_all, refresh_ui)
                )
            elif current_view == "history":
                history_view.render_history(history, get_distance_to_depot)
            elif current_view == "dispatch":
                dispatch_view.render_dispatch(bins, facilities, road_graph)
            elif current_view == "facilities":
                facilities_view.render_facility_report(facilities, facilities_avl, bins, history)
            elif current_view == "predictions":
                predictions_view.render_predictions(bins, history)

# ---------- Dialogs & small UI utilities ----------
def open_add_bin_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Add New Bin").classes("text-xl font-semibold")
        bid = ui.input(label="ID")
        btype = ui.select(["Household","Industrial","Recyclable","Organic"], label="Type")
        blat = ui.input(label="Latitude", value="25.2048")
        blon = ui.input(label="Longitude", value="55.2708")
        bfill = ui.number(label="Fill %", value=0, min=0, max=100)
        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Add", on_click=lambda: [add_bin_action(bid.value, btype.value, blat.value, blon.value, bfill.value), dialog.close()]).classes("bg-green-600 text-white")
    dialog.open()

def open_update_fill_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Update Fill Level").classes("text-xl font-semibold")
        
        # Bin ID dropdown selection
        bin_ids = [b.id for b in bins]
        bid = ui.select(
            options=bin_ids,
            label="Bin ID",
            value=bin_ids[0] if bin_ids else None
        ).classes("w-full")
        
        # Fill level input and slider synced
        fill_val = ui.number(label="New Fill %", value=0, min=0, max=100).classes("w-full")
        ui.slider(min=0, max=100, step=1).bind_value(fill_val).classes("w-full")
        
        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Update", on_click=lambda: [update_fill_action(bid.value, fill_val.value), dialog.close()]).classes("bg-blue-600 text-white")
    dialog.open()

def open_request_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Request Collection").classes("text-xl font-semibold")
        
        # Bin ID dropdown selection
        bin_ids = [b.id for b in bins]
        bid = ui.select(
            options=bin_ids,
            label="Bin ID",
            value=bin_ids[0] if bin_ids else None
        ).classes("w-full")
        
        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Submit", on_click=lambda: [request_collection_action(bid.value), dialog.close()]).classes("bg-orange-500 text-white")
    dialog.open()

# ---------- Top-level UI (layout) ----------
ui.colors(primary='#10b981', secondary='#3B82F6', accent='#EF4444')

with ui.left_drawer(value=True).classes("w-64 border-r pt-6"):
    with ui.column().classes("p-6 gap-3 w-full"):
        ui.label("GreenBin").classes("text-4xl font-bold w-full text-center")
        ui.label("Smart Waste Collection").classes("text-xs text-gray-500 mb-4 w-full text-center")
        
        # Navigation container that will be refreshed
        sidebar_nav_container = ui.column().classes("w-full gap-3")
        
def refresh_sidebar():
    """Refresh sidebar navigation to update active state."""
    global sidebar_nav_container
    if sidebar_nav_container:
        sidebar_nav_container.clear()
        with sidebar_nav_container:
            def nav_btn(label, icon, view):
                def on_click():
                    navigate_to(view)
                is_active = current_view == view
                
                button = ui.button(on_click=on_click).props("flat no-caps align=left").classes(
                    f"w-full px-4 py-3 rounded-lg "
                    f"{'bg-green-700 text-white' if is_active else 'bg-gray-100 hover:bg-gray-200'}"
                )
                with button:
                    with ui.row().classes("items-center gap-3"):
                        ui.icon(icon, size="20px")
                        ui.label(label).classes("text-sm font-medium")
            
            nav_btn("Dashboard", "dashboard", "dashboard")
            nav_btn("Bins", "delete", "bins")
            nav_btn("Requests", "assignment", "requests")
            nav_btn("History", "history", "history")
            nav_btn("Dispatch", "local_shipping", "dispatch")
            nav_btn("Facilities", "factory", "facilities")
            nav_btn("Predictions", "trending_up", "predictions")

with ui.column().classes("p-8 gap-6 w-full"):
    # Header strip
    with ui.row().classes("items-center justify-between w-full"):
        with ui.row().classes("items-center gap-4"):
            ui.icon("recycling").classes("text-3xl text-green-600")
            ui.label("Waste Management Console").classes("text-2xl font-bold text-gray-800")
        
        with ui.row().classes("items-center gap-3"):
            ui.button("Undo", on_click=undo_last_action, icon="undo").props("flat color=grey-8")
            ui.button("New Request", on_click=open_request_dialog).classes("bg-orange-500 text-white shadow-md")
            ui.avatar(icon="person", color="grey-3", text_color="grey-8").classes("ml-2")

    # content container
    content_container = ui.column().classes("w-full")
    refresh_ui()



ui.run(title="GreenBin Dashboard", port=8085)
