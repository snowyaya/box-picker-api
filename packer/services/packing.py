from dataclasses import dataclass
from typing import List, Optional, Tuple

from .box_catalog import Box, BOXES_SORTED

@dataclass(frozen=True)
class Item:
    sku: str
    l: int
    w: int
    h: int
    order: int  # original order in input list, for stable output

    @property
    def volume(self) -> int:
        return self.l * self.w * self.h

    def orientations(self) -> List[Tuple[int, int, int]]:
        a, b, c = self.l, self.w, self.h
        # 6 unique orientations
        return list({
            (a, b, c), (a, c, b),
            (b, a, c), (b, c, a),
            (c, a, b), (c, b, a),
        })

def _fits_single(item: Item, box: Box) -> bool:
    # Items may be rotated
    for (l, w, h) in item.orientations():
        if l <= box.length and w <= box.width and h <= box.height:
            return True
    return False

def shelf_pack_fits(items: List[Item], box: Box) -> bool:
    """
    Simple 3D shelf/row/layer heuristic.
    - fill along X (length)
    - then new row in Y (width)
    - then new layer in Z (height)
    Items may rotate; we pick the first orientation that fits current cursor.
    This is not optimal 3D bin packing (explicitly not required).
    """
    # place bigger items first
    items_sorted = sorted(items, key=lambda it: (it.volume, max(it.l, it.w, it.h)), reverse=True)

    x = 0
    y = 0
    z = 0

    row_height_y = 0      # max width in current row
    layer_height_z = 0    # max height in current layer

    for it in items_sorted:
        placed = False

        # Try all orientations; prefer ones with larger base first (helps stability)
        ors = sorted(it.orientations(), key=lambda t: (t[0]*t[1], t[2]), reverse=True)

        for (l, w, h) in ors:
            # current row
            if x + l <= box.length and y + w <= box.width and z + h <= box.height:
                # place here
                x += l
                row_height_y = max(row_height_y, w)
                layer_height_z = max(layer_height_z, h)
                placed = True
                break

        if placed:
            continue

        # start new row
        x = 0
        y += row_height_y
        row_height_y = 0

        for (l, w, h) in ors:
            if x + l <= box.length and y + w <= box.width and z + h <= box.height:
                x += l
                row_height_y = max(row_height_y, w)
                layer_height_z = max(layer_height_z, h)
                placed = True
                break

        if placed:
            continue

        # start new layer
        x = 0
        y = 0
        z += layer_height_z
        row_height_y = 0
        layer_height_z = 0

        for (l, w, h) in ors:
            if x + l <= box.length and y + w <= box.width and z + h <= box.height:
                x += l
                row_height_y = max(row_height_y, w)
                layer_height_z = max(layer_height_z, h)
                placed = True
                break

        if not placed:
            return False

    return True

def find_smallest_single_box(items: List[Item]) -> Optional[Box]:
    for box in BOXES_SORTED:
        if all(_fits_single(it, box) for it in items) and shelf_pack_fits(items, box):
            return box
    return None

def pack_into_boxes(items: List[Item]) -> List[Tuple[Box, List[Item]]]:
    """
    Multi-box heuristic:
    - First-fit decreasing by item volume
    - For each item, try existing boxes (smallest total volume solution tends to emerge)
    - If none fits, open the smallest possible new box that can fit it.
    Objective priority:
      1) fewest boxes: we always try existing boxes before opening new
      2) smallest total volume: when opening, choose smallest possible box
      3) prefer smaller boxes: enforced by scanning BOXES_SORTED
    """
    items_sorted = sorted(items, key=lambda it: it.volume, reverse=True)
    assignments: List[Tuple[Box, List[Item]]] = []

    for it in items_sorted:
        placed = False

        # try to place into an existing box (in increasing box volume order)
        # also try smaller-used boxes first by sorting assignments by box volume
        assignments.sort(key=lambda t: t[0].volume)

        for idx, (box, box_items) in enumerate(assignments):
            trial = box_items + [it]
            if all(_fits_single(x, box) for x in trial) and shelf_pack_fits(trial, box):
                box_items.append(it)
                assignments[idx] = (box, box_items)
                placed = True
                break

        if placed:
            continue

        # open a new smallest box that can fit the item alone
        new_box = None
        for b in BOXES_SORTED:
            if _fits_single(it, b) and shelf_pack_fits([it], b):
                new_box = b
                break

        if new_box is None:
            # no available box fits this item at all
            raise ValueError(f"Item '{it.sku}' does not fit in any available box.")

        assignments.append((new_box, [it]))

    # final sort for stable output: smallest boxes first
    assignments.sort(key=lambda t: t[0].volume)
    return assignments
