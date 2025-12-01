"""History view for GreenBin application."""
from nicegui import ui
import pandas as pd
from algorithms.searching import search_by_substring
from algorithms.sorting import merge_sort


def create_history_filters(sort_options=None):
    """Create filter inputs for history views."""
    if sort_options is None:
        sort_options = ["Recent First", "Bin ID"]
    
    with ui.row().classes("w-full gap-4 mb-4"):
        search = ui.input(placeholder="Search Bin ID...").classes("flex-1").props("outlined dense")
        area = ui.input(placeholder="Filter Area (lat,lon)...").classes("flex-1").props("outlined dense")
        type_filter = ui.select(["All", "Household", "Industrial", "Recyclable", "Organic"], 
                                value="All", label="Waste Type").classes("w-48").props("outlined dense")
        sort_by = ui.select(sort_options, value=sort_options[0], 
                           label="Sort By").classes("w-48").props("outlined dense")
    return search, area, type_filter, sort_by


def render_history(history, get_distance_to_depot_fn):
    """Render the history view."""
    ui.label("Collection History").classes("text-2xl font-bold mb-4")
    
    # Metrics container (above tabs)
    d_metrics = ui.row().classes("w-full gap-4 mb-4")

    # Create tabs for different history types
    with ui.tabs().classes("w-full").props("align=justify") as tabs:
        tab_dispatch = ui.tab("Dispatch History")
        tab_update = ui.tab("Update Bin History")
        tab_request = ui.tab("Request History")
    
    with ui.tab_panels(tabs, value=tab_dispatch).classes("w-full bg-transparent"):
        # Dispatch History Tab
        with ui.tab_panel(tab_dispatch).classes("p-0"):
            with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white"):
                d_search, d_area, d_type, d_sort = create_history_filters(
                    sort_options=["Recent First", "Bin ID", "Distance", "CO2 Saved"]
                )
                
                d_table = ui.column().classes("w-full")
            
            def refresh_dispatch_history():
                d_table.clear()
                d_metrics.clear()
                
                query = d_search.value.strip()
                area_query = d_area.value.strip()
                type_filter = d_type.value
                sort_by = d_sort.value
                
                # Filter only dispatched items from history
                dispatch_history = [h for h in history if h.get('status') == 'Collected']

                # Filter by Type
                if type_filter != "All":
                    dispatch_history = [h for h in dispatch_history if h.get('type') == type_filter]

                # Filter by Area
                if area_query:
                    dispatch_history = search_by_substring(dispatch_history, lambda h: h.get("area", ""), area_query)
                
                # Enrich with distance and CO2
                enriched = []
                for h in dispatch_history:
                    dist = 0.0
                    if "area" in h:
                        try:
                            lat_str, lon_str = h["area"].split(",")
                            dist = get_distance_to_depot_fn(float(lat_str), float(lon_str))
                        except:
                            dist = 0.0
                    enriched.append({**h, "distance": dist, "co2": 2.5})
                
                # Search using DSA
                if query:
                    enriched = search_by_substring(enriched, lambda h: h.get("bin_id", ""), query)
                
                # Sort using merge_sort
                if sort_by == "Recent First":
                    enriched.reverse()
                elif sort_by == "Bin ID":
                    enriched = merge_sort(enriched, key=lambda h: h["bin_id"])
                elif sort_by == "Distance":
                    enriched = merge_sort(enriched, key=lambda h: h["distance"])
                    enriched.reverse()
                elif sort_by == "CO2 Saved":
                    enriched = merge_sort(enriched, key=lambda h: h["co2"])
                    enriched.reverse()
                
                # Metrics
                total = len(enriched)
                total_dist = sum(h["distance"] for h in enriched)
                total_co2 = sum(h["co2"] for h in enriched)
                
                with d_metrics:
                    with ui.card().classes("flex-1 p-3 bg-blue-50"):
                        ui.label("Total Dispatches").classes("text-xs text-gray-500")
                        ui.label(str(total)).classes("text-xl font-bold")
                    with ui.card().classes("flex-1 p-3 bg-green-50"):
                        ui.label("Total Distance").classes("text-xs text-gray-500")
                        ui.label(f"{total_dist:.2f} km").classes("text-xl font-bold")
                    with ui.card().classes("flex-1 p-3 bg-teal-50"):
                        ui.label("CO2 Saved").classes("text-xs text-gray-500")
                        ui.label(f"{total_co2:.2f} kg").classes("text-xl font-bold")
                
                # Format for display
                df = pd.DataFrame(enriched) if enriched else pd.DataFrame()
                if not df.empty:
                    df['distance'] = df['distance'].apply(lambda x: f"{x:.2f}")
                    df['co2'] = df['co2'].apply(lambda x: f"{x:.2f}")
                    rows = df.to_dict('records')
                else:
                    rows = []
                
                with d_table:
                    ui.table(
                        columns=[
                            {"name":"bin_id","label":"Bin ID","field":"bin_id", "align": "left"},
                            {"name":"type","label":"Type","field":"type", "align": "left"},
                            {"name":"dist","label":"Distance (km)","field":"distance", "align": "left"},
                            {"name":"co2","label":"CO2 (kg)","field":"co2", "align": "left"},
                            {"name":"time","label":"Time","field":"timestamp", "align": "left"},
                        ],
                        rows=rows,
                        pagination=10
                    ).classes("w-full").props('flat bordered dense separator="cell"')

            d_search.on_value_change(refresh_dispatch_history)
            d_area.on_value_change(refresh_dispatch_history)
            d_type.on_value_change(refresh_dispatch_history)
            d_sort.on_value_change(refresh_dispatch_history)
            refresh_dispatch_history()

        # Update Bin History Tab
        with ui.tab_panel(tab_update).classes("p-0"):
            with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white"):
                u_search, u_area, u_type, u_sort = create_history_filters()
                u_table = ui.column().classes("w-full")
            
            def refresh_update_history():
                u_table.clear()
                query = u_search.value.strip()
                type_filter = u_type.value
                sort_by = u_sort.value
                
                # Filter updates
                updates = [h for h in history if h.get('status') in ['Updated', 'IoT Update']]
                
                if type_filter != "All":
                    updates = [h for h in updates if h.get('type') == type_filter]
                
                if query:
                    updates = search_by_substring(updates, lambda h: h.get("bin_id", ""), query)
                    
                if sort_by == "Recent First":
                    updates.reverse()
                elif sort_by == "Bin ID":
                    updates = merge_sort(updates, key=lambda h: h["bin_id"])
                
                df = pd.DataFrame(updates) if updates else pd.DataFrame()
                rows = df.to_dict('records') if not df.empty else []
                
                with u_table:
                    ui.table(
                        columns=[
                            {"name":"bin_id","label":"Bin ID","field":"bin_id", "align": "left"},
                            {"name":"type","label":"Type","field":"type,", "align": "left"},
                            {"name":"prev","label":"Prev Fill","field":"prev_fill", "align": "left"},
                            {"name":"new","label":"New Fill","field":"new_fill", "align": "left"},
                            {"name":"time","label":"Time","field":"timestamp", "align": "left"},
                        ],
                        rows=rows,
                        pagination=10
                    ).classes("w-full").props('flat bordered dense separator="cell"')

            u_search.on_value_change(refresh_update_history)
            u_type.on_value_change(refresh_update_history)
            u_sort.on_value_change(refresh_update_history)
            refresh_update_history()

        # Request History Tab
        with ui.tab_panel(tab_request).classes("p-0"):
            with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white"):
                r_search, r_area, r_type, r_sort = create_history_filters()
                r_table = ui.column().classes("w-full")
            
            def refresh_request_history():
                r_table.clear()
                query = r_search.value.strip()
                type_filter = r_type.value
                sort_by = r_sort.value
                
                # Filter requests
                req_history = [h for h in history if h.get('status') == 'Request Processed']
                
                if type_filter != "All":
                    req_history = [h for h in req_history if h.get('type') == type_filter]
                
                if query:
                    req_history = search_by_substring(req_history, lambda h: h.get("bin_id", ""), query)
                    
                if sort_by == "Recent First":
                    req_history.reverse()
                elif sort_by == "Bin ID":
                    req_history = merge_sort(req_history, key=lambda h: h["bin_id"])
                
                df = pd.DataFrame(req_history) if req_history else pd.DataFrame()
                rows = df.to_dict('records') if not df.empty else []
                
                with r_table:
                    ui.table(
                        columns=[
                            {"name":"bin_id","label":"Bin ID","field":"bin_id", "align": "left"},
                            {"name":"type","label":"Type","field":"type", "align": "left"},
                            {"name":"action","label":"Action","field":"action", "align": "left"},
                            {"name":"time","label":"Time","field":"timestamp", "align": "left"},
                        ],
                        rows=rows,
                        pagination=10
                    ).classes("w-full").props('flat bordered dense separator="cell"')

            r_search.on_value_change(refresh_request_history)
            r_type.on_value_change(refresh_request_history)
            r_sort.on_value_change(refresh_request_history)
            refresh_request_history()
