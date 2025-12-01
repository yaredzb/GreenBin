"""Bins registry view for GreenBin application."""
from nicegui import ui
import pandas as pd
from algorithms.sorting import merge_sort
from algorithms.searching import search_by_substring


def render_bin_registry(bins, open_add_bin_dialog, open_update_fill_dialog, dispatch_bin_logic, simulate_updates_action, collect_urgent_action):
    """Render the bin registry and management view."""
    with ui.row().classes("w-full justify-between items-center mb-6"):
        ui.label("Bin Registry & Management").classes("text-2xl font-bold")
        with ui.row().classes("gap-3"):
            ui.button("Add Bin", on_click=open_add_bin_dialog, icon="add").classes("bg-green-600 text-white")
            ui.button("Update Fill", on_click=open_update_fill_dialog, icon="refresh").props("outline color=primary")
            ui.button("Simulate Updates", on_click=simulate_updates_action, icon="update").props("outline color=secondary")

    # Stats overview
    total_bins = len(bins)
    urgent_bins = len([b for b in bins if b.fill_level >= 80])
    avg_fill = sum(b.fill_level for b in bins) / total_bins if total_bins else 0
    
    with ui.row().classes("w-full gap-4 mb-6"):
        with ui.card().classes("flex-1 p-4 shadow-sm"):
            ui.label("Total Bins").classes("text-sm text-gray-600 mb-1")
            ui.label(str(total_bins)).classes("text-3xl font-bold text-blue-600")
        with ui.card().classes("flex-1 p-4 shadow-sm"):
            ui.label("Urgent (≥80%)").classes("text-sm text-gray-600 mb-1")
            ui.label(str(urgent_bins)).classes("text-3xl font-bold text-red-600")
        with ui.card().classes("flex-1 p-4 shadow-sm"):
            ui.label("Avg Fill Level").classes("text-sm text-gray-600 mb-1")
            ui.label(f"{avg_fill:.1f}%").classes("text-3xl font-bold text-orange-600")

    # Search & filter card
    with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("Bin Directory").classes("text-xl font-bold text-gray-800")
            with ui.row().classes("gap-3 items-center"):
                ui.button("Collect All", on_click=collect_urgent_action, icon="cleaning_services").classes("bg-red-500 text-white")
                ui.label(f"{len(bins)} bins registered").classes("text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full")
        
        with ui.row().classes("w-full gap-4 mb-4"):
            search_input = ui.input(placeholder="Search by Bin ID...").classes("flex-1").props("outlined dense")
            sort_select = ui.select(
                ["ID", "Fill Level", "Type", "Location"], 
                value="Fill Level", 
                label="Sort By"
            ).classes("w-48").props("outlined dense")

        table_container = ui.column().classes("w-full")

        def refresh_bin_table():
            table_container.clear()
            query = search_input.value.strip()
            sort_by = sort_select.value
            
            # Filter
            if query:
                filtered_bins = search_by_substring(bins, lambda b: b.id, query)
            else:
                filtered_bins = bins[:]
            
            # Sort
            if sort_by == "ID":
                filtered_bins = merge_sort(filtered_bins, key=lambda b: b.id)
            elif sort_by == "Fill Level":
                filtered_bins = merge_sort(filtered_bins, key=lambda b: b.fill_level)
                filtered_bins.reverse()
            elif sort_by == "Type":
                filtered_bins = merge_sort(filtered_bins, key=lambda b: b.waste_type)
            elif sort_by == "Location":
                filtered_bins = merge_sort(filtered_bins, key=lambda b: (b.lat, b.lon))

            # Create table data
            df_bins = pd.DataFrame([
                {
                    "id": b.id,
                    "waste_type": b.waste_type,
                    "location": f"{b.lat:.4f}, {b.lon:.4f}",
                    "fill_level": b.fill_level,
                    "status": ("Critical" if b.fill_level >= 80 else
                              "High" if b.fill_level >= 50 else
                              "Medium" if b.fill_level >= 25 else
                              "Low" if b.fill_level > 0 else "Empty")
                }
                for b in filtered_bins
            ])
            
            rows = df_bins.to_dict('records') if not df_bins.empty else []

            with table_container:
                if rows:
                    table = ui.table(
                        columns=[
                            {"name": "id", "label": "Bin ID", "field": "id", "align": "left", "sortable": True},
                            {"name": "type", "label": "Waste Type", "field": "waste_type", "align": "left", "sortable": True},
                            {"name": "loc", "label": "Location", "field": "location", "align": "left"},
                            {"name": "fill", "label": "Fill Level", "field": "fill_level", "align": "center", "sortable": True},
                            {"name": "status", "label": "Status", "field": "status", "align": "center"},
                            {"name": "actions", "label": "Actions", "field": "actions", "align": "center"}
                        ],
                        rows=rows,
                        pagination=10
                    ).classes("w-full").props('flat bordered dense separator="cell"')
                    
                    # Fill level progress bar
                    table.add_slot('body-cell-fill', r'''
                        <q-td :props="props">
                            <div class="flex items-center justify-center gap-2">
                                <q-linear-progress 
                                    :value="props.value / 100" 
                                    :color="props.value >= 80 ? 'red' : props.value >= 50 ? 'orange' : props.value >= 25 ? 'blue' : 'green'" 
                                    track-color="grey-3" 
                                    class="w-28" 
                                    size="8px"
                                    rounded
                                />
                                <span class="text-sm font-semibold">{{ props.value }}%</span>
                            </div>
                        </q-td>
                    ''')
                    
                    # Status badge
                    table.add_slot('body-cell-status', r'''
                        <q-td :props="props">
                            <q-badge 
                                :color="props.value === 'Critical' ? 'red' : 
                                       props.value === 'High' ? 'orange' : 
                                       props.value === 'Medium' ? 'blue' : 
                                       props.value === 'Low' ? 'green' : 'grey'"
                                :label="props.value"
                                class="px-3 py-1"
                                style="min-width: 70px; display: inline-block; text-align: center;"
                            />
                        </q-td>
                    ''')
                    
                    # Action buttons
                    table.add_slot('body-cell-actions', r'''
                        <q-td :props="props">
                            <q-btn 
                                size="sm" 
                                label="Dispatch"
                                color="primary"
                                @click="$parent.$emit('dispatch', props.row)"
                            />
                        </q-td>
                    ''')
                    
                    table.on('dispatch', lambda e: dispatch_bin_logic(e.args['id']))
                else:
                    ui.label("No bins match your search criteria").classes("text-gray-500 text-center py-8")

        search_input.on_value_change(lambda: refresh_bin_table())
        sort_select.on_value_change(lambda: refresh_bin_table())
        refresh_bin_table()
