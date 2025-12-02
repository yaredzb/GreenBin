"""Collection requests view for GreenBin application."""
from nicegui import ui
import pandas as pd
import state
from .tables import REQUESTS_COLUMNS, REQUESTS_STATUS_SLOT, REQUESTS_ACTIONS_SLOT

def process_specific_request(bin_id, save_all, dispatch_bin_logic, refresh_ui):
    """Process a specific collection request."""
    for i, r in enumerate(state.requests):
        if r.bin_id == bin_id:
            req = state.requests.pop(i)
            state.request_stack.append(("request_approve", req))
            save_all()
            dispatch_bin_logic(bin_id, skip_undo=True)
            ui.notify(f"Processed request for {bin_id}", color="positive")
            refresh_ui()
            return


def reject_specific_request(bin_id, save_all, refresh_ui):
    """Reject a specific collection request."""
    for i, r in enumerate(state.requests):
        if r.bin_id == bin_id:
            req = state.requests.pop(i)
            state.request_stack.append(("request_reject", req))
            save_all()
            ui.notify(f"Rejected request for {bin_id}", color="info")
            refresh_ui()
            return


def render_requests(process_request_action, process_specific_request_fn, reject_specific_request_fn):
    """Render the collection requests view."""
    with ui.row().classes("w-full justify-between items-center mb-6"):
        ui.label("Collection Requests").classes("text-2xl font-bold")
        with ui.row().classes("gap-3"):
            ui.button("Process Next", on_click=process_request_action, icon="play_arrow").classes("bg-blue-600 text-white")
    
    # Stats overview
    total_requests = len(state.requests)
    pending_requests = len([r for r in state.requests if r.status == "Pending"])
    processed_requests = len([h for h in state.history if h.get("action") == "Processed" or h.get("status") == "Request Processed"])
    
    with ui.row().classes("w-full gap-4 mb-6"):
        with ui.card().classes("flex-1 p-4 shadow-sm"):
            ui.label("Total Pending").classes("text-sm text-gray-600 mb-1")
            ui.label(str(total_requests)).classes("text-3xl font-bold text-blue-600")
        with ui.card().classes("flex-1 p-4 shadow-sm"):
            ui.label("Urgent").classes("text-sm text-gray-600 mb-1")
            ui.label(str(pending_requests)).classes("text-3xl font-bold text-orange-600")
        with ui.card().classes("flex-1 p-4 shadow-sm"):
            ui.label("Processed").classes("text-sm text-gray-600 mb-1")
            ui.label(str(processed_requests)).classes("text-3xl font-bold text-green-600")
    
    # Main requests card with dynamic table
    with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("Request Queue").classes("text-xl font-bold text-gray-800")
            if state.requests:
                ui.label(f"{len(state.requests)} requests").classes("text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full")
        
        # Dynamic table container
        table_container = ui.column().classes("w-full")
        
        def refresh_table():
            table_container.clear()
            with table_container:
                if state.requests:
                    df_requests = pd.DataFrame([r.to_dict() for r in state.requests])
                    
                    table = ui.table(
                        columns=REQUESTS_COLUMNS,
                        rows=df_requests.to_dict('records'),
                        pagination=10
                    ).classes("w-full").props('flat bordered dense separator="cell"')
                    
                    table.add_slot('body-cell-status', REQUESTS_STATUS_SLOT)
                    table.add_slot('body-cell-actions', REQUESTS_ACTIONS_SLOT)
                    
                    table.on('approve', lambda e: process_specific_request_fn(e.args['bin_id']))
                    table.on('reject', lambda e: reject_specific_request_fn(e.args['bin_id']))
                else:
                    with ui.column().classes("w-full items-center py-12"):
                        ui.icon("inbox", size="64px").classes("text-gray-300 mb-4")
                        ui.label("No pending requests").classes("text-xl font-semibold text-gray-600 mb-2")
                        ui.label("All collection requests have been processed").classes("text-sm text-gray-500")
        
        # Initial render
        refresh_table()
