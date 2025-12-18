from typing import Any
import board
from dataclasses import dataclass, field


@dataclass
class SensorConfig:
    dht_11_pin: Any = field(default_factory=lambda:board.D23)


Config = SensorConfig()
