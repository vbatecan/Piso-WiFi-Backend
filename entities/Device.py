from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Device(BaseModel):
    mac_address: str
    time_remaining: int
    last_connected: datetime | None
    is_active: bool

    def __str__(self):
        return f"Device(mac_address={self.mac_address}, time_remaining={self.time_remaining}, last_connected={self.last_connected}, is_active={self.is_active})"