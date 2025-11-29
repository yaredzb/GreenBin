import datetime
from dataclasses import dataclass, field, asdict

@dataclass
class Bin:
    id: str
    waste_type: str  # Household, Industrial, Recyclable, Organic
    lat: float
    lon: float
    fill_level: int = 0

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Bin(**data)

@dataclass
class CollectionRequest:
    bin_id: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    status: str = "Pending"

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return CollectionRequest(**data)
