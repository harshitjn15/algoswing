from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class ChartAnnotation(BaseModel):
    """
    MongoDB model for user-drawn annotations on the chart (e.g. trendlines, notes).
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    symbol: str
    type: str  # "trendline", "note", "support", "resistance"
    points: list[Dict[str, Any]]  # e.g., [{"time": 1690000000, "price": 100}, {"time": 1690086400, "price": 110}]
    properties: Dict[str, Any] = {} # color, thickness, text, etc
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
