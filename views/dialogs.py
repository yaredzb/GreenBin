"""Dialog components for GreenBin application."""
from nicegui import ui
import actions
import state

def open_add_bin_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Add New Bin").classes("text-xl font-semibold")
        bid = ui.input(label="ID").classes("w-full")    
        btype = ui.select(options=["Household","Industrial","Recyclable","Organic"], label="Bin Type").classes("w-full")
        blat = ui.input(label="Latitude", value="25.2048").classes("w-full")
        blon = ui.input(label="Longitude", value="55.2708").classes("w-full")
        bfill = ui.number(label="Fill %", value=0, min=0, max=100).classes("w-full")
        ui.slider(min=0, max=100, step=1).bind_value(bfill).classes("w-full")
        
        def submit():
            dialog.close()
            actions.add_bin_action(bid.value, btype.value, blat.value, blon.value, bfill.value)
            
        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Add", on_click=submit).classes("bg-green-600 text-white")
    dialog.open()

def open_update_fill_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Update Fill Level").classes("text-xl font-semibold")
        
        # Bin ID dropdown selection
        bin_ids = [b.id for b in state.bins]
        bid = ui.select(
            options=bin_ids,
            label="Bin ID",
            value=bin_ids[0] if bin_ids else None
        ).classes("w-full")
        
        # Fill level input and slider synced
        fill_val = ui.number(label="New Fill %", value=0, min=0, max=100).classes("w-full")
        ui.slider(min=0, max=100, step=1).bind_value(fill_val).classes("w-full")
        
        def submit():
            dialog.close()
            actions.update_fill_action(bid.value, fill_val.value)
            
        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Update", on_click=submit).classes("bg-blue-600 text-white")
    dialog.open()

def open_request_dialog():
    with ui.dialog() as dialog, ui.card().classes("w-96"):
        ui.label("Request Collection").classes("text-xl font-semibold")
        
        # Bin ID dropdown selection
        bin_ids = [b.id for b in state.bins]
        bid = ui.select(
            options=bin_ids,
            label="Bin ID",
            value=bin_ids[0] if bin_ids else None
        ).classes("w-full")
        
        def submit():
            dialog.close()
            actions.request_collection_action(bid.value)
            
        with ui.row().classes("justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Submit", on_click=submit).classes("bg-orange-500 text-white")
    dialog.open()
