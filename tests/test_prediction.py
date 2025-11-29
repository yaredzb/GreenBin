# tests/test_prediction.py
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from structures.min_heap import MinHeap
from services.predictor import OverflowPredictor
from models import Bin

def test_min_heap():
    print("Testing MinHeap...")
    heap = MinHeap()
    heap.push(10, "A")
    heap.push(5, "B")
    heap.push(20, "C")
    
    assert heap.peek() == (5, "B")
    assert heap.pop() == (5, "B")
    assert heap.pop() == (10, "A")
    assert heap.pop() == (20, "C")
    print("MinHeap passed.")

def test_predictor():
    print("Testing OverflowPredictor...")
    bins = [
        Bin(id="B1", waste_type="Organic", fill_level=90, lat=0, lon=0), # High fill, fast rate
        Bin(id="B2", waste_type="Industrial", fill_level=10, lat=0, lon=0), # Low fill, slow rate
        Bin(id="B3", waste_type="Recyclable", fill_level=50, lat=0, lon=0) # Med fill, med rate
    ]
    
    predictor = OverflowPredictor()
    predictions = predictor.predict(bins, [])
    
    # B1 should be first (soonest overflow)
    # B3 second
    # B2 last
    
    print("Predictions:")
    for hours, b in predictions:
        print(f"Bin {b.id}: {hours:.2f} hours")
        
    assert predictions[0][1].id == "B1"
    assert predictions[-1][1].id == "B2"
    print("Predictor passed.")

if __name__ == "__main__":
    test_min_heap()
    test_predictor()
