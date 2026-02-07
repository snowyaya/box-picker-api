import json
from django.test import TestCase, Client

class PackEndpointTests(TestCase):
    def setUp(self):
        self.client = Client()

    def post_pack(self, payload: dict):
        return self.client.post(
            "/pack",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertTrue(body.get("ok"))
        self.assertIn("endpoints", body)
        self.assertIn("POST /pack", body["endpoints"])

    def test_validation_empty_items(self):
        r = self.post_pack({"items": []})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "validation_error")

    def test_duplicate_sku_400(self):
        payload = {
            "items": [
                {"sku": "DUP", "dimensions": {"length": 6, "width": 4, "height": 4}},
                {"sku": "DUP", "dimensions": {"length": 6, "width": 4, "height": 4}},
            ]
        }
        r = self.post_pack(payload)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "validation_error")

    def test_zero_or_negative_dimensions_400(self):
        payloads = [
            {"items": [{"sku": "A", "dimensions": {"length": 0, "width": 4, "height": 4}}]},
            {"items": [{"sku": "A", "dimensions": {"length": -1, "width": 4, "height": 4}}]},
            {"items": [{"sku": "A", "dimensions": {"length": 6, "width": 0, "height": 4}}]},
            {"items": [{"sku": "A", "dimensions": {"length": 6, "width": 4, "height": 0}}]},
        ]
        for p in payloads:
            r = self.post_pack(p)
            self.assertEqual(r.status_code, 400)
            self.assertEqual(r.json()["error"], "validation_error")

    def test_item_too_large_422(self):
        # Largest box is 24x20x20. Make something bigger than that in every orientation.
        payload = {
            "items": [
                {"sku": "HUGE", "dimensions": {"length": 25, "width": 21, "height": 21}},
            ]
        }
        r = self.post_pack(payload)
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json()["error"], "item_too_large")

    def test_deterministic_ordering_kept(self):
        payload = {
            "items": [
                {"sku": "SKU-3", "dimensions": {"length": 6, "width": 4, "height": 4}},
                {"sku": "SKU-1", "dimensions": {"length": 8, "width": 4, "height": 4}},
                {"sku": "SKU-2", "dimensions": {"length": 10, "width": 4, "height": 4}},
            ]
        }
        r = self.post_pack(payload)
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("boxes", body)
        # ensure within each returned box, items preserve original request order
        order = {sku: i for i, sku in enumerate([x["sku"] for x in payload["items"]])}
        for b in body["boxes"]:
            idxs = [order[sku] for sku in b["items"]]
            self.assertEqual(idxs, sorted(idxs))
