import heapq
from math import sqrt

def calculate_distance(lat1, lon1, lat2, lon2):
    # Simple Euclidean distance approximation for small areas
    return sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


def optimize_route(start_lat, start_lon, bins):
    """
    Simple Nearest Neighbor algorithm for route optimization.
    Returns a list of (lat, lon) tuples representing the path.
    """
    if not bins:
        return []

    path = [(start_lat, start_lon)]
    unvisited = bins.copy()
    current_lat, current_lon = start_lat, start_lon

    while unvisited:
        # Find nearest bin
        nearest = min(unvisited, key=lambda b: calculate_distance(current_lat, current_lon, b.lat, b.lon))
        path.append((nearest.lat, nearest.lon))
        current_lat, current_lon = nearest.lat, nearest.lon
        unvisited.remove(nearest)
    
    return path
