from typing import Annotated, Any, Optional, Union

from pydantic import BaseModel, Discriminator, RootModel, Tag, model_validator

from src.openapi.schemas.Header import Header
from src.openapi.schemas.Link import Link
from src.openapi.schemas.MediaType import MediaType
from src.openapi.schemas.Reference import Reference


def get_discriminator_value(v: Any) -> str:
    has_ref_param: Any = None
    if isinstance(v, dict):
        has_ref_param = "$ref" in v or "ref_" in v
    else:
        has_ref_param = hasattr(v, "$ref") or hasattr(v, "ref_")
    return "reference" if has_ref_param else "response"


class ResponseOrReference(RootModel[Union["Response", Reference]]):
    root: Annotated[
        (Annotated["Response", Tag("response")] | Annotated[Reference, Tag("reference")]),
        Discriminator(get_discriminator_value),
    ]


class Responses(RootModel[dict[str, Union["Response", Reference]]]):
    root: dict[str, Union["Response", Reference]]

    @model_validator(mode="before")
    @classmethod
    def check_values(cls, v: dict[str, Union["Response", Reference]]) -> dict[str, Union["Response", Reference]]:
        if any(isinstance(i, Reference) for i in v.values()):
            raise ValueError("All values must be non-negative")
        return v


class Response(BaseModel):
    description: str
    headers: Optional[dict[str, Union[Header, Reference]]] = None
    content: Optional[dict[str, MediaType]] = None
    links: Optional[dict[str, Union[Link, Reference]]] = None
