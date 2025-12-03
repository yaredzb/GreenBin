import json
import random

file_path = r'd:\University of Dubai\3RD YEAR\Data Structure\Practice\GreenBin_Project\data\bins.json'

with open(file_path, 'r') as f:
    raw_bins = json.load(f)

# Deduplicate by ID, keeping the last occurrence
unique_bins_map = {}
for b in raw_bins:
    unique_bins_map[b['id']] = b

bins = list(unique_bins_map.values())

# Sort by ID for tidiness
bins.sort(key=lambda x: x['id'])

for b in bins:
    # Safe inland bounding box (Al Quoz / Nad Al Sheba area)
    # Lat: 25.10 to 25.18
    # Lon: 55.25 to 55.35
    b['lat'] = round(random.uniform(25.10, 25.18), 5)
    b['lon'] = round(random.uniform(55.25, 55.35), 5)

with open(file_path, 'w') as f:
    json.dump(bins, f, indent=2)

print(f"Fixed locations for {len(bins)} bins (deduplicated).")
