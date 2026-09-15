from pydantic import BaseModel
from enum import Enum
from typing import Optional


class PhoneStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


class PhoneNumberCreate(BaseModel):
    e164: str
    country_code: str
    current_carrier: str


class PhoneNumber(BaseModel):
    id: int
    e164: str
    country_code: str
    status: PhoneStatus = PhoneStatus.AVAILABLE
    customer_id: Optional[int] = None
    current_carrier: str
    signature: Optional[str] = None
    version: int = 1


class StatusUpdate(BaseModel):
    new_status: PhoneStatus
    version: int
