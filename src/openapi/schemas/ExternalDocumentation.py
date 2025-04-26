from typing import Optional

from pydantic import BaseModel


class ExternalDocumentation(BaseModel):
    url: str
    description: Optional[str] = None
