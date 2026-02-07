# Box Picker API (Django + Pydantic)

Local-only stateless API that selects the optimal shipping box (or boxes) to pack items by dimensions.

## Constraints
- Python + Django
- No external services
- In-memory processing only
- No auth
- No database usage (Django configured but not used by the endpoint)
- Stateless API
- Runs locally

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install django pydantic
python manage.py runserver

## Endpoint
### POST /pack

#### Request:

```json
{
  "items": [
    { "sku": "SKU-CAM-01", "dimensions": { "length": 6, "width": 4, "height": 4 } }
  ]
}

#### Response:
```json
{
  "boxes": [
    {
      "box_id": "BX-M",
      "dimensions": { "length": 12, "width": 10, "height": 6 },
      "items": ["SKU-CAM-01"]
    }
  ],
  "total_boxes": 1
}
