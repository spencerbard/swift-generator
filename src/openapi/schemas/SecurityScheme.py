from enum import StrEnum
from typing import Optional, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OAuthFlows(BaseModel):
    implicit: Optional["OAuthFlow"] = None
    password: Optional["OAuthFlow"] = None
    clientCredentials: Optional["OAuthFlow"] = None
    authorizationCode: Optional["OAuthFlow"] = None


class OAuthFlow(BaseModel):  # TODO: too complicated for now
    model_config = ConfigDict(extra="allow")


class EnumOpenAPISpecSecuritySchemeIn(StrEnum):
    query = "query"
    header = "header"
    cookie = "cookie"


class EnumOpenAPISpecSecuritySchemeType(StrEnum):
    apiKey = "apiKey"
    http = "http"
    mutualTLS = "mutualTLS"
    oauth2 = "oauth2"
    openIdConnect = "openIdConnect"


class SecurityScheme(BaseModel):
    type: EnumOpenAPISpecSecuritySchemeType
    description: Optional[str] = None
    name: Optional[str] = None
    in_: Optional[EnumOpenAPISpecSecuritySchemeIn] = Field(alias="in", default=None)
    scheme: Optional[str] = None
    bearerFormat: Optional[str] = None
    flows: Optional["OAuthFlows"] = None
    openIdConnectUrl: Optional[str] = None

    @model_validator(mode="after")
    def _validate_required(self) -> Self:
        def required_set_for_type(field_name: str, field_type: EnumOpenAPISpecSecuritySchemeType) -> None:
            is_type = self.type == field_type
            is_set = getattr(self, field_name) is not None
            if is_type and not is_set:
                raise ValueError(f"{field_type} security scheme must have a {field_name} value")
            if not is_type and is_set:
                raise ValueError(
                    f"{field_type} security scheme must not have a {field_name} value. {field_name} is only valid for {field_type} security schemes."  # noqa: E501
                )

        required_set_for_type("name", EnumOpenAPISpecSecuritySchemeType.apiKey)
        required_set_for_type("in_", EnumOpenAPISpecSecuritySchemeType.apiKey)
        required_set_for_type("scheme", EnumOpenAPISpecSecuritySchemeType.http)
        required_set_for_type("bearerFormat", EnumOpenAPISpecSecuritySchemeType.http)
        required_set_for_type("flows", EnumOpenAPISpecSecuritySchemeType.oauth2)
        required_set_for_type("openIdConnectUrl", EnumOpenAPISpecSecuritySchemeType.openIdConnect)

        return self
