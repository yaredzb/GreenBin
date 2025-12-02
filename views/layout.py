"""Layout components for GreenBin application."""
from nicegui import ui
import actions
from . import dialogs

def status_badge(fill_level):
    # 0% - empty, 1-25% low load, 25-50% -medium load, 50-75% - high load, 85% -100 critical
    if fill_level >= 85:
        return ui.label("CRITICAL").classes("px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-bold")
    if fill_level >= 50:
        return ui.label("HIGH LOAD").classes("px-2 py-1 bg-orange-100 text-orange-700 rounded-full text-xs")
    if fill_level >= 25:
        return ui.label("MEDIUM").classes("px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs")
    if fill_level > 0:
        return ui.label("LOW").classes("px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs")
    return ui.label("EMPTY").classes("px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs")

def render_sidebar(current_view, navigate_fn):
    """Render the sidebar navigation."""
    with ui.left_drawer(value=True).classes("w-64 pt-6 bg-gray-70"):
        with ui.column().classes("p-6 gap-3 w-full"):
            ui.label("GreenBin").classes("text-4xl font-bold w-full text-center")
            ui.label("Smart Waste Collection").classes("text-xs text-gray-500 mb-4 w-full text-center")
            
            with ui.column().classes("w-full gap-3"):
                def nav_btn(label, icon, view):
                    def on_click():
                        navigate_fn(view)
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
                # nav_btn("Predictions", "trending_up", "predictions")

def render_header():
    """Render the application header."""
    with ui.row().classes("items-center justify-between w-full"):
        with ui.row().classes("items-center gap-4"):
            ui.icon("recycling").classes("text-3xl text-green-600")
            ui.label("Waste Management Console").classes("text-2xl font-bold text-gray-800")
        
        with ui.row().classes("items-center gap-3"):
            ui.button("Undo", on_click=actions.undo_last_action, icon="rotate_left").classes("bg-gray-200 text-gray-800 hover:bg-gray-300")
            ui.button("New Request", on_click=dialogs.open_request_dialog).classes("bg-orange-500 text-white shadow-md")
