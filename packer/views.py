import json
from itertools import permutations

from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST, require_GET
from pydantic import ValidationError

from .schemas import PackRequest, PackResponse, PackedBox, BoxOutDimensions
from .services.packing import Item, find_smallest_single_box, pack_into_boxes
from .services.box_catalog import BOXES


@require_GET
def health(request: HttpRequest):
    return JsonResponse({"ok": True, "path": request.path}, status=200)

@require_POST
def pack(request: HttpRequest):
    # 0) Enforce JSON content type (optional but clean)
    content_type = request.META.get("CONTENT_TYPE", "")
    if "application/json" not in content_type:
        return error_response(
            "unsupported_media_type",
            415,
            details="Use Content-Type: application/json",
        )
    
    # 1) Parse JSON
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError as e:
        return error_response("invalid_json", 400, details=e.msg)

    # 2) Validate input via Pydantic
    try:
        req = PackRequest.model_validate(payload)
    except ValidationError as e:
        # Convert Pydantic errors to JSON-serializable format
        errors = []
        for err in e.errors():
            # Create a clean dict with only JSON-serializable values
            clean_err = {
                "type": err.get("type"),
                "loc": list(err.get("loc", [])),
                "msg": err.get("msg"),
            }
            # Only include input if it's serializable
            if "input" in err:
                try:
                    json.dumps(err["input"])  # Test if serializable
                    clean_err["input"] = err["input"]
                except (TypeError, ValueError):
                    pass  # Skip non-serializable input
            errors.append(clean_err)
        return error_response("validation_error", 400, details=errors)

    # 3) Convert into internal Item objects and keep request order
    items = [
        Item(
            sku=i.sku,
            l=i.dimensions.length,
            w=i.dimensions.width,
            h=i.dimensions.height,
            order=idx,
        )
        for idx, i in enumerate(req.items)
    ]

    # 4) Pre-check: if any item can't fit in the largest box (in any rotation), return 422
    largest = _largest_box()
    too_large = [it for it in items if not _fits_in_box(it, largest)]
    if too_large:
        return error_response(
            "item_too_large",
            422,
            details=[
                {
                    "sku": it.sku,
                    "dimensions": {"length": it.l, "width": it.w, "height": it.h},
                    "max_box_inner_dimensions": {
                        "length": largest.length,
                        "width": largest.width,
                        "height": largest.height,
                    },
                }
                for it in too_large
            ],
        )

    # Case 1: fits in a single box
    single = find_smallest_single_box(items)
    ordered_skus = [it.sku for it in sorted(items, key=lambda x: x.order)]

    if single is not None:
        resp = PackResponse(
            boxes=[
                PackedBox(
                    box_id=single.box_id,
                    dimensions=BoxOutDimensions(
                        length=single.length, width=single.width, height=single.height
                    ),
                    items=ordered_skus,
                )
            ],
            total_boxes=1,
        )
        return JsonResponse(resp.model_dump(), status=200)

    # Case 2: multiple boxes
    try:
        assignments = pack_into_boxes(items)
    except ValueError as e:
        return error_response("packing_error", 422, details=str(e))

    resp_boxes = []
    for box, box_items in assignments:
        ordered_box_skus = [it.sku for it in sorted(box_items, key=lambda x: x.order)]
        resp_boxes.append(
            PackedBox(
                box_id=box.box_id,
                dimensions=BoxOutDimensions(length=box.length, width=box.width, height=box.height),
                items=ordered_box_skus,
            )
        )

    resp = PackResponse(boxes=resp_boxes, total_boxes=len(resp_boxes))
    return JsonResponse(resp.model_dump(), status=200)


def _fits_in_box(item: Item, box) -> bool:
    b = (box.length, box.width, box.height)
    dims = (item.l, item.w, item.h)

    # any rotation allowed (all permutations)
    rotations = set(permutations(dims, 3))
    return any(l <= b[0] and w <= b[1] and h <= b[2] for (l, w, h) in rotations)


def _largest_box():
    return max(BOXES, key=lambda bx: bx.volume)


def error_response(code: str, status: int, details=None, ctx=None):
    safe_details = None
    if details is not None:
        if isinstance(details, list):
            safe_details = [_json_safe(d) for d in details]
        else:
            safe_details = _json_safe(details)

    safe_ctx = None
    if ctx is not None:
        safe_ctx = {k: _json_safe(v) for k, v in ctx.items()}

    payload = {"error": code}
    if safe_details is not None:
        payload["details"] = safe_details
    if safe_ctx is not None:
        payload["ctx"] = safe_ctx

    return JsonResponse(payload, status=status)


def _json_safe(x):
    """Convert value to JSON-serializable format"""
    if isinstance(x, Exception):
        return str(x)
    if isinstance(x, dict):
        return {k: _json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_safe(item) for item in x]
    # Test if it's JSON serializable
    try:
        json.dumps(x)
        return x
    except (TypeError, ValueError):
        return str(x)
