from typing import Optional

from pydantic import BaseModel


class Contact(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None
