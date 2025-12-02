from structures.linked_list import LinkedList
from structures.priority_queue import PriorityQueue
from structures.hash_map import HashMap
from structures.avl_tree import AVLTree
from structures.graph import Graph
from structures.queue import Queue
from structures.stack import Stack
from algorithms.sorting import merge_sort
from models import get_iso_timestamp


class CityManager:
    def __init__(self, bins, facilities):

        # bins: list of Bin objects
        self.bins_list = LinkedList()
        for b in bins:
            self.bins_list.add(b)

        # facilities in AVL keyed by facility id 
        self.facilities = AVLTree()
        for f in facilities:
            self.facilities.insert(f.id, f)
            
        # urgent heap
        self.urgent = PriorityQueue()
        for b in bins:
            self.urgent.push(b)
            
        # hash map for fast lookup
        self.bin_map = HashMap()
        for b in bins:
            self.bin_map.set(b.id, b)

        # graph (nodes = bins + facilities)
        self.graph = Graph()
        for b in bins:
            self.graph.add_node(b.id, b.lat, b.lon)
        for f in facilities:
            self.graph.add_node(f.id, f.lat, f.lon)

        # create edges between nearby nodes (k-nearest or radius)
        self._connect_nodes(radius_km=0.05)
        # queue & stack
        self.requests = Queue()
        self.undo_stack = Stack()
        # History tracking
        self.history = [] # List of dicts: {timestamp, bin_id, type, area, status}

    def _connect_nodes(self, radius_km=0.05):
        nodes = list(self.graph.positions.items())  # (node_id, (lat,lon))
        for i in range(len(nodes)):
            id_i, pos_i = nodes[i]
            for j in range(i+1, len(nodes)):
                id_j, pos_j = nodes[j]
                # simple euclidean distance in degrees
                dx = pos_i[0] - pos_j[0]
                dy = pos_i[1] - pos_j[1]
                dist = (dx*dx + dy*dy)**0.5
                if dist <= radius_km:
                    # rough conversion deg->km
                    self.graph.add_edge(id_i, id_j, weight=dist*111)

    def get_all_bins(self):
        return self.bins_list.to_list()

    def get_bin(self, bin_id):
        return self.bin_map.get(bin_id)

    def update_iot(self):
        # simulate updates and rebuild urgent heap
        for b in self.bins_list:
            b.simulate_iot_update()
        # rebuild heap
        self.urgent = PriorityQueue()
        for b in self.bins_list:
            self.urgent.push(b)

    def get_urgent_bins(self, threshold=80):
        # Return bins with fill level >= threshold, sorted by fill level (desc)
        return sorted([b for b in self.bins_list if b.fill_level >= threshold], key=lambda x: x.fill_level, reverse=True)

    def sorted_facilities(self):
        # return facilities sorted by capacity ascending
        facs = self.facilities.values()
        return merge_sort(facs, key=lambda f: f.capacity)

    def add_bin(self, bin_obj):
        self.bins_list.add(bin_obj)
        self.bin_map.set(bin_obj.id, bin_obj)
        self.graph.add_node(bin_obj.id, bin_obj.lat, bin_obj.lon)
        self.urgent.push(bin_obj)
        self.undo_stack.push(("add_bin", bin_obj.id))

    def remove_bin(self, bin_id):
        # Remove from list and map
        if self.bins_list.remove(bin_id):
            self.bin_map.remove(bin_id)
            # Rebuild urgent heap (expensive but safe)
            self.update_iot()
            return True
        return False

    def add_request(self, bin_id):
        self.requests.enqueue(bin_id)
        self.undo_stack.push(("request", bin_id))

    def process_request(self):
        return self.requests.dequeue()

    def undo_last(self):
        action = self.undo_stack.pop()
        if not action:
            return None, None
        
        act_type, data = action
        
        if act_type == "request":
            # Remove specific request from queue
            items = list(self.requests)
            if data in items:
                items.remove(data)
                # Rebuild queue
                self.requests = Queue()
                for it in items:
                    self.requests.enqueue(it)
                return "request", data
                
        elif act_type == "add_bin":
            if self.remove_bin(data):
                return "add_bin", data
                
        return None, None

    def find_route(self, start_id, target_id):
        # uses graph.dijkstra to get list of node ids
        path = self.graph.dijkstra(start_id, target_id)
        # convert to coordinates
        coords = [self.graph.get_node_pos(nid) for nid in path]
        return path, coords

    def log_collection(self, bin_id):
        bin_obj = self.get_bin(bin_id)
        if bin_obj:
            record = {
                "timestamp": get_iso_timestamp(),
                "bin_id": bin_id,
                "type": getattr(bin_obj, "waste_type", "General"),
                "area": f"({bin_obj.lat:.2f}, {bin_obj.lon:.2f})", # Simplified area
                "status": "Collected"
            }
            self.history.append(record)

    def search_history(self, query="", filter_type="All"):
        results = self.history
        if filter_type and filter_type != "All":
            results = [r for r in results if r["type"] == filter_type]
        
        if query:
            q = query.lower()
            results = [r for r in results if q in r["bin_id"].lower() or q in r["area"].lower()]
            
        return results
