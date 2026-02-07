from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Box:
    box_id: str
    length: int
    width: int
    height: int

    @property
    def volume(self) -> int:
        return self.length * self.width * self.height

BOXES: List[Box] = [
    Box("BX-S", 8, 6, 4),
    Box("BX-M", 12, 10, 6),
    Box("BX-L", 16, 12, 8),
    Box("BX-XL", 20, 16, 12),
    Box("BX-XXL", 24, 20, 20),
]

# keep sorted smallest->largest by volume
BOXES_SORTED = sorted(BOXES, key=lambda b: (b.volume, b.length, b.width, b.height))
