# 📦 Box Picker API

A local-only Django API that determines optimal shipping box configuration for a set of items based on their dimensions. The API selects the smallest box(es) needed to pack all items, using intelligent algorithms to minimize total boxes and volume.

## 🎯 Features

- **Smart Box Selection**: Automatically finds the smallest box that fits all items
- **Multi-Box Packing**: Intelligently splits items across multiple boxes when needed
- **Item Rotation**: Considers all possible item orientations for optimal fit
- **Input Validation**: Comprehensive validation with clear error messages
- **Stateless Design**: No database or external dependencies required

## 📋 Technical Stack

- **Language**: Python 3.8+
- **Framework**: Django 6.0
- **Validation**: Pydantic
- **Architecture**: Stateless, in-memory processing

## 📦 Box Catalog

The API supports five standard box sizes (unlimited quantities):

| Box ID   | Inner Dimensions (L×W×H inches) | Volume (in³) |
|----------|----------------------------------|--------------|
| BX-S     | 8 × 6 × 4                       | 192          |
| BX-M     | 12 × 10 × 6                     | 720          |
| BX-L     | 16 × 12 × 8                     | 1,536        |
| BX-XL    | 20 × 16 × 12                    | 3,840        |
| BX-XXL   | 24 × 20 × 20                    | 9,600        |

## 🚀 Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd box-picker-api
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django pydantic
   ```

4. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000`

### Verify Installation

Check that the server is running:
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{"ok": true, "path": "/health"}
```

> **Note:** This API does not use trailing slashes (`APPEND_SLASH = False`). Browsers may automatically add trailing slashes to URLs, which will result in 404 errors. Use the exact URLs shown in the examples (without trailing slashes) when testing via curl or API clients.

## 🏃 Running the Application

### Standard Run (Default Port 8000)

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000`

### Run on Different Port

```bash
python manage.py runserver 8080
```

The server will start at `http://127.0.0.1:8080`

### Run on Different Host (Allow External Access)

```bash
python manage.py runserver 0.0.0.0:8000
```

The server will be accessible from other machines on your network at `http://<your-ip>:8000`

### Run in Background (Unix/Linux/Mac)

```bash
nohup python manage.py runserver > server.log 2>&1 &
```

To stop the background server:
```bash
# Find the process ID
ps aux | grep runserver

# Kill the process
kill <process-id>
```

### Stop the Server

Press `Ctrl+C` in the terminal where the server is running

### Common Issues

**Port already in use:**
```
Error: That port is already in use.
```
Solution: Use a different port or kill the process using port 8000
```bash
# On Unix/Linux/Mac
lsof -ti:8000 | xargs kill -9

# On Windows
netstat -ano | findstr :8000
taskkill /PID <process-id> /F
```

**Virtual environment not activated:**
```
ModuleNotFoundError: No module named 'django'
```
Solution: Activate your virtual environment
```bash
source .venv/bin/activate  # Unix/Linux/Mac
.venv\Scripts\activate     # Windows
```

## 📡 API Reference

### `POST /pack`

Determines optimal box configuration for a list of items.

#### Request Headers

```
Content-Type: application/json
```

#### Request Body

```json
{
  "items": [
    {
      "sku": "string (required, non-empty, unique)",
      "dimensions": {
        "length": "integer (required, > 0)",
        "width": "integer (required, > 0)",
        "height": "integer (required, > 0)"
      }
    }
  ]
}
```

#### Response (200 OK)

```json
{
  "boxes": [
    {
      "box_id": "BX-M",
      "dimensions": {
        "length": 12,
        "width": 10,
        "height": 6
      },
      "items": ["SKU-CAM-01", "SKU-LENS-02"]
    }
  ],
  "total_boxes": 1
}
```

#### Error Responses

| Status Code | Error Code              | Description                                    |
|-------------|-------------------------|------------------------------------------------|
| 400         | `invalid_json`          | Request body is not valid JSON                 |
| 400         | `validation_error`      | Input validation failed (details in response)  |
| 415         | `unsupported_media_type`| Content-Type is not application/json          |
| 422         | `item_too_large`        | One or more items exceed largest box capacity  |
| 422         | `packing_error`         | Unable to pack items into available boxes      |

### `GET /health`

Health check endpoint.

#### Response (200 OK)

```json
{
  "ok": true,
  "path": "/health"
}
```

## 🧪 Test Cases

### ✅ Valid Requests

#### 1. Single Small Item

Verifies that a single item is packed into the smallest suitable box.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "sku": "SKU-CAM-01",
        "dimensions": { "length": 6, "width": 4, "height": 4 }
      }
    ]
  }'
```

**Expected**: Single BX-S box (smallest box that fits a 6×4×4 item)

---

#### 2. Multiple Items Fitting in One Box

Tests packing multiple items into a single box.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      { "sku": "SKU-CAM-01", "dimensions": { "length": 6, "width": 4, "height": 4 } },
      { "sku": "SKU-LENS-02", "dimensions": { "length": 8, "width": 4, "height": 4 } }
    ]
  }'
```

**Expected**: Single box containing both items

---

#### 3. Multiple Items Requiring Multiple Boxes

Tests the multi-box packing algorithm with items that cannot fit in a single box.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      { "sku": "ITEM-1", "dimensions": { "length": 20, "width": 15, "height": 10 } },
      { "sku": "ITEM-2", "dimensions": { "length": 20, "width": 15, "height": 10 } },
      { "sku": "ITEM-3", "dimensions": { "length": 20, "width": 15, "height": 10 } }
    ]
  }'
```

**Expected**: Items split across multiple boxes (these items are too large to fit together even in BX-XXL)

---

#### 4. Item Requiring Rotation

Verifies that the API considers item rotations.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      { "sku": "SKU-MIC-01", "dimensions": { "length": 10, "width": 3, "height": 3 } }
    ]
  }'
```

**Expected**: Item packed successfully (rotated to fit if necessary)

---

### ❌ Invalid Requests

#### 5. Missing Items Field

Tests validation when required field is missing.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response** (400):
```json
{
  "error": "validation_error",
  "details": [
    {
      "type": "missing",
      "loc": ["items"],
      "msg": "Field required"
    }
  ]
}
```

---

#### 6. Empty Items Array

Tests validation for empty item list.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{
    "items": []
  }'
```

**Expected Response** (400):
```json
{
  "error": "validation_error",
  "details": [...]
}
```

---

#### 7. Negative or Zero Dimensions

Tests validation for invalid dimension values.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "sku": "BAD-ITEM",
        "dimensions": { "length": -1, "width": 0, "height": 4 }
      }
    ]
  }'
```

**Expected Response** (400):
```json
{
  "error": "validation_error",
  "details": [
    {
      "type": "greater_than",
      "loc": ["items", 0, "dimensions", "length"],
      "msg": "Input should be greater than 0"
    }
  ]
}
```

---

#### 8. Duplicate SKUs

Tests validation for unique SKU constraint.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      { "sku": "DUPLICATE", "dimensions": { "length": 5, "width": 5, "height": 5 } },
      { "sku": "DUPLICATE", "dimensions": { "length": 6, "width": 6, "height": 6 } }
    ]
  }'
```

**Expected Response** (400):
```json
{
  "error": "validation_error",
  "details": [
    {
      "type": "value_error",
      "loc": ["items"],
      "msg": "Value error, Duplicate sku values are not allowed."
    }
  ]
}
```

---

#### 9. Item Too Large for Any Box

Tests handling of items exceeding maximum box capacity.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "sku": "HUGE-ITEM",
        "dimensions": { "length": 100, "width": 100, "height": 100 }
      }
    ]
  }'
```

**Expected Response** (422):
```json
{
  "error": "item_too_large",
  "details": [
    {
      "sku": "HUGE-ITEM",
      "dimensions": { "length": 100, "width": 100, "height": 100 },
      "max_box_inner_dimensions": { "length": 24, "width": 20, "height": 20 }
    }
  ]
}
```

---

#### 10. Invalid JSON

Tests handling of malformed JSON.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{ invalid json }'
```

**Expected Response** (400):
```json
{
  "error": "invalid_json",
  "details": "Expecting property name enclosed in double quotes: line 1 column 3 (char 2)"
}
```

---

#### 11. Wrong Content Type

Tests Content-Type validation.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: text/plain" \
  -d 'hello'
```

**Expected Response** (415):
```json
{
  "error": "unsupported_media_type",
  "details": "Use Content-Type: application/json"
}
```

---

#### 12. Empty SKU

Tests validation for non-empty SKU requirement.

```bash
curl -X POST http://127.0.0.1:8000/pack \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      { "sku": "", "dimensions": { "length": 5, "width": 5, "height": 5 } }
    ]
  }'
```

**Expected Response** (400):
```json
{
  "error": "validation_error",
  "details": [
    {
      "type": "string_too_short",
      "loc": ["items", 0, "sku"],
      "msg": "String should have at least 1 character"
    }
  ]
}
```

## 🏗️ Project Structure

```
box-picker-api/
├── box_picker/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── packer/              # Main application
│   ├── views.py         # API endpoints
│   ├── schemas.py       # Pydantic models
│   ├── urls.py          # URL routing
│   └── services/        # Business logic
│       ├── packing.py   # Packing algorithms
│       └── box_catalog.py
├── manage.py
└── README.md
```

## 🧮 Algorithm Approach

The API uses a heuristic-based approach optimized for the specified criteria:

1. **Pre-validation**: Checks if any item exceeds the largest available box
2. **Single Box Attempt**: Tries to fit all items in the smallest possible single box
3. **Multi-Box Packing**: If single box fails, uses a greedy algorithm to:
   - Sort items by volume (largest first)
   - Pack each item into the smallest available box that fits
   - Minimize total number of boxes and volume

**Note**: This is a heuristic solution. Perfect 3D bin packing is NP-hard, so the algorithm prioritizes reasonable performance and good results over guaranteed optimal solutions.

## 🎯 Optimization Criteria

The API optimizes in the following priority order:

1. **Fewest number of boxes** - Minimize box count
2. **Smallest total volume** - Minimize wasted space
3. **Prefer smaller boxes** - Use smaller boxes over larger ones when possible

---

**Built with Django + Pydantic | No external services required | Runs entirely locally**