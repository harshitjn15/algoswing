from typing import Optional
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


class Note(BaseModel):
    """
    Model for textual observations attached to a stock.
    Example: 'Good volume ATH breakout, waiting for retest.'
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    symbol: str
    content: str
    user_id: str = "default"
    
    # Optional relation to a specific signal or trade
    signal_id: Optional[str] = None
    trade_id: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}
