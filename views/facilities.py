"""Facilities view for GreenBin application."""
from nicegui import ui
import pandas as pd
from algorithms.sorting import merge_sort
from views.components import create_stat_card
import services.report_generator as report_gen
from .charts import get_capacity_efficiency_scatter_options
from .tables import FACILITIES_COLUMNS, FACILITIES_EFFICIENCY_SLOT

def render_facility_report(facilities, facilities_avl, bins, history):
    """Render the facility performance report."""
    with ui.row().classes("w-full justify-between items-center mb-6"):
        ui.label("Facility Performance Report").classes("text-2xl font-bold")
        ui.button("Download Report", icon="download", on_click=lambda: ui.download(report_gen.generate_professional_report(bins, history, facilities))).classes("bg-blue-600 text-white")
    
    if not facilities:
        with ui.card().classes("w-full p-8 text-center shadow-sm"):
            ui.label("No facilities found").classes("text-lg text-gray-500")
        return

    # Calculate stats
    total = len(facilities)
    avg_eff = sum(f.efficiency for f in facilities) / total if total else 0
    top_f = max(facilities, key=lambda x: x.efficiency) if facilities else None
    
    # Stats cards
    with ui.row().classes("w-full gap-4 mb-6"):
        create_stat_card("Total Facilities", str(total), "Active processing sites", border_color="#3B82F6")
        create_stat_card("Average Efficiency", f"{avg_eff:.1f}%", "Fleet performance", border_color="#10B981")
        if top_f:
            create_stat_card("Top Performer", top_f.id, f"{top_f.efficiency}% efficiency", border_color="#F59E0B")


    # Render Charts
    with ui.row().classes("w-full mb-6"):
        with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white h-full"):
            with ui.row().classes("w-full justify-between items-center mb-4"):
                ui.label("Capacity vs Efficiency Analysis").classes("text-xl font-bold text-gray-800")
            
            ui.echart(get_capacity_efficiency_scatter_options(facilities)).classes("h-64")

    # Data table section
    with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white"):
        ui.label("Facility Details").classes("text-xl font-bold text-gray-800 mb-4")
        
        # Filters
        with ui.row().classes("w-full gap-4 mb-4"):
            search_input = ui.input(placeholder="Search by Facility ID...").classes("flex-1").props("outlined dense")
            eff_filter = ui.select(
                ["All", "High (>90%)", "Medium (70-90%)", "Low (<70%)"], 
                value="All", 
                label="Filter by Efficiency"
            ).classes("w-56").props("outlined dense")

        table_container = ui.column().classes("w-full")

        def refresh_table():
            table_container.clear()
            query = search_input.value.strip()
            eff_val = eff_filter.value
            
            # Filter by efficiency
            filtered_facs = facilities[:]
            if eff_val == "High (>90%)":
                filtered_facs = [f for f in filtered_facs if f.efficiency > 90]
            elif eff_val == "Medium (70-90%)":
                filtered_facs = [f for f in filtered_facs if 70 <= f.efficiency <= 90]
            elif eff_val == "Low (<70%)":
                filtered_facs = [f for f in filtered_facs if f.efficiency < 70]

            # Search by ID
            if query:
                found = facilities_avl.get(query)
                if found and found in filtered_facs:
                    df_facilities = pd.DataFrame([{
                        "id": found.id, 
                        "loc": f"{found.lat:.4f}, {found.lon:.4f}", 
                        "cap": found.capacity,
                        "eff_val": found.efficiency
                    }])
                else:
                    df_facilities = pd.DataFrame()
            else:
                sorted_facs = merge_sort(filtered_facs, key=lambda x: x.efficiency)
                sorted_facs.reverse()
                
                df_facilities = pd.DataFrame([{
                    "id": f.id, 
                    "loc": f"{f.lat:.4f}, {f.lon:.4f}",
                    "cap": f.capacity,
                    "eff_val": f.efficiency
                } for f in sorted_facs])
            
            rows = df_facilities.to_dict('records') if not df_facilities.empty else []

            with table_container:
                if rows:
                    ui.table(
                        columns=FACILITIES_COLUMNS,
                        rows=rows,
                        pagination=10
                    ).classes("w-full").props('flat bordered dense separator="cell"').add_slot('body-cell-eff', FACILITIES_EFFICIENCY_SLOT)
                else:
                    ui.label("No facilities match your criteria").classes("text-gray-500 text-center py-8")

        search_input.on_value_change(lambda: refresh_table())
        eff_filter.on_value_change(lambda: refresh_table())
        
        refresh_table()
