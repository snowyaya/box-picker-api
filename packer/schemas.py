from pydantic import BaseModel, Field, field_validator
from typing import List

class Dimensions(BaseModel):
    length: int = Field(..., gt=0)
    width: int = Field(..., gt=0)
    height: int = Field(..., gt=0)

class ItemIn(BaseModel):
    sku: str = Field(..., min_length=1)
    dimensions: Dimensions

class PackRequest(BaseModel):
    items: List[ItemIn] = Field(..., min_length=1)

    @field_validator("items")
    @classmethod
    def unique_skus(cls, items: List[ItemIn]):
        skus = [i.sku for i in items]
        if len(set(skus)) != len(skus):
            raise ValueError("Duplicate sku values are not allowed.")
        return items

class BoxOutDimensions(BaseModel):
    length: int
    width: int
    height: int

class PackedBox(BaseModel):
    box_id: str
    dimensions: BoxOutDimensions
    items: List[str]

class PackResponse(BaseModel):
    boxes: List[PackedBox]
    total_boxes: int
