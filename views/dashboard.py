"""Dashboard view for GreenBin application."""
from nicegui import ui
import pandas as pd
from .components import create_stat_card
from .charts import get_bin_status_chart_options, get_waste_composition_chart_options


def get_stats(bins, history, requests):
    """Calculate dashboard statistics."""
    total_collections = len([h for h in history if h.get('status') == 'Collected'])
    co2_saved = total_collections * 2.5
    urgent_count = len([b for b in bins if b.fill_level >= 80])
    pending_count = len(requests)
    return total_collections, co2_saved, urgent_count, pending_count


def undo_specific_history(entry, bins, history, save_all, refresh_ui):
    """Undo a specific history record."""
    b = next((x for x in bins if x.id == entry["bin_id"]), None)
    if b and "prev_fill" in entry:
        b.fill_level = entry["prev_fill"]
    # remove entry from history
    for i in range(len(history)-1, -1, -1):
        if history[i]["timestamp"] == entry["timestamp"] and history[i]["bin_id"] == entry["bin_id"]:
            history.pop(i)
            break
    save_all()
    ui.notify("Undid collection", color="info")
    refresh_ui()


from .tables import DASHBOARD_URGENT_COLUMNS, DASHBOARD_URGENT_ACTIONS_SLOT

def render_urgent_bins_table(bins, collect_urgent_action, dispatch_bin_logic):
    """Render the table of urgent bins."""
    with ui.card().classes("flex-1 p-0 shadow-sm"):
        with ui.row().classes("p-4 border-b w-full items-center"):
            ui.label("Critical / Urgent Bins").classes("text-lg font-semibold")
            ui.button("Collect All", on_click=collect_urgent_action).classes("ml-auto bg-red-500 text-white")
        urgent_bins = [b for b in bins if b.fill_level >= 80]
        
        # Create DataFrame for urgent bins
        if urgent_bins:
            df_urgent = pd.DataFrame([
                {"id": b.id, "waste_type": b.waste_type, "fill_level": b.fill_level, "status": "CRITICAL"}
                for b in urgent_bins
            ])
            df_urgent['fill_level'] = df_urgent['fill_level'].astype(str) + '%'
        
        rows = df_urgent.to_dict('records') if urgent_bins else []
        if urgent_bins:
            with ui.table(columns=DASHBOARD_URGENT_COLUMNS, rows=rows, pagination=10).classes("w-full shadow-md").props('bordered flat separator="cell" rows-per-page-options="[10,20]"') as table:
                table.add_slot('body-cell-actions', DASHBOARD_URGENT_ACTIONS_SLOT)
                table.on('dispatch', lambda e: dispatch_bin_logic(e.args['id']))
        else:
            ui.label("No critical bins at the moment").classes("p-4 text-gray-500")


def render_recent_collections(history):
    """Render the list of recent collections."""
    with ui.card().classes("w-1/3 p-4 shadow-md rounded-xl"):
        ui.label("Recent Collections").classes("text-lg font-semibold mb-3")

        if history:
            for entry in history[-5:][::-1]:
                with ui.row().classes(
                    "w-full items-center justify-between p-3 border rounded-lg mb-2 recent-collection-card"
                ):
                    # Left side (bin + timestamp)
                    with ui.column().classes("gap-1"):
                        ui.label(f"🗑️ {entry['bin_id']} — {entry['type']}").classes(
                            "font-semibold text-sm"
                        )
                        ui.label(entry["timestamp"]).classes(
                            "text-xs text-gray-500"
                        )
        else:
            ui.label("No recent collections").classes("text-sm text-gray-500")


def render_dashboard(bins, history, requests, collect_urgent_action, dispatch_bin_logic, save_all, refresh_ui):
    """Render the dashboard view."""
    tc, co2, uc, pc = get_stats(bins, history, requests)

    # Header
    with ui.row().classes("w-full justify-between items-center mb-4"):
        ui.label("Dashboard Overview").classes("text-2xl font-bold text-gray-800")

    # Stats row
    with ui.row().classes("w-full gap-6 mb-6"):
        create_stat_card("Total Collections", str(tc), "Collections completed", border_color="#3B82F6")
        create_stat_card("CO₂ Saved (kg)", f"{co2:.1f}", "Estimated", border_color="#10B981")
        create_stat_card("Urgent Bins", str(uc), "≥80% full", border_color="#EF4444")
        create_stat_card("Pending Requests", str(pc), "Awaiting processing", border_color="#8B5CF6")

    # Visualizations
    with ui.row().classes("w-full gap-6 mb-6"):
        # Bin Status Pie Chart
        status_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Empty": 0}
        for b in bins:
            if b.fill_level >= 80: 
                status_counts["Critical"] += 1
            elif b.fill_level >= 50: 
                status_counts["High"] += 1
            elif b.fill_level >= 25: 
                status_counts["Medium"] += 1
            elif b.fill_level > 0: 
                status_counts["Low"] += 1
            else: 
                status_counts["Empty"] += 1

        total_bins = sum(status_counts.values())

        with ui.card().classes("flex-1 p-6 shadow-lg rounded-lg bg-white"):
            # Header with total count
            with ui.row().classes("w-full justify-between items-center mb-4"):
                ui.label("Bin Status Distribution").classes("text-xl font-bold text-gray-800")
                ui.label(f"Total: {total_bins} bins").classes("text-sm font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full")
            
            ui.echart(get_bin_status_chart_options(bins)).classes("h-80")

        # Waste Type Bar Chart
        type_counts = {}
        for b in bins:
            type_counts[b.waste_type] = type_counts.get(b.waste_type, 0) + 1

        with ui.card().classes("flex-1 p-6 shadow-lg rounded-lg bg-white"):
            # Header with total count
            with ui.row().classes("w-full justify-between items-center mb-4"):
                ui.label("Waste Composition Analysis").classes("text-xl font-bold text-gray-800")
                ui.label(f"{len(type_counts)} types").classes("text-sm font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full")
            
            ui.echart(get_waste_composition_chart_options(bins)).classes("h-80")

    # Main content split
    with ui.row().classes("w-full gap-6 items-start"):
        # Left: urgent table
        render_urgent_bins_table(bins, collect_urgent_action, dispatch_bin_logic)

        # Right Panel: Recent History
        render_recent_collections(history)
