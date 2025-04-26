"""
Pydantic schemas representing JSON Schema Draft 2020-12 specification.

This module provides a complete set of Pydantic models for working with JSON Schema Draft 2020-12.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Self, Union

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, model_validator

# Basic types and utilities
JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class EnumSchemaType(str, Enum):
    """The type of a JSON Schema."""

    ARRAY = "array"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NULL = "null"
    NUMBER = "number"
    OBJECT = "object"
    STRING = "string"


class EnumSchemaTypeExtra(str, Enum):
    """Extra types defined in JSON Schema."""

    ENUM = "enum"
    CONST = "const"
    ANY_OF = "anyOf"
    ONE_OF = "oneOf"
    NOT = "not"
    IF = "if"
    ALL_OF = "allOf"


EnumSchemaTypeExtended = Union[EnumSchemaType, EnumSchemaTypeExtra]


class EnumFormat(str, Enum):
    """Common formats defined in JSON Schema."""

    DATE = "date"
    DATETIME = "date-time"
    EMAIL = "email"
    HOSTNAME = "hostname"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    URI = "uri"
    UUID = "uuid"
    URI_REFERENCE = "uri-reference"
    URI_TEMPLATE = "uri-template"
    JSON_POINTER = "json-pointer"
    RELATIVE_JSON_POINTER = "relative-json-pointer"
    REGEX = "regex"
    TIME = "time"
    DURATION = "duration"
    IRI = "iri"
    IRI_REFERENCE = "iri-reference"


# Core Schema: https://www.learnjsonschema.com/2020-12/applicator/properties/
class JSONSchema(BaseModel):
    """Represents a JSON Schema document according to Draft 2020-12 specification."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    # Core
    id_: Optional[AnyUrl] = Field(None, alias="$id")
    schema_: Optional[AnyUrl] = Field(None, alias="$schema")
    ref_: Optional[str] = Field(None, alias="$ref")
    comment_: Optional[str] = Field(None, alias="$comment")
    defs_: Optional[Dict[str, "JSONSchema"]] = Field(None, alias="$defs")
    anchor_: Optional[str] = Field(None, alias="$anchor")
    dynamic_ref_: Optional[str] = Field(None, alias="$dynamicRef")
    dynamic_anchor_: Optional[str] = Field(None, alias="$dynamicAnchor")
    vocabulary_: Optional[Dict[AnyUrl, bool]] = Field(None, alias="$vocabulary")

    # Applicator
    allOf: Optional[List["JSONSchema"]] = None
    anyOf: Optional[List["JSONSchema"]] = None
    oneOf: Optional[List["JSONSchema"]] = None
    if_: Optional["JSONSchema"] = Field(None, alias="if")
    then: Optional["JSONSchema"] = None
    else_: Optional["JSONSchema"] = Field(None, alias="else")
    not_: Optional["JSONSchema"] = Field(None, alias="not")
    properties: Optional[Dict[str, "JSONSchema"]] = None
    additionalProperties: Optional[Union[bool, "JSONSchema"]] = None
    patternProperties: Optional[Dict[str, "JSONSchema"]] = None
    dependentSchemas: Optional[Dict[str, "JSONSchema"]] = None
    propertyNames: Optional["JSONSchema"] = None
    contains: Optional["JSONSchema"] = None
    items: Optional[Union["JSONSchema", List["JSONSchema"]]] = None
    prefixItems: Optional[List["JSONSchema"]] = None

    @model_validator(mode="after")
    def validate_then_else(self) -> Self:
        if self.if_ is None and self.then is not None:
            raise ValueError("`then` can only be provided if `if` is provided")
        if self.if_ is None and self.else_ is not None:
            raise ValueError("`else` can only be provided if `if` is provided")
        return self

    # Validation
    type: Optional[Union[EnumSchemaType, List[EnumSchemaType]]] = None
    enum: Optional[List[JSONType]] = None
    const: Optional[JSONType] = None
    maxLength: Optional[int] = Field(None, ge=0)
    minLength: Optional[int] = Field(None, ge=0)
    pattern: Optional[str] = None
    exclusiveMaximum: Optional[float] = None
    exclusiveMinimum: Optional[float] = None
    maximum: Optional[float] = None
    minimum: Optional[float] = None
    multipleOf: Optional[float] = None
    dependentRequired: Optional[Dict[str, List[str]]] = None
    maxProperties: Optional[int] = Field(None, ge=0)
    minProperties: Optional[int] = Field(None, ge=0)
    required: Optional[List[str]] = None
    maxItems: Optional[int] = Field(None, ge=0)
    minItems: Optional[int] = Field(None, ge=0)
    maxContains: Optional[int] = Field(None, ge=0)
    minContains: Optional[int] = Field(None, ge=0)
    uniqueItems: Optional[bool] = None

    # Meta Data
    title: Optional[str] = None
    description: Optional[str] = None
    default: Optional[JSONType] = None
    deprecated: Optional[bool] = None
    examples: Optional[List[JSONType]] = None
    readOnly: Optional[bool] = None
    writeOnly: Optional[bool] = None

    # Format Annotation
    format: Optional[Union[EnumFormat, str]] = None

    # Content
    contentEncoding: Optional[str] = None
    contentMediaType: Optional[str] = None
    contentSchema: Optional["JSONSchema"] = None

    # Unevaluated
    unevaluatedItems: Optional["JSONSchema"] = None
    unevaluatedProperties: Optional[Union[bool, "JSONSchema"]] = None

    # Custom extensions
    x_unique_key: Optional[bool] = None
