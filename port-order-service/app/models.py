from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class PortStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SUBMITTED_AND_PENDING = "SUBMITTED_AND_PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


class PortOrder(BaseModel):
    e164: str
    customer_id: Optional[int] = None
    status: PortStatus = PortStatus.AVAILABLE
    next_action_at: Optional[datetime] = None
    version: int = 0
