"""Shared UI components for GreenBin application."""
from nicegui import ui


def create_stat_card(title, value, subtitle=None, border_color="#FFFFFF"):
    """Create a standardized statistic card."""
    with ui.card().classes("p-4 rounded-xl shadow-md flex-1"):
        with ui.row().classes("items-start justify-between"):
            with ui.column():
                ui.label(title).classes("text-sm text-gray-600")
                ui.label(value).classes("text-2xl font-bold")
                if subtitle:
                    ui.label(subtitle).classes("text-xs text-gray-500")
            ui.icon("bar_chart").classes("text-3xl").style(f"color: {border_color}")
