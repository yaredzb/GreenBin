class Facility:
    def __init__(self, id: str, lat: float, lon: float, capacity: int, efficiency: float = 0.0):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.capacity = capacity
        self.efficiency = efficiency

    def to_dict(self):
        return {"id": self.id, "lat": self.lat, "lon": self.lon, "capacity": self.capacity, "efficiency": self.efficiency}

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            lat=data.get("lat"),
            lon=data.get("lon"),
            capacity=data.get("capacity"),
            efficiency=data.get("efficiency", 0.0)
        )

    def __repr__(self):
        return f"Facility({self.id}, cap={self.capacity}, eff={self.efficiency})"
