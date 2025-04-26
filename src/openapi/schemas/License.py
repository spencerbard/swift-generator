from typing import Optional

from pydantic import BaseModel


class License(BaseModel):
    name: str
    identifier: Optional[str] = None
    url: Optional[str] = None
