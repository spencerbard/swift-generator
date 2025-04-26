from typing import Any, Optional, Union

from pydantic import BaseModel, Field

from src.openapi.schemas.Example import Example
from src.openapi.schemas.Header import Header
from src.openapi.schemas.Reference import Reference
from src.openapi.schemas.Schema import Schema


class Encoding(BaseModel):
    contentType: Optional[str] = None
    headers: Optional[dict[str, Union[Header, Reference]]] = None


class MediaType(BaseModel):
    schema_: Optional[Schema] = Field(alias="schema", default=None)
    example: Optional[Any] = None  # This is actually defined as Any
    examples: Optional[dict[str, Union[Example, Reference]]] = None
    encoding: Optional[dict[str, Encoding]] = None
