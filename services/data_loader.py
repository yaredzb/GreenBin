import random
from models.bin import Bin
from models.facility import Facility

# center on Dubai (lat, lon) and generate small offsets for realism
DUBAI_CENTER = (25.2048, 55.2708)


def _rand_coord(center, spread=0.05):
    return center[0] + random.uniform(-spread, spread), center[1] + random.uniform(-spread, spread)


def generate_bins(n=40):
    bins = []
    for i in range(n):
        lat, lon = _rand_coord(DUBAI_CENTER, spread=0.08)
        b = Bin(id=f"B{i+1}", lat=lat, lon=lon,
                fill_level=random.randint(0, 80))
        bins.append(b)
    return bins


def generate_facilities(n=6):
    facilities = []
    for i in range(n):
        lat, lon = _rand_coord(DUBAI_CENTER, spread=0.06)
        f = Facility(id=f"F{i+1}", lat=lat, lon=lon,
                     capacity=random.randint(80, 300))
        facilities.append(f)
    return facilities
