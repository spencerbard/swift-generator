from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel

from src.openapi.enums.HttpMethod import EnumHttpMethod
from src.openapi.schemas.Example import Example
from src.openapi.schemas.ExternalDocumentation import ExternalDocumentation
from src.openapi.schemas.Header import Header
from src.openapi.schemas.Info import Info
from src.openapi.schemas.Link import Link
from src.openapi.schemas.MediaType import MediaType
from src.openapi.schemas.Parameter import Parameter
from src.openapi.schemas.Reference import Reference
from src.openapi.schemas.Response import Response, Responses
from src.openapi.schemas.Schema import Schema
from src.openapi.schemas.SecurityRequirement import SecurityRequirement
from src.openapi.schemas.SecurityScheme import SecurityScheme
from src.openapi.schemas.Server import Server
from src.openapi.schemas.Tag import Tag


class Spec(BaseModel):
    openapi: str
    info: Info
    jsonSchemaDialect: Optional[str] = None
    servers: Optional[list[Server]] = None
    paths: Optional["Paths"] = None
    webhooks: Optional[dict[str, "PathItem"]] = None
    components: Optional["Components"] = None
    security: Optional[list["SecurityRequirement"]] = None
    tags: Optional[list["Tag"]] = None
    externalDocs: Optional[ExternalDocumentation] = None


class Components(BaseModel):
    schemas: Optional[dict[str, Schema]] = None
    responses: Optional[dict[str, Union["Response", Reference]]] = None
    parameters: Optional[dict[str, Union[Parameter, Reference]]] = None
    examples: Optional[dict[str, Union[Example, Reference]]] = None
    requestBodies: Optional[dict[str, Union["RequestBody", Reference]]] = None
    headers: Optional[dict[str, Union[Header, Reference]]] = None
    securitySchemes: Optional[dict[str, Union[SecurityScheme, Reference]]] = None
    links: Optional[dict[str, Union[Link, Reference]]] = None
    callbacks: Optional[dict[str, Union["Callback", Reference]]] = None
    pathItems: Optional[dict[str, "PathItem"]] = None


class Paths(RootModel[dict[str, "PathItem"]]):
    root: dict[str, "PathItem"]


class PathItem(BaseModel):
    ref_: Optional[str] = Field(alias="$ref", default=None)
    summary: Optional[str] = None
    description: Optional[str] = None
    get: Optional["Operation"] = None
    put: Optional["Operation"] = None
    post: Optional["Operation"] = None
    delete: Optional["Operation"] = None
    options: Optional["Operation"] = None
    head: Optional["Operation"] = None
    patch: Optional["Operation"] = None
    trace: Optional["Operation"] = None
    servers: Optional[list[Server]] = None
    parameters: Optional[list[Parameter]] = None

    @property
    def methods(self) -> dict[EnumHttpMethod, "Operation"]:
        all_methods = [method for method in EnumHttpMethod]
        return {method: getattr(self, method) for method in all_methods if getattr(self, method) is not None}


class Operation(BaseModel):
    tags: Optional[list[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    externalDocs: Optional[ExternalDocumentation] = None
    operationId: Optional[str] = None
    parameters: Optional[list[Union[Parameter, Reference]]] = None
    requestBody: Optional[Union["RequestBody", Reference]] = None
    responses_: Optional[Responses] = Field(alias="responses", default=None)
    callbacks: Optional[dict[str, Union["Callback", Reference]]] = None
    deprecated: Optional[bool] = None
    security: Optional[list[SecurityRequirement]] = None
    servers: Optional[list[Server]] = None

    @property
    def responses(self) -> Responses:
        if self.responses_ is None:
            return Responses(root={})
        return self.responses_


class RequestBody(BaseModel):
    model_config = ConfigDict(extra="allow")
    description: Optional[str] = None
    content: dict[str, MediaType]
    required: Optional[bool] = None


class Callback(RootModel[dict[str, "PathItem"]]):
    root: dict[str, "PathItem"]
