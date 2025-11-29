"""Facilities view for GreenBin application."""
from nicegui import ui
import pandas as pd
from algorithms.sorting import merge_sort
from views.components import create_stat_card
from views.components import create_stat_card
import services.report_generator as report_gen

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

    # Efficiency bar chart
    sorted_facilities = sorted(facilities, key=lambda f: f.efficiency, reverse=True)
    
    with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white mb-6"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("Efficiency Comparison").classes("text-xl font-bold text-gray-800")
            ui.label(f"{len(facilities)} facilities").classes("text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full")
        
        bar_colors = []
        for f in sorted_facilities:
            if f.efficiency > 90:
                bar_colors.append("#10B981")
            elif f.efficiency >= 70:
                bar_colors.append("#F59E0B")
            else:
                bar_colors.append("#EF4444")
        
        ui.echart({
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow", "shadowStyle": {"color": "rgba(0, 0, 0, 0.05)"}},
                "formatter": "{b}: {c}%",
                "backgroundColor": "rgba(255, 255, 255, 0.95)",
                "borderColor": "#e5e7eb",
                "borderWidth": 1,
                "textStyle": {"color": "#374151", "fontSize": 13},
                "padding": [10, 15]
            },
            "grid": {
                "left": "12%",
                "right": "8%",
                "bottom": "5%",
                "top": "3%",
                "containLabel": True
            },
            "xAxis": {
                "type": "value",
                "max": 100,
                "axisLabel": {
                    "formatter": "{value}%",
                    "color": "#6b7280",
                    "fontSize": 12
                },
                "axisLine": {"lineStyle": {"color": "#e5e7eb", "width": 2}},
                "splitLine": {"lineStyle": {"color": "#f3f4f6", "type": "dashed"}}
            },
            "yAxis": {
                "type": "category",
                "data": [f.id for f in sorted_facilities],
                "axisLabel": {
                    "color": "#374151",
                    "fontSize": 12,
                    "fontWeight": 500
                },
                "axisLine": {"lineStyle": {"color": "#e5e7eb", "width": 2}},
                "axisTick": {"show": False}
            },
            "series": [{
                "name": "Efficiency",
                "type": "bar",
                "barWidth": "60%",
                "data": [
                    {
                        "value": f.efficiency,
                        "itemStyle": {
                            "color": bar_colors[i],
                            "borderRadius": [0, 6, 6, 0],
                            "shadowBlur": 8,
                            "shadowColor": "rgba(0, 0, 0, 0.1)",
                            "shadowOffsetX": 2
                        }
                    } for i, f in enumerate(sorted_facilities)
                ],
                "label": {
                    "show": True,
                    "position": "right",
                    "formatter": "{c}%",
                    "fontSize": 12,
                    "fontWeight": "600",
                    "color": "#374151"
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 15,
                        "shadowColor": "rgba(0, 0, 0, 0.2)"
                    }
                }
            }]
        }).classes("h-64" if len(facilities) <= 5 else "h-96")

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
                        columns=[
                            {"name": "id", "label": "Facility ID", "field": "id", "align": "left", "sortable": True},
                            {"name": "loc", "label": "Location", "field": "loc", "align": "left"},
                            {"name": "cap", "label": "Capacity", "field": "cap", "align": "center", "sortable": True},
                            {"name": "eff", "label": "Efficiency", "field": "eff_val", "align": "left", "sortable": True}
                        ],
                        rows=rows,
                        pagination=10
                    ).classes("w-full").props('flat bordered dense separator="cell"').add_slot('body-cell-eff', r'''
                        <q-td :props="props">
                            <div class="flex items-center gap-2">
                                <q-linear-progress 
                                    :value="props.value / 100" 
                                    :color="props.value > 90 ? 'green' : props.value >= 70 ? 'orange' : 'red'"
                                    track-color="grey-3" 
                                    class="w-32" 
                                    size="8px"
                                    rounded
                                />
                                <span class="text-sm font-semibold">{{ props.value }}%</span>
                            </div>
                        </q-td>
                    ''')
                else:
                    ui.label("No facilities match your criteria").classes("text-gray-500 text-center py-8")

        search_input.on_value_change(lambda: refresh_table())
        eff_filter.on_value_change(lambda: refresh_table())
        
        refresh_table()
