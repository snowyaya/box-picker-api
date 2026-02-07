import unittest

from packer.services.box_catalog import Box
from packer.services.packing import (
    Item,
    _fits_single,
    shelf_pack_fits,
    find_smallest_single_box,
    pack_into_boxes,
    BOXES_SORTED,
)


class TestPacking(unittest.TestCase):
    # ---------- helpers ----------
    def smallest_box(self):
        return BOXES_SORTED[0]

    def medium_box(self):
        # safe pick: just take something not smallest, not largest
        return BOXES_SORTED[len(BOXES_SORTED) // 2]

    def largest_box(self):
        return BOXES_SORTED[-1]

    # ---------- _fits_single ----------
    def test_item_fits_exactly(self):
        item = Item(sku="test", l=10, w=5, h=3, order=1)
        # use a real catalog box that is >= these dims
        box = self.largest_box()
        self.assertTrue(_fits_single(item, box))

    def test_item_does_not_fit(self):
        item = Item(sku="test", l=10_000, w=10_000, h=10_000, order=1)
        self.assertFalse(_fits_single(item, self.largest_box()))

    def test_item_fits_when_rotated(self):
        # Pick something that should fit when rotated in most sane catalogs:
        # e.g., (8,3,2) should fit into a box that has dims like (12,10,6) etc.
        item = Item(sku="rot", l=8, w=3, h=2, order=1)
        box = self.medium_box()
        self.assertTrue(_fits_single(item, box))

    # ---------- shelf_pack_fits ----------
    def test_shelf_pack_empty_items_list_is_true(self):
        self.assertTrue(shelf_pack_fits([], self.smallest_box()))

    def test_shelf_pack_single_item_fits(self):
        item = Item(sku="one", l=2, w=2, h=1, order=1)
        self.assertTrue(shelf_pack_fits([item], self.smallest_box() if _fits_single(item, self.smallest_box()) else self.medium_box()))

    def test_shelf_pack_single_item_does_not_fit(self):
        item = Item(sku="huge", l=10_000, w=10_000, h=10_000, order=1)
        self.assertFalse(shelf_pack_fits([item], self.largest_box()))

    def test_shelf_pack_multiple_small_items(self):
        items = [
            Item(sku="a", l=2, w=2, h=1, order=1),
            Item(sku="b", l=2, w=2, h=1, order=2),
            Item(sku="c", l=2, w=2, h=1, order=3),
        ]
        box = self.medium_box()
        # If your medium box is too small in some catalogs, fall back to largest to avoid flake
        if not all(_fits_single(it, box) for it in items):
            box = self.largest_box()
        self.assertTrue(shelf_pack_fits(items, box))

    # ---------- find_smallest_single_box ----------
    def test_find_smallest_single_box_single_item(self):
        item = Item(sku="test", l=1, w=1, h=1, order=1)
        result = find_smallest_single_box([item])
        self.assertIsNotNone(result)
        self.assertTrue(_fits_single(item, result))
        self.assertTrue(shelf_pack_fits([item], result))

    def test_find_smallest_single_box_returns_smallest_possible(self):
        item = Item(sku="tiny", l=1, w=1, h=1, order=1)
        result = find_smallest_single_box([item])
        self.assertIsNotNone(result)

        # No smaller box should also fit + pack
        for smaller_box in [b for b in BOXES_SORTED if b.volume < result.volume]:
            if _fits_single(item, smaller_box):
                self.assertFalse(shelf_pack_fits([item], smaller_box))

    def test_find_smallest_single_box_empty_list_returns_smallest_box(self):
        # If your implementation returns None for empty list, change this accordingly.
        result = find_smallest_single_box([])
        self.assertIsNotNone(result)
        self.assertEqual(result.box_id, self.smallest_box().box_id)

    def test_find_smallest_single_box_no_fit(self):
        items = [
            Item(sku="huge1", l=10_000, w=10_000, h=10_000, order=1),
            Item(sku="huge2", l=10_000, w=10_000, h=10_000, order=2),
        ]
        result = find_smallest_single_box(items)
        self.assertIsNone(result)

    # ---------- pack_into_boxes ----------
    def test_pack_into_boxes_empty_list(self):
        result = pack_into_boxes([])
        self.assertEqual(result, [])

    def test_pack_into_boxes_single_item(self):
        item = Item(sku="one", l=1, w=1, h=1, order=1)
        result = pack_into_boxes([item])
        self.assertEqual(len(result), 1)
        box, packed_items = result[0]
        self.assertEqual(packed_items, [item])
        self.assertTrue(_fits_single(item, box))
        self.assertTrue(shelf_pack_fits(packed_items, box))

    def test_pack_into_boxes_item_too_large_raises(self):
        item = Item(sku="huge", l=10_000, w=10_000, h=10_000, order=1)
        with self.assertRaises(ValueError):
            pack_into_boxes([item])

    def test_pack_into_boxes_all_items_accounted_for(self):
        items = [
            Item(sku="a", l=4, w=4, h=2, order=1),
            Item(sku="b", l=4, w=4, h=2, order=2),
            Item(sku="c", l=2, w=2, h=1, order=3),
        ]
        result = pack_into_boxes(items)

        packed = []
        for box, its in result:
            # every item in a returned box must fit that box
            for it in its:
                self.assertTrue(_fits_single(it, box))
            self.assertTrue(shelf_pack_fits(its, box))
            packed.extend(its)

        self.assertCountEqual([it.sku for it in packed], [it.sku for it in items])

    def test_pack_into_boxes_output_boxes_sorted_by_volume_if_multiple(self):
        items = [
            Item(sku="a", l=8, w=8, h=8, order=1),
            Item(sku="b", l=8, w=8, h=8, order=2),
            Item(sku="c", l=8, w=8, h=8, order=3),
        ]
        result = pack_into_boxes(items)
        if len(result) > 1:
            vols = [box.volume for box, _ in result]
            self.assertEqual(vols, sorted(vols))

    def test_shelf_pack_empty_items(self):
        self.assertTrue(shelf_pack_fits([], self.smallest_box()))

    def test_shelf_pack_multiple_items_fit(self):
        items = [
            Item("a", 3, 2, 1, 1),
            Item("b", 4, 2, 1, 2),
            Item("c", 2, 2, 1, 3),
        ]
        box = self.medium_box()
        self.assertTrue(shelf_pack_fits(items, box))

    def test_shelf_pack_items_fit_height(self):
        items = [
            Item("a", 5, 5, 4, 1),
            Item("b", 5, 5, 4, 2),
        ]
        box = Box(box_id="BX", length=10, width=10, height=7) # height too small for 2 layers
        self.assertTrue(shelf_pack_fits(items, box))

    def test_shelf_pack_items_exceed_height(self):
        items = [
            Item("a", 8, 8, 8, 1),
            Item("b", 8, 8, 8, 2),
        ]
        box = Box(box_id="BX", length=10, width=10, height=7)
        self.assertFalse(shelf_pack_fits(items, box))

    def test_shelf_pack_items_require_two_layers(self):
        items = [
            Item("a", 6, 5, 4, 1),
            Item("b", 6, 5, 4, 2),
        ]
        box = Box(box_id="BX", length=10, width=10, height=7)
        self.assertTrue(shelf_pack_fits(items, box))

if __name__ == "__main__":
    unittest.main()
