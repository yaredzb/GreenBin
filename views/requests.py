"""Collection requests view for GreenBin application."""
from nicegui import ui
import pandas as pd


def process_specific_request(bin_id, requests, request_stack, save_all, dispatch_bin_logic, refresh_ui):
    """Process a specific collection request."""
    for i, r in enumerate(requests):
        if r.bin_id == bin_id:
            req = requests.pop(i)
            request_stack.append(("request_add", req))
            save_all()
            dispatch_bin_logic(bin_id)
            ui.notify(f"Processed request for {bin_id}", color="positive")
            refresh_ui()
            return


def reject_specific_request(bin_id, requests, save_all, refresh_ui):
    """Reject a specific collection request."""
    for i, r in enumerate(requests):
        if r.bin_id == bin_id:
            req = requests.pop(i)
            save_all()
            ui.notify(f"Rejected request for {bin_id}", color="info")
            refresh_ui()
            return


def render_requests(requests, undo_last_action, process_request_action, process_specific_request_fn, reject_specific_request_fn):
    """Render the collection requests view."""
    with ui.row().classes("w-full justify-between items-center mb-6"):
        ui.label("Collection Requests").classes("text-2xl font-bold")
        with ui.row().classes("gap-3"):
            ui.button("Undo Last", on_click=undo_last_action, icon="undo").props("outline color=grey-7")
            ui.button("Process Next", on_click=process_request_action, icon="play_arrow").classes("bg-blue-600 text-white")
    
    # Stats overview
    total_requests = len(requests)
    pending_requests = len([r for r in requests if r.status == "Pending"])
    
    with ui.row().classes("w-full gap-4 mb-6"):
        with ui.card().classes("flex-1 p-4 shadow-sm"):
            ui.label("Total Requests").classes("text-sm text-gray-600 mb-1")
            ui.label(str(total_requests)).classes("text-3xl font-bold text-blue-600")
        with ui.card().classes("flex-1 p-4 shadow-sm"):
            ui.label("Pending").classes("text-sm text-gray-600 mb-1")
            ui.label(str(pending_requests)).classes("text-3xl font-bold text-orange-600")
        with ui.card().classes("flex-1 p-4 shadow-sm"):
            ui.label("In Queue").classes("text-sm text-gray-600 mb-1")
            ui.label(str(len([r for r in requests if hasattr(r, 'status') and r.status != "Completed"]))).classes("text-3xl font-bold text-purple-600")
    
    # Main requests card
    with ui.card().classes("w-full p-6 shadow-lg rounded-lg bg-white"):
        with ui.row().classes("w-full justify-between items-center mb-4"):
            ui.label("Request Queue").classes("text-xl font-bold text-gray-800")
            if requests:
                ui.label(f"{len(requests)} requests").classes("text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full")
        
        if requests:
            df_requests = pd.DataFrame([r.to_dict() for r in requests])
            
            table = ui.table(
                columns=[
                    {"name": "bin_id", "label": "Bin ID", "field": "bin_id", "align": "left", "sortable": True},
                    {"name": "time", "label": "Requested At", "field": "timestamp", "align": "left", "sortable": True},
                    {"name": "priority", "label": "Priority", "field": "status", "align": "center"},
                    {"name": "status", "label": "Status", "field": "status", "align": "center"},
                    {"name": "actions", "label": "Actions", "field": "actions", "align": "center"}
                ],
                rows=df_requests.to_dict('records'),
                pagination=10
            ).classes("w-full").props('flat bordered dense separator="cell"')
            
            # Priority indicator
            table.add_slot('body-cell-priority', r'''
                <q-td :props="props">
                    <q-icon 
                        :name="props.value === 'Urgent' ? 'priority_high' : 
                               props.value === 'High' ? 'arrow_upward' : 
                               'remove'"
                        :color="props.value === 'Urgent' ? 'red' : 
                                props.value === 'High' ? 'orange' : 
                                'grey'"
                        size="sm"
                    />
                </q-td>
            ''')
            
            # Status badge
            table.add_slot('body-cell-status', r'''
                <q-td :props="props">
                    <q-badge 
                        :color="props.value === 'Pending' ? 'orange' : 
                                props.value === 'Processing' ? 'blue' : 
                                props.value === 'Completed' ? 'green' : 'grey'"
                        :label="props.value"
                        class="px-3 py-1"
                    />
                </q-td>
            ''')
            
            # Action buttons with icons
            table.add_slot('body-cell-actions', r'''
                <q-td :props="props">
                    <div class="flex gap-2 justify-center">
                        <q-btn 
                            size="sm" 
                            flat
                            dense
                            icon="check_circle" 
                            color="green"
                            @click="$parent.$emit('approve', props.row)"
                        >
                            <q-tooltip>Approve request</q-tooltip>
                        </q-btn>
                        <q-btn 
                            size="sm" 
                            flat
                            dense
                            icon="cancel" 
                            color="red"
                            @click="$parent.$emit('reject', props.row)"
                        >
                            <q-tooltip>Reject request</q-tooltip>
                        </q-btn>
                    </div>
                </q-td>
            ''')
            
            table.on('approve', lambda e: process_specific_request_fn(e.args['bin_id']))
            table.on('reject', lambda e: reject_specific_request_fn(e.args['bin_id']))
        else:
            with ui.column().classes("w-full items-center py-12"):
                ui.icon("inbox", size="64px").classes("text-gray-300 mb-4")
                ui.label("No pending requests").classes("text-xl font-semibold text-gray-600 mb-2")
                ui.label("All collection requests have been processed").classes("text-sm text-gray-500")
