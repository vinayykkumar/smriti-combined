"""
JSON serialization utilities.
"""
import json
from datetime import datetime
from typing import Any
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for MongoDB ObjectId and datetime.
    """
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def json_serialize(obj: Any) -> str:
    """
    Serialize object to JSON string.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON string
    """
    return json.dumps(obj, cls=JSONEncoder)


def json_deserialize(json_str: str) -> Any:
    """
    Deserialize JSON string to object.
    
    Args:
        json_str: JSON string
        
    Returns:
        Deserialized object
    """
    return json.loads(json_str)
