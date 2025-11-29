# Map visualization with Dijkstra's algorithm
import plotly.graph_objects as go

def render_map_view():
    """Render interactive map showing bins, facilities, and shortest paths using Dijkstra."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        ui.label("Plotly not installed. Run: pip install plotly").classes("text-red-500")
        return
    
    ui.label("Route Optimization Map").classes("text-2xl font-bold mb-4")
    ui.label("Visualizing shortest paths from bins to facilities using Dijkstra's algorithm").classes("text-sm text-gray-600 mb-4")
    
    # Bin selector for path visualization
    bin_options = {b.id: f"{b.id} - {b.waste_type} ({b.fill_level}%)" for b in bins}
    
    with ui.row().classes("w-full gap-4 mb-4"):
        selected_bin = ui.select(
            options=["None"] + list(bin_options.keys()),
            value="None",
            label="Select bin to show shortest path"
        ).classes("flex-grow")
        
        show_network = ui.switch("Show Road Network", value=False).classes("ml-4")
    
    map_container = ui.column().classes("w-full")
    
    def update_map():
        map_container.clear()
        
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
            
            # Add shortest path if bin selected
            if selected_bin.value != "None":
                bin_obj = next((b for b in bins if b.id == selected_bin.value), None)
                if bin_obj:
                    # Find nearest facility
                    nearest_facility = min(facilities,
                                          key=lambda f: routing.calculate_distance(bin_obj.lat, bin_obj.lon, f.lat, f.lon))
                    
                    # Calculate shortest path using Dijkstra
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
                            mode='lines',
                            line=dict(width=4, color='red'),
                            name='Shortest Path',
                            hovertemplate='Path segment<extra></extra>'
                        ))
                        
                        # Calculate total distance
                        total_dist = 0
                        for i in range(len(path) - 1):
                            for neighbor, weight in road_graph.adj[path[i]]:
                                if neighbor == path[i+1]:
                                    total_dist += weight
                                    break
                        
                        # Show path info
                        with ui.card().classes("p-4 mb-4 bg-blue-50"):
                            with ui.row().classes("gap-6"):
                                with ui.column():
                                    ui.label("Total Distance").classes("text-xs text-gray-600")
                                    ui.label(f"{total_dist:.2f} km").classes("text-xl font-bold")
                                with ui.column():
                                    ui.label("Path Nodes").classes("text-xs text-gray-600")
                                    ui.label(str(len(path))).classes("text-xl font-bold")
                                with ui.column():
                                    ui.label("Est. CO₂ Saved").classes("text-xs text-gray-600")
                                    ui.label(f"{total_dist * 0.42:.2f} kg").classes("text-xl font-bold")
            
            # Add facilities
            fig.add_trace(go.Scattermapbox(
                lat=[f.lat for f in facilities],
                lon=[f.lon for f in facilities],
                mode='markers',
                marker=dict(size=15, color='purple', symbol='circle'),
                text=[f"{f.id}<br>Efficiency: {f.efficiency}%" for f in facilities],
                hovertemplate='<b>%{text}</b><extra>Facility</extra>',
                name='Facilities'
            ))
            
            # Add bins
            fig.add_trace(go.Scattermapbox(
                lat=[b.lat for b in bins],
                lon=[b.lon for b in bins],
                mode='markers',
                marker=dict(
                    size=10,
                    color=[b.fill_level for b in bins],
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title="Fill %", x=1.02)
                ),
                text=[f"{b.id}<br>{b.waste_type}<br>{b.fill_level}%" for b in bins],
                hovertemplate='<b>%{text}</b><extra>Bin</extra>',
                name='Bins'
            ))
            
            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox_center={"lat": 25.2048, "lon": 55.2708},
                mapbox_zoom=11,
                height=600,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=True,
                legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
            )
            
            ui.plotly(fig).classes('w-full')
    
    selected_bin.on_value_change(lambda: update_map())
    show_network.on_value_change(lambda: update_map())
    update_map()
