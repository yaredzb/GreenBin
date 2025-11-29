
import sys
import os

# Add current directory to path so we can import modules
sys.path.append(os.getcwd())

try:
    from models.bin import Bin
    import storage
    
    print("Attempting to load bins...")
    bins = storage.load_bins()
    print(f"Loaded {len(bins)} bins.")
    for b in bins:
        print(b)
except Exception as e:
    print(f"Caught exception: {e}")
