from typing import Any, Optional

from pydantic import BaseModel

from src.openapi.schemas.Server import Server


class Link(BaseModel):
    operationRef: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None  # This is actually defined as Any
    requestBody: Optional[Any] = None  # This is actually defined as Any
    description: Optional[str] = None
    server: Optional[Server] = None
