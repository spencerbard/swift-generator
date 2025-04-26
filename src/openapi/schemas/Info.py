from typing import Optional

from pydantic import BaseModel

from src.openapi.schemas.Contact import Contact
from src.openapi.schemas.License import License


class Info(BaseModel):
    title: str
    summary: Optional[str] = None
    description: Optional[str] = None
    termsOfService: Optional[str] = None
    contact: Optional[Contact] = None
    license: Optional[License] = None
    version: Optional[str] = None
