from typing import Optional

from pydantic import BaseModel


class Header(BaseModel):
    description: Optional[str] = None
    required: Optional[bool] = None
    deprecated: Optional[bool] = None
