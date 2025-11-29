# This file makes the views directory a Python package
from .dashboard import render_dashboard
from .bins import render_bin_registry
from .requests import render_requests
from .history import render_history
from .dispatch import render_dispatch
from .facilities import render_facility_report
from .predictions import render_predictions

__all__ = [
    'render_dashboard',
    'render_bin_registry',
    'render_requests',
    'render_history',
    'render_dispatch',
    'render_facility_report',
    'render_predictions'
]
