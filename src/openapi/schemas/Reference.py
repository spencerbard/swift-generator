from typing import Optional

from pydantic import BaseModel, Field


class Reference(BaseModel):
    ref_: Optional[str] = Field(alias="$ref", default=None)
    summary: Optional[str] = None
    description: Optional[str] = None
