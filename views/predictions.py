"""Predictions view for GreenBin application."""
from nicegui import ui
import pandas as pd
from services.predictor import OverflowPredictor

def render_predictions(bins, history):
    """Render the overflow predictions view."""
    ui.label("Overflow Predictions").classes("text-2xl font-bold mb-4")
    ui.label("Predicted time until overflow based on waste type and fill level.").classes("text-sm text-gray-600 mb-4")

    predictor = OverflowPredictor()
    # Get predictions: list of (hours_remaining, bin_obj)
    predictions = predictor.predict(bins, history)

    # Convert to DataFrame for table
    data = []
    for hours, b in predictions:
        # Categorize based on BOTH time remaining AND current fill level
        # This prevents empty bins from being marked as critical
        
        if b.fill_level >= 85:
            # Already critical fill level
            status = "CRITICAL"
            color = "red"
            if hours < 1:
                time_str = "Immediate"
            elif hours < 24:
                time_str = f"{int(hours)} hours"
            else:
                days = int(hours / 24)
                time_str = f"{days} days"
        elif hours < 12 and b.fill_level >= 60:
            # Will overflow soon AND already moderately full
            time_str = f"{int(hours)} hours"
            status = "CRITICAL"
            color = "red"
        elif hours < 24 and b.fill_level >= 50:
            # Will overflow within a day AND already half full
            time_str = f"{int(hours)} hours"
            status = "Warning"
            color = "orange"
        elif hours < 48:
            # Will overflow within 2 days
            time_str = f"{int(hours)} hours"
            status = "Monitor"
            color = "yellow"
        else:
            # Plenty of time
            days = int(hours / 24)
            time_str = f"{days} days"
            status = "Stable"
            color = "green"

        data.append({
            "id": b.id,
            "type": b.waste_type,
            "fill": f"{b.fill_level}%",
            "time": time_str,
            "status": status,
            "hours_val": hours # for sorting if needed
        })

    df_pred = pd.DataFrame(data)

    if df_pred.empty:
        ui.label("No bins to predict.").classes("text-gray-500")
        return

    columns = [
        {"name":"id","label":"Bin ID","field":"id", "align": "left"},
        {"name":"type","label":"Waste Type","field":"type", "align": "left"},
        {"name":"fill","label":"Current Fill","field":"fill", "align": "right"},
        {"name":"time","label":"Est. Time to Overflow","field":"time", "align": "left"},
        {"name":"status","label":"Status","field":"status", "align": "left"},
    ]

    with ui.table(columns=columns, rows=df_pred.to_dict('records'), pagination=10).classes("w-full shadow-md").props('bordered flat separator="cell" rows-per-page-options="[10,20,50]"') as table:
        table.add_slot('body-cell-status', r'''
            <q-td :props="props">
                <q-chip :color="props.row.status == 'CRITICAL' ? 'red' : props.row.status == 'Warning' ? 'orange' : props.row.status == 'Monitor' ? 'yellow' : 'green'" 
                        text-color="white" 
                        dense 
                        square>
                    {{ props.value }}
                </q-chip>
            </q-td>
        ''')
