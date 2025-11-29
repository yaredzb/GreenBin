import random
class Bin:
    def __init__(self, id: str, lat: float, lon: float, fill_level: int = 0, waste_type: str = "General"):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.fill_level = fill_level  # 0-100
        self.waste_type = waste_type

    def simulate_iot_update(self):
        # random increment 0-15
        self.fill_level = min(100, self.fill_level + random.randint(0, 15))

    def urgency(self) -> int:
        # urgency measured by fill_level (higher is more urgent)
        return self.fill_level

    def to_dict(self):
        return {
            "id": self.id, 
            "lat": self.lat, 
            "lon": self.lon, 
            "fill_level": self.fill_level,
            "waste_type": self.waste_type
        }

    def __repr__(self):
        return f"Bin({self.id}, type={self.waste_type}, fill={self.fill_level})"
