import random
from collections import deque
import models
from models.facility import Facility
import storage
import routing
from structures.avl_tree import AVLTree
from structures.graph import Graph

# ---------- State & Data ----------
bins = storage.load_bins()
requests = storage.load_requests()
history = storage.load_history()
facilities = storage.load_facilities()
request_stack = deque()

# AVL Tree for Facility Lookup (Key: Facility ID)
facilities_avl = AVLTree()
for f in facilities:
    facilities_avl.insert(f.id, f)

# seed sample bins if empty (keeps previous logic)
if not bins:
    for i in range(1, 21):
        b_id = f"B{100 + i}"
        b_type = random.choice(["Household", "Industrial", "Recyclable", "Organic"])
        b_lat = 25.2048 + random.uniform(-0.04, 0.04)
        b_lon = 55.2708 + random.uniform(-0.04, 0.04)
        b_fill = random.randint(0, 95)
        bins.append(models.Bin(id=b_id, waste_type=b_type, lat=b_lat, lon=b_lon, fill_level=b_fill))
    storage.save_bins(bins)

# seed facilities if empty
if not facilities:
    for i in range(1, 6):
        f_id = f"F{100 + i}"
        f_lat = 25.2048 + random.uniform(-0.02, 0.02)
        f_lon = 55.2708 + random.uniform(-0.02, 0.02)
        f_cap = random.randint(1000, 5000)
        f_eff = round(random.uniform(50.0, 99.9), 1)
        new_f = Facility(id=f_id, lat=f_lat, lon=f_lon, capacity=f_cap, efficiency=f_eff)
        facilities.append(new_f)
        facilities_avl.insert(new_f.id, new_f)
    storage.save_facilities(facilities)

# Build road network graph for Dijkstra's algorithm
road_graph = Graph()

def build_road_network():
    """Build road network connecting bins and facilities."""
    global road_graph
    road_graph = Graph()
    
    # Add all bins and facilities as nodes
    for b in bins:
        road_graph.add_node(b.id, b.lat, b.lon)
    for f in facilities:
        road_graph.add_node(f.id, f.lat, f.lon)
    
    # Connect each bin to its 3 nearest neighbors
    all_nodes = [(b.id, b.lat, b.lon) for b in bins] + [(f.id, f.lat, f.lon) for f in facilities]
    
    for node_id, lat, lon in all_nodes:
        # Find 3 nearest neighbors
        distances = []
        for other_id, other_lat, other_lon in all_nodes:
            if node_id != other_id:
                dist = routing.calculate_distance(lat, lon, other_lat, other_lon) * 111  # km
                distances.append((dist, other_id))
        
        distances.sort()
        for dist, neighbor_id in distances[:3]:
            road_graph.add_edge(node_id, neighbor_id, dist)
    
    # Ensure each bin has direct connection to nearest facility
    for b in bins:
        nearest_facility = min(facilities, 
                              key=lambda f: routing.calculate_distance(b.lat, b.lon, f.lat, f.lon))
        dist = routing.calculate_distance(b.lat, b.lon, nearest_facility.lat, nearest_facility.lon) * 111
        road_graph.add_edge(b.id, nearest_facility.id, dist)

build_road_network()

def save_all():
    storage.save_bins(bins)
    storage.save_requests(requests)
    storage.save_history(history)
    storage.save_facilities(facilities)
