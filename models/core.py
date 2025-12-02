import datetime
import random
from dataclasses import dataclass, field, asdict

@dataclass
class Bin:
    id: str
    waste_type: str  # Household, Industrial, Recyclable, Organic
    lat: float
    lon: float
    fill_level: int = 0

    def simulate_iot_update(self):
        # random increment 0-15
        self.fill_level = min(100, self.fill_level + random.randint(0, 15))

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Bin(**data)

def get_iso_timestamp():
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')

@dataclass
class CollectionRequest:
    bin_id: str
    timestamp: str = field(default_factory=get_iso_timestamp)
    status: str = "Pending"

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return CollectionRequest(**data)
