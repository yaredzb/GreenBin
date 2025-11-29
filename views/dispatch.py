"""Dispatch view for GreenBin application."""
from nicegui import ui
import routing

def render_dispatch(bins, facilities, road_graph):
    """Render the dispatch center view."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        ui.label("Plotly not installed").classes("text-red-500")
        return
    
    ui.label("Dispatch Center & Routing").classes("text-2xl font-bold mb-4")
    
    urg = [b for b in bins if b.fill_level >= 80]
    
    # Bin selector for pathfinding
    bin_options = {b.id: f"{b.id} - {b.waste_type} ({b.fill_level}%)" for b in bins}
    
    # Controls
    with ui.card().classes("w-full p-4 shadow-sm mb-4"):
        with ui.row().classes("w-full gap-4 items-center"):
            selected_bin = ui.select(
                options=["None"] + list(bin_options.keys()),
                value="None",
                label="Select bin for shortest path"
            ).classes("flex-1")
            
            with ui.row().classes("gap-3 items-center"):
                ui.label(f"Urgent: {len(urg)}").classes("text-sm font-semibold text-red-600 bg-red-50 px-3 py-2 rounded-lg")
                show_all_bins = ui.switch("All Bins", value=True)
                show_network = ui.switch("Road Network", value=False)
    
    # Containers
    map_container = ui.column().classes("w-full mb-4")
    table_container = ui.column().classes("w-full")
    
    def update_view():
        map_container.clear()
        table_container.clear()
        
        # Path calculation for map (if needed)
        path = []
        if selected_bin.value != "None":
            bin_obj = next((b for b in bins if b.id == selected_bin.value), None)
            if bin_obj:
                nearest_facility = min(facilities,
                                      key=lambda f: routing.calculate_distance(bin_obj.lat, bin_obj.lon, f.lat, f.lon))
                path = road_graph.dijkstra(bin_obj.id, nearest_facility.id)
        
        # Map
        with map_container:
            fig = go.Figure()
            
            # Add road network if enabled
            if show_network.value:
                for node_id in road_graph.adj:
                    node_pos = road_graph.get_node_pos(node_id)
                    if node_pos:
                        for neighbor_id, weight in road_graph.adj[node_id]:
                            neighbor_pos = road_graph.get_node_pos(neighbor_id)
                            if neighbor_pos:
                                fig.add_trace(go.Scattermapbox(
                                    lat=[node_pos[0], neighbor_pos[0]],
                                    lon=[node_pos[1], neighbor_pos[1]],
                                    mode='lines',
                                    line=dict(width=1, color='rgba(100,100,100,0.3)'),
                                    showlegend=False,
                                    hoverinfo='skip'
                                ))
            
            # Add bins
            bins_to_show = bins if show_all_bins.value else urg
            fig.add_trace(go.Scattermapbox(
                lat=[b.lat for b in bins_to_show],
                lon=[b.lon for b in bins_to_show],
                mode='markers',
                marker=dict(
                    size=14,
                    symbol='circle',
                    color='red'
                ),
                text=[f"{b.id}<br>{b.waste_type}<br>{b.fill_level}%" for b in bins_to_show],
                hovertemplate='<b>%{text}</b><extra>Bin</extra>',
                name='Bins'
            ))
            
            # Add facilities
            fig.add_trace(go.Scattermapbox(
                lat=[f.lat for f in facilities],
                lon=[f.lon for f in facilities],
                mode='markers',
                marker=dict(
                    size=16,
                    symbol='circle',
                    color='#10B981' # Emerald green
                ),
                text=[f"{f.id}<br>Capacity: {f.capacity}<br>Efficiency: {f.efficiency}%" for f in facilities],
                hovertemplate='<b>%{text}</b><extra>Facility</extra>',
                name='Facilities'
            ))
            
            # Show shortest path if bin selected
            if selected_bin.value != "None":
                bin_obj = next((b for b in bins if b.id == selected_bin.value), None)
                if bin_obj:
                    nearest_facility = min(facilities,
                                          key=lambda f: routing.calculate_distance(bin_obj.lat, bin_obj.lon, f.lat, f.lon))
                    path = road_graph.dijkstra(bin_obj.id, nearest_facility.id)
                    
                    if path and len(path) > 1:
                        # Get coordinates for path
                        path_lats = []
                        path_lons = []
                        for node_id in path:
                            pos = road_graph.get_node_pos(node_id)
                            if pos:
                                path_lats.append(pos[0])
                                path_lons.append(pos[1])
                        
                        # Add path line
                        fig.add_trace(go.Scattermapbox(
                            lat=path_lats,
                            lon=path_lons,
                            mode='lines+markers',
                            line=dict(width=4, color='red'),
                            name='Optimal Route'
                        ))
            
            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox=dict(
                    center=dict(lat=25.2048, lon=55.2708),
                    zoom=11
                ),
                margin={"r":0,"t":0,"l":0,"b":0},
                height=500
            )
            ui.plotly(fig).classes("w-full h-96 rounded-lg shadow-md")

        # Table of urgent bins to dispatch
        with table_container:
            ui.label("Dispatch Queue").classes("text-lg font-semibold mb-2")
            if urg:
                import pandas as pd
                df = pd.DataFrame([
                    {"id": b.id, "type": b.waste_type, "fill": b.fill_level, "loc": f"{b.lat:.4f},{b.lon:.4f}"}
                    for b in urg
                ])
                ui.table(
                    columns=[
                        {"name":"id","label":"Bin ID","field":"id"},
                        {"name":"type","label":"Type","field":"type"},
                        {"name":"fill","label":"Fill %","field":"fill"},
                        {"name":"loc","label":"Location","field":"loc"},
                    ],
                    rows=df.to_dict('records'),
                    pagination=10
                ).classes("w-full shadow-md").props('bordered flat separator="cell"')
            else:
                ui.label("No urgent bins").classes("text-gray-500")
    
    selected_bin.on_value_change(lambda: update_view())
    show_all_bins.on_value_change(lambda: update_view())
    show_network.on_value_change(lambda: update_view())
    update_view()
