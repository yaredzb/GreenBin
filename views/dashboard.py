"""Dashboard view for GreenBin application."""
from nicegui import ui
import pandas as pd
from .components import create_stat_card
from .components import create_stat_card


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
            
            ui.echart({
                "tooltip": {
                    "trigger": "item",
                    "formatter": "{b}: {c} bins ({d}%)",
                    "backgroundColor": "rgba(255, 255, 255, 0.95)",
                    "borderColor": "#e5e7eb",
                    "borderWidth": 1,
                    "textStyle": {"color": "#374151", "fontSize": 13}
                },
                "legend": {
                    "orient": "horizontal",
                    "bottom": "0%",
                    "left": "center",
                    "itemGap": 20,
                    "itemWidth": 14,
                    "itemHeight": 14,
                    "textStyle": {"fontSize": 13, "color": "#4b5563", "fontWeight": 500}
                },
                "series": [{
                    "name": "Bin Status",
                    "type": "pie",
                    "radius": ["45%", "75%"],
                    "center": ["50%", "45%"],
                    "avoidLabelOverlap": True,
                    "itemStyle": {
                        "borderRadius": 8,
                        "borderColor": "#fff",
                        "borderWidth": 3,
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.1)"
                    },
                    "label": {
                        "show": True,
                        "position": "outside",
                        "formatter": "{d}%",
                        "fontSize": 13,
                        "fontWeight": "600",
                        "color": "#374151"
                    },
                    "labelLine": {
                        "show": True,
                        "length": 15,
                        "length2": 10,
                        "smooth": True
                    },
                    "emphasis": {
                        "label": {
                            "show": True,
                            "fontSize": 16,
                            "fontWeight": "bold"
                        },
                        "itemStyle": {
                            "shadowBlur": 20,
                            "shadowColor": "rgba(0, 0, 0, 0.2)"
                        },
                        "scale": True,
                        "scaleSize": 8
                    },
                    "data": [
                        {"value": status_counts["Critical"], "name": "Critical", "itemStyle": {"color": "#DC2626"}},
                        {"value": status_counts["High"], "name": "High", "itemStyle": {"color": "#EA580C"}},
                        {"value": status_counts["Medium"], "name": "Medium", "itemStyle": {"color": "#CA8A04"}},
                        {"value": status_counts["Low"], "name": "Low", "itemStyle": {"color": "#16A34A"}},
                        {"value": status_counts["Empty"], "name": "Empty", "itemStyle": {"color": "#6B7280"}}
                    ]
                }]
            }).classes("h-80")

        # Waste Type Bar Chart
        type_counts = {}
        for b in bins:
            type_counts[b.waste_type] = type_counts.get(b.waste_type, 0) + 1

        total_waste_bins = sum(type_counts.values())

        # Define color palette for different waste types
        waste_colors = {
            "Household": "#6366F1",   # Indigo
            "Industrial": "#64748B",  # Slate
            "Recyclable": "#10B981",  # Emerald
            "Organic": "#84CC16",     # Lime
        }

        # Assign colors based on waste type or use default gradient
        bar_colors = [waste_colors.get(wtype, "#3B82F6") for wtype in type_counts.keys()]

        with ui.card().classes("flex-1 p-6 shadow-lg rounded-lg bg-white"):
            # Header with total count
            with ui.row().classes("w-full justify-between items-center mb-4"):
                ui.label("Waste Composition Analysis").classes("text-xl font-bold text-gray-800")
                ui.label(f"{len(type_counts)} types").classes("text-sm font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full")
            
            ui.echart({
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {
                        "type": "shadow",
                        "shadowStyle": {
                            "color": "rgba(0, 0, 0, 0.05)"
                        }
                    },
                    "formatter": "{b}: {c} bins",
                    "backgroundColor": "rgba(255, 255, 255, 0.95)",
                    "borderColor": "#e5e7eb",
                    "borderWidth": 1,
                    "textStyle": {"color": "#374151", "fontSize": 13},
                    "padding": [10, 15]
                },
                "grid": {
                    "left": "3%",
                    "right": "4%",
                    "bottom": "10%",
                    "top": "5%",
                    "containLabel": True
                },
                "xAxis": [{
                    "type": "category",
                    "data": list(type_counts.keys()),
                    "axisTick": {
                        "alignWithLabel": True,
                        "lineStyle": {"color": "#e5e7eb"}
                    },
                    "axisLine": {
                        "lineStyle": {"color": "#e5e7eb", "width": 2}
                    },
                    "axisLabel": {
                        "color": "#6b7280",
                        "fontSize": 12,
                        "fontWeight": 500,
                        "rotate": 45 if len(type_counts) > 6 else 0,
                        "interval": 0
                    }
                }],
                "yAxis": [{
                    "type": "value",
                    "name": "Number of Bins",
                    "nameTextStyle": {
                        "color": "#6b7280",
                        "fontSize": 12,
                        "fontWeight": 500,
                        "padding": [0, 0, 10, 0]
                    },
                    "axisLine": {
                        "show": True,
                        "lineStyle": {"color": "#e5e7eb", "width": 2}
                    },
                    "axisTick": {
                        "show": True,
                        "lineStyle": {"color": "#e5e7eb"}
                    },
                    "axisLabel": {
                        "color": "#6b7280",
                        "fontSize": 12
                    },
                    "splitLine": {
                        "lineStyle": {
                            "color": "#f3f4f6",
                            "type": "dashed"
                        }
                    }
                }],
                "series": [{
                    "name": "Bin Count",
                    "type": "bar",
                    "barWidth": "50%",
                    "data": [
                        {
                            "value": count,
                            "itemStyle": {
                                "color": bar_colors[i],
                                "borderRadius": [6, 6, 0, 0],
                                "shadowBlur": 10,
                                "shadowColor": "rgba(0, 0, 0, 0.1)",
                                "shadowOffsetY": 2
                            }
                        } for i, count in enumerate(type_counts.values())
                    ],
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 20,
                            "shadowColor": "rgba(0, 0, 0, 0.2)",
                            "brightness": 1.1
                        },
                        "label": {
                            "show": True,
                            "position": "top",
                            "formatter": "{c}",
                            "fontSize": 14,
                            "fontWeight": "bold",
                            "color": "#374151"
                        }
                    },
                    "animationDuration": 1000,
                    "animationEasing": "elasticOut"
                }]
            }).classes("h-80")

    # Main content split
    with ui.row().classes("w-full gap-6 items-start"):
        # Left: urgent table
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
            
            columns = [
                {"name":"id","label":"Bin","field":"id"},
                {"name":"type","label":"Type","field":"waste_type"},
                {"name":"fill","label":"Fill %","field":"fill_level"},
                {"name":"status","label":"Status","field":"status"},
                {"name":"actions","label":"Actions","field":"actions"}
            ]
            rows = df_urgent.to_dict('records') if urgent_bins else []
            if urgent_bins:
                with ui.table(columns=columns, rows=rows, pagination=10).classes("w-full shadow-md").props('bordered flat separator="cell" rows-per-page-options="[10,20]"') as table:
                    table.add_slot('body-cell-actions', r'''
                        <q-td :props="props">
                            <q-btn size="sm" color="red" label="Dispatch" @click="$parent.$emit('dispatch', props.row)" />
                        </q-td>
                    ''')
                    table.on('dispatch', lambda e: dispatch_bin_logic(e.args['id']))
            else:
                ui.label("No critical bins at the moment").classes("p-4 text-gray-500")

        # Right Panel: Recent History
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

                        # Right side (Undo button)
                        ui.button(
                            "Undo",
                            on_click=lambda e=entry: undo_specific_history(e, bins, history, save_all, refresh_ui),
                        ).props("flat color=red size=sm")
            else:
                ui.label("No recent collections").classes("text-sm text-gray-500")
