"""Chart configurations for the dashboard."""

# --- Dashboard View ---
def get_bin_status_chart_options(bins):
    """Generate EChart options for Bin Status Pie Chart."""
    status_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Empty": 0}
    for b in bins:
        if b.fill_level >= 80: 
            status_counts["Critical"] += 1
        elif b.fill_level >= 50: 
            status_counts["High"] += 1
        elif b.fill_level >= 25: 
            status_counts["Medium"] += 1
        elif b.fill_level > 0: 
            status_counts["Low"] += 1
        else: 
            status_counts["Empty"] += 1

    return {
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} bins ({d}%)",
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "borderColor": "#e5e7eb",
            "borderWidth": 1,
            "textStyle": {"color": "#374151", "fontSize": 13}
        },
        "legend": {
            "orient": "horizontal",
            "bottom": "0%",
            "left": "center",
            "itemGap": 20,
            "itemWidth": 14,
            "itemHeight": 14,
            "textStyle": {"fontSize": 13, "color": "#4b5563", "fontWeight": 500}
        },
        "series": [{
            "name": "Bin Status",
            "type": "pie",
            "radius": ["45%", "75%"],
            "center": ["50%", "45%"],
            "avoidLabelOverlap": True,
            "itemStyle": {
                "borderRadius": 8,
                "borderColor": "#fff",
                "borderWidth": 3,
                "shadowBlur": 10,
                "shadowColor": "rgba(0, 0, 0, 0.1)"
            },
            "label": {
                "show": True,
                "position": "outside",
                "formatter": "{d}%",
                "fontSize": 13,
                "fontWeight": "600",
                "color": "#374151"
            },
            "labelLine": {
                "show": True,
                "length": 15,
                "length2": 10,
                "smooth": True
            },
            "emphasis": {
                "label": {
                    "show": True,
                    "fontSize": 16,
                    "fontWeight": "bold"
                },
                "itemStyle": {
                    "shadowBlur": 20,
                    "shadowColor": "rgba(0, 0, 0, 0.2)"
                },
                "scale": True,
                "scaleSize": 8
            },
            "data": [
                item for item in [
                    {"value": status_counts["Critical"], "name": "Critical", "itemStyle": {"color": "#DC2626"}},
                    {"value": status_counts["High"], "name": "High", "itemStyle": {"color": "#EA580C"}},
                    {"value": status_counts["Medium"], "name": "Medium", "itemStyle": {"color": "#CA8A04"}},
                    {"value": status_counts["Low"], "name": "Low", "itemStyle": {"color": "#16A34A"}},
                    {"value": status_counts["Empty"], "name": "Empty", "itemStyle": {"color": "#6B7280"}}
                ] if item["value"] > 0
            ]
        }]
    }


def get_waste_composition_chart_options(bins):
    """Generate EChart options for Waste Composition Bar Chart."""
    type_counts = {}
    for b in bins:
        type_counts[b.waste_type] = type_counts.get(b.waste_type, 0) + 1

    # Define color palette for different waste types
    waste_colors = {
        "Household": "#6366F1",   # Indigo
        "Industrial": "#64748B",  # Slate
        "Recyclable": "#10B981",  # Emerald
        "Organic": "#84CC16",     # Lime
    }

    # Assign colors based on waste type or use default gradient
    bar_colors = [waste_colors.get(wtype, "#3B82F6") for wtype in type_counts.keys()]

    return {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow",
                "shadowStyle": {
                    "color": "rgba(0, 0, 0, 0.05)"
                }
            },
            "formatter": "{b}: {c} bins",
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "borderColor": "#e5e7eb",
            "borderWidth": 1,
            "textStyle": {"color": "#374151", "fontSize": 13},
            "padding": [10, 15]
        },
        "grid": {
            "left": "10%",
            "right": "4%",
            "bottom": "10%",
            "top": "15%",
            "containLabel": True
        },
        "xAxis": [{
            "type": "category",
            "data": list(type_counts.keys()),
            "axisTick": {
                "alignWithLabel": True,
                "lineStyle": {"color": "#e5e7eb"}
            },
            "axisLine": {
                "lineStyle": {"color": "#e5e7eb", "width": 2}
            },
            "axisLabel": {
                "color": "#6b7280",
                "fontSize": 12,
                "fontWeight": 500,
                "rotate": 45 if len(type_counts) > 6 else 0,
                "interval": 0
            }
        }],
        "yAxis": [{
            "type": "value",
            "boundaryGap": [0, 0.2],
            "name": "Number of Bins",
            "nameTextStyle": {
                "color": "#6b7280",
                "fontSize": 12,
                "fontWeight": 500,
                "padding": [0, 0, 10, 0]
            },
            "axisLine": {
                "show": True,
                "lineStyle": {"color": "#e5e7eb", "width": 2}
            },
            "axisTick": {
                "show": True,
                "lineStyle": {"color": "#e5e7eb"}
            },
            "axisLabel": {
                "color": "#6b7280",
                "fontSize": 12
            },
            "splitLine": {
                "lineStyle": {
                    "color": "#f3f4f6",
                    "type": "dashed"
                }
            }
        }],
        "series": [{
            "name": "Bin Count",
            "type": "bar",
            "barWidth": "50%",
            "data": [
                {
                    "value": count,
                    "itemStyle": {
                        "color": bar_colors[i],
                        "borderRadius": [6, 6, 0, 0],
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.1)",
                        "shadowOffsetY": 2
                    }
                } for i, count in enumerate(type_counts.values())
            ],
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 20,
                    "shadowColor": "rgba(0, 0, 0, 0.2)",
                    "brightness": 1.1
                },
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{c}",
                    "fontSize": 14,
                    "fontWeight": "bold",
                    "color": "#374151"
                }
            },
            "animationDuration": 1000,
            "animationEasing": "elasticOut"
        }]
    }


# --- Facilities View ---
def get_capacity_efficiency_scatter_options(facilities):
    """Generate EChart options for Capacity vs Efficiency Scatter Plot."""
    # Prepare data: [capacity, efficiency, facility_id]
    scatter_data = []
    for f in facilities:
        # Color based on efficiency
        if f.efficiency > 90:
            color = "#10B981"
        elif f.efficiency >= 70:
            color = "#F59E0B"
        else:
            color = "#EF4444"
        
        scatter_data.append({
            "value": [f.capacity, f.efficiency],
            "name": f.id,
            "itemStyle": {"color": color}
        })

    return {
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}<br/>Capacity: {c0}<br/>Efficiency: {c1}%",
            "backgroundColor": "rgba(255, 255, 255, 0.95)",
            "borderColor": "#e5e7eb",
            "textStyle": {"color": "#374151"}
        },
        "grid": {
            "left": "10%",
            "right": "10%",
            "bottom": "15%",
            "top": "15%",
            "containLabel": True
        },
        "xAxis": {
            "type": "value",
            "name": "Capacity",
            "nameLocation": "middle",
            "nameGap": 30,
            "nameTextStyle": {
                "fontSize": 12,
                "fontWeight": "bold",
                "color": "#374151"
            },
            "axisLabel": {
                "color": "#6b7280",
                "fontSize": 11
            },
            "splitLine": {"lineStyle": {"color": "#f3f4f6", "type": "dashed"}}
        },
        "yAxis": {
            "type": "value",
            "name": "Efficiency (%)",
            "nameLocation": "middle",
            "nameGap": 40,
            "nameTextStyle": {
                "fontSize": 12,
                "fontWeight": "bold",
                "color": "#374151"
            },
            "max": 100,
            "axisLabel": {
                "formatter": "{value}%",
                "color": "#6b7280",
                "fontSize": 11
            },
            "splitLine": {"lineStyle": {"color": "#f3f4f6", "type": "dashed"}}
        },
        "series": [{
            "type": "scatter",
            "symbolSize": 15,
            "data": scatter_data,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowColor": "rgba(0, 0, 0, 0.3)"
                },
                "scale": True,
                "scaleSize": 1.2
            },
            "label": {
                "show": True,
                "position": "top",
                "formatter": "{b}",
                "fontSize": 10,
                "color": "#374151"
            }
        }]
    }
