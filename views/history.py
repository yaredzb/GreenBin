"""History view for GreenBin application."""
from nicegui import ui
import pandas as pd
from algorithms.searching import search_by_substring
from algorithms.sorting import merge_sort
from .tables import HISTORY_DISPATCH_COLUMNS, HISTORY_UPDATE_COLUMNS, HISTORY_REQUEST_COLUMNS


# Create filter inputs for history views
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


# Generic function to render a history tab with filtering and sorting
def render_history_tab(
    history,
    columns,
    filter_status,
    sort_options,
    enrich_fn=None,
    metrics_container=None,
    metrics_fn=None
):
    """
    Generic function to render a history tab.
    
    Args:
        history: Full history data
        columns: Table column definitions
        filter_status: Status value(s) to filter by (string or list)
        sort_options: List of sort options for dropdown
        enrich_fn: Optional function to enrich data (e.g., add distance/CO2)
        metrics_container: Optional container for metrics display
        metrics_fn: Optional function to calculate and display metrics
    """
    with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white"):
        # Create filters
        search, area, type_filter, sort_by = create_history_filters(sort_options)
        
        # Table container
        table_container = ui.column().classes("w-full")
        
        def refresh_table():
            table_container.clear()
            if metrics_container:
                metrics_container.clear()
            
            query = search.value.strip()
            area_query = area.value.strip()
            type_val = type_filter.value
            sort_val = sort_by.value
            
            # Filter by status
            if isinstance(filter_status, list):
                filtered = [h for h in history if h.get('status') in filter_status]
            else:
                filtered = [h for h in history if h.get('status') == filter_status]
            
            # Filter by type
            if type_val != "All":
                filtered = [h for h in filtered if h.get('type') == type_val]
            
            # Filter by area
            if area_query:
                filtered = search_by_substring(filtered, lambda h: h.get("area", ""), area_query)
            
            # Enrich data if function provided
            if enrich_fn:
                filtered = enrich_fn(filtered)
            
            # Search by bin ID
            if query:
                filtered = search_by_substring(filtered, lambda h: h.get("bin_id", ""), query)
            
            # Sort data
            if sort_val == "Recent First":
                filtered.reverse()
            elif sort_val == "Bin ID":
                filtered = merge_sort(filtered, key=lambda h: h.get("bin_id", ""))
            elif sort_val == "Distance":
                filtered = merge_sort(filtered, key=lambda h: h.get("distance", 0))
                filtered.reverse()
            elif sort_val == "CO2 Saved":
                filtered = merge_sort(filtered, key=lambda h: h.get("co2", 0))
                filtered.reverse()
            
            # Display metrics if function provided
            if metrics_fn and metrics_container:
                metrics_fn(filtered, metrics_container)
            
            # Prepare table data
            df = pd.DataFrame(filtered) if filtered else pd.DataFrame()
            if not df.empty and enrich_fn:
                # Format numeric columns
                if 'distance' in df.columns:
                    df['distance'] = df['distance'].apply(lambda x: f"{x:.2f}")
                if 'co2' in df.columns:
                    df['co2'] = df['co2'].apply(lambda x: f"{x:.2f}")
            
            rows = df.to_dict('records') if not df.empty else []
            
            # Render table
            with table_container:
                ui.table(
                    columns=columns,
                    rows=rows,
                    pagination=10
                ).classes("w-full").props('flat bordered dense separator="cell"')
        
        # Attach event handlers
        search.on_value_change(refresh_table)
        area.on_value_change(refresh_table)
        type_filter.on_value_change(refresh_table)
        sort_by.on_value_change(refresh_table)
        
        # Initial render
        refresh_table()


# Main history view rendering function
def render_history(history, get_distance_to_depot_fn):
    """Render the history view."""
    ui.label("Collection History").classes("text-2xl font-bold mb-4")
    
    # Metrics container for dispatch tab
    dispatch_metrics = ui.row().classes("w-full gap-4 mb-4")

    # Create tabs
    with ui.tabs().classes("w-full").props("align=justify") as tabs:
        tab_dispatch = ui.tab("Dispatch History")
        tab_update = ui.tab("Update Bin History")
        tab_request = ui.tab("Request History")
    
    with ui.tab_panels(tabs, value=tab_dispatch).classes("w-full bg-transparent"):
        # Dispatch History Tab
        with ui.tab_panel(tab_dispatch).classes("p-0"):
            def enrich_dispatch(data):
                """Enrich dispatch data with distance and CO2."""
                enriched = []
                for h in data:
                    dist = 0.0
                    if "area" in h:
                        try:
                            lat_str, lon_str = h["area"].split(",")
                            dist = get_distance_to_depot_fn(float(lat_str), float(lon_str))
                        except:
                            dist = 0.0
                    enriched.append({**h, "distance": dist, "co2": 2.5})
                return enriched
            
            def display_dispatch_metrics(data, container):
                """Display metrics for dispatch history."""
                total = len(data)
                total_dist = sum(h.get("distance", 0) for h in data)
                total_co2 = sum(h.get("co2", 0) for h in data)
                
                with container:
                    with ui.card().classes("flex-1 p-3 bg-blue-50"):
                        ui.label("Total Dispatches").classes("text-xs text-gray-500")
                        ui.label(str(total)).classes("text-xl font-bold")
                    with ui.card().classes("flex-1 p-3 bg-green-50"):
                        ui.label("Total Distance").classes("text-xs text-gray-500")
                        ui.label(f"{total_dist:.2f} km").classes("text-xl font-bold")
                    with ui.card().classes("flex-1 p-3 bg-teal-50"):
                        ui.label("CO2 Saved").classes("text-xs text-gray-500")
                        ui.label(f"{total_co2:.2f} kg").classes("text-xl font-bold")
            
            render_history_tab(
                history=history,
                columns=HISTORY_DISPATCH_COLUMNS,
                filter_status="Collected",
                sort_options=["Recent First", "Bin ID", "Distance", "CO2 Saved"],
                enrich_fn=enrich_dispatch,
                metrics_container=dispatch_metrics,
                metrics_fn=display_dispatch_metrics
            )

        # Update Bin History Tab
        with ui.tab_panel(tab_update).classes("p-0"):
            render_history_tab(
                history=history,
                columns=HISTORY_UPDATE_COLUMNS,
                filter_status=["Updated", "IoT Update"],
                sort_options=["Recent First", "Bin ID"]
            )

        # Request History Tab
        with ui.tab_panel(tab_request).classes("p-0"):
            render_history_tab(
                history=history,
                columns=HISTORY_REQUEST_COLUMNS,
                filter_status="Request Processed",
                sort_options=["Recent First", "Bin ID"]
            )
