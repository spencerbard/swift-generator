from typing import Any, Optional

from pydantic import BaseModel


class Example(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    value: Optional[Any] = None  # This is actually defined as Any
    externalValue: Optional[str] = None
