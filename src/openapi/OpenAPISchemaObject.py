"""
For more info on JSON Schema spec, see here:
    - https://www.learnjsonschema.com/2020-12
    - https://json-schema.org/understanding-json-schema/reference

This file contains the Pydantic models for the JSON Schema spec.
This is a work in progress and not all fields are supported yet.
"""

from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Self

from pydantic import BaseModel, Field

NotYetSupported = Annotated[Literal[None], Field(description="Not yet supported")]


class OpenAPISchemaTypeEnum(str, Enum):
    string = "string"
    object = "object"
    integer = "integer"
    number = "number"
    boolean = "boolean"
    array = "array"
    null = "null"


class OpenAPISchemaSharedApplicatorFields(BaseModel):
    allOf: NotYetSupported
    anyOf: NotYetSupported
    oneOf: NotYetSupported
    if_: Literal[None] = Field(None, alias="if", description="Not yet supported")
    then: NotYetSupported
    else_: Literal[None] = Field(None, alias="else", description="Not yet supported")
    not_: Literal[None] = Field(None, alias="not", description="Not yet supported")


class OpenAPISchemaCoreFields(BaseModel):
    _id: Optional[str] = Field(alias="$id", default=None)
    # TODO: Support more versions
    _schema: Literal["https://json-schema.org/draft/2020-12/schema"] = "https://json-schema.org/draft/2020-12/schema"
    _ref: Optional[str] = Field(alias="$ref", default=None)
    _comment: Optional[str] = Field(alias="$comment", default=None)
    _defs: Optional[Dict[str, "OpenAPISchemaObject"]] = Field(alias="$defs", default=None)

    _anchor: Literal[None] = Field(None, alias="$anchor", description="Not yet supported")
    _dynamicAnchor: Literal[None] = Field(None, alias="$dynamicAnchor", description="Not yet supported")
    _dynamicRef: Literal[None] = Field(None, alias="$dynamicRef", description="Not yet supported")
    _vocabulary: Literal[None] = Field(None, alias="$vocabulary", description="Not yet supported")


class OpenAPISchemaMetadataFields(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    deprecated: Optional[bool] = None
    examples: Optional[List[Any]] = None
    readOnly: Optional[bool] = None
    writeOnly: Optional[bool] = None


class OpenAPIObjectSchema(OpenAPISchemaMetadataFields):
    type: Literal[OpenAPISchemaTypeEnum.object] = OpenAPISchemaTypeEnum.object
    required: List[str] = []
    properties: Optional[Dict[str, "OpenAPISchemaObject"]] = None

    additionalProperties: NotYetSupported
    minProperties: NotYetSupported
    maxProperties: NotYetSupported
    patternProperties: NotYetSupported
    dependentRequired: NotYetSupported
    dependentSchemas: NotYetSupported
    unevaluatedProperties: NotYetSupported


class OpenAPIStringFormatEnum(str, Enum):
    date_time = "date-time"
    date = "date"
    time = "time"
    duration = "duration"
    email = "email"
    idn_email = "idn-email"
    hostname = "hostname"
    idn_hostname = "idn-hostname"
    ipv4 = "ipv4"
    ipv6 = "ipv6"
    uri = "uri"
    uri_reference = "uri-reference"
    iri = "iri"
    iri_reference = "iri-reference"
    uuid = "uuid"
    uri_template = "uri-template"
    json_pointer = "json-pointer"
    relative_json_pointer = "relative-json-pointer"
    regex = "regex"


class OpenAPIStringSchema(OpenAPISchemaMetadataFields):
    type: Literal[OpenAPISchemaTypeEnum.string] = OpenAPISchemaTypeEnum.string
    format: Optional[OpenAPIStringFormatEnum] = None

    minLength: NotYetSupported
    maxLength: NotYetSupported
    pattern: NotYetSupported

    # Content
    contentEncoding: NotYetSupported
    contentMediaType: NotYetSupported
    contentSchema: NotYetSupported


class OpenAPINumericBaseSchema(OpenAPISchemaMetadataFields):
    minimum: NotYetSupported
    maximum: NotYetSupported
    exclusiveMinimum: NotYetSupported
    exclusiveMaximum: NotYetSupported
    multipleOf: NotYetSupported


class OpenAPIIntegerSchema(OpenAPINumericBaseSchema):
    type: Literal[OpenAPISchemaTypeEnum.integer] = OpenAPISchemaTypeEnum.integer

    format: NotYetSupported


class OpenAPINumberSchema(OpenAPINumericBaseSchema):
    type: Literal[OpenAPISchemaTypeEnum.number] = OpenAPISchemaTypeEnum.number

    format: NotYetSupported


class OpenAPIBooleanSchema(OpenAPISchemaMetadataFields):
    type: Literal[OpenAPISchemaTypeEnum.boolean] = OpenAPISchemaTypeEnum.boolean


class OpenAPIArraySchema(OpenAPISchemaMetadataFields):
    type: Literal[OpenAPISchemaTypeEnum.array] = OpenAPISchemaTypeEnum.array
    items: Self  # TODO: Null `items` w/ non-null `prefixItems` not yet supported, this would need to change to Optional

    prefixItems: NotYetSupported
    unevaluatedItems: NotYetSupported
    contains: NotYetSupported
    minContains: NotYetSupported
    maxContains: NotYetSupported
    minItems: NotYetSupported
    maxItems: NotYetSupported
    uniqueItems: NotYetSupported


class OpenAPINullSchema(OpenAPISchemaMetadataFields):
    type: Literal[OpenAPISchemaTypeEnum.null] = OpenAPISchemaTypeEnum.null


class OpenAPIEnumSchema(OpenAPISchemaMetadataFields):
    enum: List[Any]


class OpenAPISchemaObject(OpenAPISchemaMetadataFields):
    """Pydantic model representing an OpenAPI Schema Object."""

    type: Optional[OpenAPISchemaTypeEnum] = None  # TODO: This should support a list of types
    enum: Optional[List[Any]] = None

    # Validation
    const: NotYetSupported
