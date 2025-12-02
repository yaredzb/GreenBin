from nicegui import ui, app
import actions
import routing
import state
from views import dashboard, bins as bins_view, requests as requests_view, history as history_view, dispatch as dispatch_view, facilities as facilities_view, predictions as predictions_view
from views import dialogs

# ---------- State ----------
bins = state.bins
requests = state.requests
history = state.history
facilities = state.facilities
facilities_avl = state.facilities_avl
road_graph = state.road_graph

# UI state
current_view = "dashboard"
content_container = None

DEPOT_LAT = 25.2048
DEPOT_LON = 55.2708

def get_distance_to_depot(lat, lon):
    return routing.calculate_distance(lat, lon, DEPOT_LAT, DEPOT_LON) * 111  # approx km

# ---------- Navigation ----------
def navigate_to(view_name):
    global current_view
    current_view = view_name
    refresh_ui()

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

def refresh_ui():
    """Clear and re-render the content container."""
    global content_container
    refresh_sidebar()
    
    if content_container:
        content_container.clear()
        with content_container:
            if current_view == "dashboard":
                dashboard.render_dashboard(
                    bins, history, requests, 
                    actions.collect_urgent_action, actions.dispatch_bin_logic, 
                    actions.save_all, refresh_ui
                )
            elif current_view == "bins":
                bins_view.render_bin_registry(
                    bins, 
                    dialogs.open_add_bin_dialog, 
                    dialogs.open_update_fill_dialog, 
                    actions.dispatch_bin_logic,
                    actions.simulate_updates_action,
                    actions.collect_all_bins_action
                )
            elif current_view == "requests":
                requests_view.render_requests(
                    actions.process_request_action,
                    lambda bid: requests_view.process_specific_request(bid, actions.save_all, actions.dispatch_bin_logic, refresh_ui),
                    lambda bid: requests_view.reject_specific_request(bid, actions.save_all, refresh_ui)
                )
            elif current_view == "history":
                history_view.render_history(history, get_distance_to_depot)
            elif current_view == "dispatch":
                dispatch_view.render_dispatch(bins, facilities, road_graph)
            elif current_view == "facilities":
                facilities_view.render_facility_report(facilities, facilities_avl, bins, history)
            elif current_view == "predictions":
                predictions_view.render_predictions(bins, history)

# ---------- Main UI ----------
ui.colors(primary='#10b981', secondary='#3B82F6', accent='#EF4444')

# Sidebar
with ui.left_drawer(value=True).classes("w-64 pt-6 bg-gray-70"):
    with ui.column().classes("p-6 gap-3 w-full"):
        ui.label("GreenBin").classes("text-4xl font-bold w-full text-center")
        ui.label("Smart Waste Collection").classes("text-xs text-gray-500 mb-4 w-full text-center")
        
        sidebar_nav_container = ui.column().classes("w-full gap-3")

# Main content area
with ui.column().classes("p-8 gap-6 w-full"):
    # Header
    with ui.row().classes("items-center justify-between w-full"):
        with ui.row().classes("items-center gap-4"):
            ui.icon("recycling").classes("text-3xl text-green-600")
            ui.label("Waste Management Console").classes("text-2xl font-bold text-gray-800")
        
        with ui.row().classes("items-center gap-3"):
            ui.button("Undo", on_click=actions.undo_last_action, icon="rotate_left").classes("bg-gray-200 text-gray-800 hover:bg-gray-300")
            ui.button("New Request", on_click=dialogs.open_request_dialog).classes("bg-orange-500 text-white shadow-md")
    
    # Content container
    content_container = ui.column().classes("w-full")

# Set the refresh callback for actions
actions.set_refresh_ui_callback(refresh_ui)

# Initial render
refresh_ui()

ui.run(title="GreenBin Dashboard", port=8085)
