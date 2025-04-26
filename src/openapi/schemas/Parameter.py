from enum import StrEnum
from typing import Any, Optional, Self, Union

from pydantic import BaseModel, Field, RootModel, model_validator

from src.openapi.schemas.Example import Example
from src.openapi.schemas.MediaType import MediaType
from src.openapi.schemas.Reference import Reference
from src.openapi.schemas.Schema import Schema


class EnumOpenAPISpecParameterIn(StrEnum):
    query = "query"
    header = "header"
    path = "path"
    cookie = "cookie"


class EnumOpenAPISpecParameterStyle(StrEnum):
    matrix = "matrix"
    label = "label"
    simple = "simple"
    form = "form"
    spaceDelimited = "spaceDelimited"
    pipeDelimited = "pipeDelimited"
    deepObject = "deepObject"


class Parameter_Common(BaseModel):
    name: str
    in_: EnumOpenAPISpecParameterIn = Field(alias="in")
    description: Optional[str] = None
    required: Optional[bool] = None
    deprecated: Optional[bool] = None
    allowEmptyValue: Optional[bool] = None

    @model_validator(mode="after")
    def _validate_required(self) -> Self:
        if self.in_ == EnumOpenAPISpecParameterIn.path and not self.required:
            raise ValueError("Path parameters must be required")
        return self


class Parameter_Schema(Parameter_Common):
    style: Optional[EnumOpenAPISpecParameterStyle] = None
    explode: Optional[bool] = None
    allowReserved: Optional[bool] = None
    schema_: Optional[Schema] = Field(alias="schema", default=None)
    example: Optional[Any] = None  # This is actually defined as Any
    examples: Optional[dict[str, Union[Example, Reference]]] = None


class Parameter_Content(Parameter_Common):
    content: dict[str, MediaType]


class Parameter(RootModel[Union[Parameter_Schema, Parameter_Content]]):
    root: Union[Parameter_Schema, Parameter_Content]
