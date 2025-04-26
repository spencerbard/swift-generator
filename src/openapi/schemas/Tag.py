from typing import Optional

from pydantic import BaseModel

from src.openapi.schemas.ExternalDocumentation import ExternalDocumentation


class Tag(BaseModel):
    name: str
    description: Optional[str] = None
    externalDocs: Optional[ExternalDocumentation] = None
