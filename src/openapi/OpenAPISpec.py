import json
from enum import StrEnum
from typing import Any, Optional, Self, Union, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator


class SchemaOpenAPISpec(BaseModel):
    openapi: str
    info: "SchemaOpenAPISpecInfo"
    jsonSchemaDialect: Optional[str] = None
    servers: Optional[list["SchemaOpenAPISpecServer"]] = None
    paths: Optional["SchemaOpenAPIPaths"] = None
    webhooks: Optional[dict[str, "SchemaOpenAPISpecPathItem"]] = None
    components: Optional["SchemaOpenAPISpecComponents"] = None
    security: Optional[list["SchemaOpenAPISpecSecurityRequirement"]] = None
    tags: Optional[list["SchemaOpenAPISpecTag"]] = None
    externalDocs: Optional["SchemaOpenAPISpecExternalDocumentation"] = None


class SchemaOpenAPISpecInfo(BaseModel):
    title: str
    summary: Optional[str] = None
    description: Optional[str] = None
    termsOfService: Optional[str] = None
    contact: Optional["SchemaOpenAPISpecContact"] = None
    license: Optional["SchemaOpenAPISpecLicense"] = None
    version: Optional[str] = None


class SchemaOpenAPISpecContact(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None


class SchemaOpenAPISpecLicense(BaseModel):
    name: str
    identifier: Optional[str] = None
    url: Optional[str] = None


class SchemaOpenAPISpecServer(BaseModel):
    url: str
    description: Optional[str] = None
    variables: Optional[dict[str, "SchemaOpenAPISpecServerVariable"]] = None


class SchemaOpenAPISpecServerVariable(BaseModel):
    default: str
    enum: Optional[list[str]] = None
    description: Optional[str] = None


class SchemaOpenAPISpecComponents(BaseModel):
    schemas: Optional[dict[str, "SchemaOpenAPISpecSchema"]] = None
    responses: Optional[dict[str, Union["SchemaOpenAPISpecResponse", "SchemaOpenAPISpecReference"]]] = None
    parameters: Optional[dict[str, Union["SchemaOpenAPISpecParameter", "SchemaOpenAPISpecReference"]]] = None
    examples: Optional[dict[str, Union["SchemaOpenAPISpecExample", "SchemaOpenAPISpecReference"]]] = None
    requestBodies: Optional[dict[str, Union["SchemaOpenAPISpecRequestBody", "SchemaOpenAPISpecReference"]]] = None
    headers: Optional[dict[str, Union["SchemaOpenAPISpecHeader", "SchemaOpenAPISpecReference"]]] = None
    securitySchemes: Optional[dict[str, Union["SchemaOpenAPISpecSecurityScheme", "SchemaOpenAPISpecReference"]]] = None
    links: Optional[dict[str, Union["SchemaOpenAPISpecLink", "SchemaOpenAPISpecReference"]]] = None
    callbacks: Optional[dict[str, Union["SchemaOpenAPISpecCallback", "SchemaOpenAPISpecReference"]]] = None
    pathItems: Optional[dict[str, "SchemaOpenAPISpecPathItem"]] = None


class SchemaOpenAPIPaths(RootModel[dict[str, "SchemaOpenAPISpecPathItem"]]):
    root: dict[str, "SchemaOpenAPISpecPathItem"]


class SchemaOpenAPISpecPathItem(BaseModel):
    _ref: Optional[str] = Field(alias="$ref", default=None)
    summary: Optional[str] = None
    description: Optional[str] = None
    get: Optional["SchemaOpenAPISpecOperation"] = None
    put: Optional["SchemaOpenAPISpecOperation"] = None
    post: Optional["SchemaOpenAPISpecOperation"] = None
    delete: Optional["SchemaOpenAPISpecOperation"] = None
    options: Optional["SchemaOpenAPISpecOperation"] = None
    head: Optional["SchemaOpenAPISpecOperation"] = None
    patch: Optional["SchemaOpenAPISpecOperation"] = None
    trace: Optional["SchemaOpenAPISpecOperation"] = None
    servers: Optional[list[SchemaOpenAPISpecServer]] = None
    parameters: Optional[list["SchemaOpenAPISpecParameter"]] = None


class SchemaOpenAPISpecOperation(BaseModel):
    tags: Optional[list[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    externalDocs: Optional["SchemaOpenAPISpecExternalDocumentation"] = None
    operationId: Optional[str] = None
    parameters: Optional[list[Union["SchemaOpenAPISpecParameter", "SchemaOpenAPISpecReference"]]] = None
    requestBody: Optional[Union["SchemaOpenAPISpecRequestBody", "SchemaOpenAPISpecReference"]] = None
    responses: Optional["SchemaOpenAPISpecResponses"] = None
    callbacks: Optional[dict[str, Union["SchemaOpenAPISpecCallback", "SchemaOpenAPISpecReference"]]] = None
    deprecated: Optional[bool] = None
    security: Optional[list["SchemaOpenAPISpecSecurityRequirement"]] = None
    servers: Optional[list["SchemaOpenAPISpecServer"]] = None


class SchemaOpenAPISpecExternalDocumentation(BaseModel):
    url: str
    description: Optional[str] = None


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


class SchemaOpenAPISpecParameter_Common(BaseModel):
    name: str
    _in: EnumOpenAPISpecParameterIn = Field(alias="in")
    description: Optional[str] = None
    required: Optional[bool] = None
    deprecated: Optional[bool] = None
    allowEmptyValue: Optional[bool] = None

    @model_validator(mode="after")
    def _validate_required(self) -> Self:
        if self._in == EnumOpenAPISpecParameterIn.path and not self.required:
            raise ValueError("Path parameters must be required")
        return self


class SchemaOpenAPISpecParameter_Schema(SchemaOpenAPISpecParameter_Common):
    style: Optional[EnumOpenAPISpecParameterStyle] = None
    explode: Optional[bool] = None
    allowReserved: Optional[bool] = None
    _schema: Optional["SchemaOpenAPISpecSchema"] = Field(alias="schema", default=None)
    example: Optional[Any] = None  # This is actually defined as Any
    examples: Optional[dict[str, Union["SchemaOpenAPISpecExample", "SchemaOpenAPISpecReference"]]] = None


class SchemaOpenAPISpecParameter_Content(SchemaOpenAPISpecParameter_Common):
    content: dict[str, "SchemaOpenAPISpecMediaType"]


class SchemaOpenAPISpecParameter(RootModel[Union[SchemaOpenAPISpecParameter_Schema, SchemaOpenAPISpecParameter_Content]]):
    root: Union[SchemaOpenAPISpecParameter_Schema, SchemaOpenAPISpecParameter_Content]


class SchemaOpenAPISpecRequestBody(BaseModel):
    model_config = ConfigDict(extra="allow")
    description: Optional[str] = None
    content: dict[str, "SchemaOpenAPISpecMediaType"]
    required: Optional[bool] = None


class SchemaOpenAPISpecMediaType(BaseModel):
    _schema: Optional["SchemaOpenAPISpecSchema"] = Field(alias="schema", default=None)
    example: Optional[Any] = None  # This is actually defined as Any
    examples: Optional[dict[str, Union["SchemaOpenAPISpecExample", "SchemaOpenAPISpecReference"]]] = None
    encoding: Optional[dict[str, "SchemaOpenAPISpecEncoding"]] = None


class SchemaOpenAPISpecEncoding(BaseModel):
    contentType: Optional[str] = None
    headers: Optional[dict[str, Union["SchemaOpenAPISpecHeader", "SchemaOpenAPISpecReference"]]] = None


class SchemaOpenAPISpecResponses(RootModel[dict[str, Union["SchemaOpenAPISpecResponse", "SchemaOpenAPISpecReference"]]]):
    root: dict[str, Union["SchemaOpenAPISpecResponse", "SchemaOpenAPISpecReference"]]


class SchemaOpenAPISpecResponse(BaseModel):
    description: str
    headers: Optional[dict[str, Union["SchemaOpenAPISpecHeader", "SchemaOpenAPISpecReference"]]] = None
    content: Optional[dict[str, "SchemaOpenAPISpecMediaType"]] = None
    links: Optional[dict[str, Union["SchemaOpenAPISpecLink", "SchemaOpenAPISpecReference"]]] = None


class SchemaOpenAPISpecCallback(RootModel[dict[str, "SchemaOpenAPISpecPathItem"]]):
    root: dict[str, "SchemaOpenAPISpecPathItem"]


class SchemaOpenAPISpecExample(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    value: Optional[Any] = None  # This is actually defined as Any
    externalValue: Optional[str] = None


class SchemaOpenAPISpecLink(BaseModel):
    operationRef: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None  # This is actually defined as Any
    requestBody: Optional[Any] = None  # This is actually defined as Any
    description: Optional[str] = None
    server: Optional[SchemaOpenAPISpecServer] = None


class SchemaOpenAPISpecHeader(BaseModel):
    description: Optional[str] = None
    required: Optional[bool] = None
    deprecated: Optional[bool] = None


class SchemaOpenAPISpecTag(BaseModel):
    name: str
    description: Optional[str] = None
    externalDocs: Optional[SchemaOpenAPISpecExternalDocumentation] = None


class SchemaOpenAPISpecReference(BaseModel):
    _ref: Optional[str] = Field(alias="$ref", default=None)
    summary: Optional[str] = None
    description: Optional[str] = None


class SchemaOpenAPISpecSchema(BaseModel):
    discriminator: Optional["SchemaOpenAPISpecDiscriminator"] = None
    xml: Optional["SchemaOpenAPISpecXML"] = None
    externalDocs: Optional["SchemaOpenAPISpecExternalDocumentation"] = None
    example: Optional[Any] = None  # This is actually defined as Any


class SchemaOpenAPISpecDiscriminator(BaseModel):
    propertyName: str
    mapping: Optional[dict[str, str]] = None


class SchemaOpenAPISpecXML(BaseModel):
    name: Optional[str] = None
    namespace: Optional[str] = None
    prefix: Optional[str] = None
    attribute: Optional[bool] = None
    wrapped: Optional[bool] = None


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


class SchemaOpenAPISpecSecurityScheme(BaseModel):
    type: EnumOpenAPISpecSecuritySchemeType
    description: Optional[str] = None
    name: Optional[str] = None
    _in: Optional[EnumOpenAPISpecSecuritySchemeIn] = Field(alias="in", default=None)
    scheme: Optional[str] = None
    bearerFormat: Optional[str] = None
    flows: Optional["SchemaOpenAPISpecOAuthFlows"] = None
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
        required_set_for_type("_in", EnumOpenAPISpecSecuritySchemeType.apiKey)
        required_set_for_type("scheme", EnumOpenAPISpecSecuritySchemeType.http)
        required_set_for_type("bearerFormat", EnumOpenAPISpecSecuritySchemeType.http)
        required_set_for_type("flows", EnumOpenAPISpecSecuritySchemeType.oauth2)
        required_set_for_type("openIdConnectUrl", EnumOpenAPISpecSecuritySchemeType.openIdConnect)

        return self


class SchemaOpenAPISpecOAuthFlows(BaseModel):
    implicit: Optional["SchemaOpenAPISpecOAuthFlow"] = None
    password: Optional["SchemaOpenAPISpecOAuthFlow"] = None
    clientCredentials: Optional["SchemaOpenAPISpecOAuthFlow"] = None
    authorizationCode: Optional["SchemaOpenAPISpecOAuthFlow"] = None


class SchemaOpenAPISpecOAuthFlow(BaseModel):  # TODO: too complicated for now
    model_config = ConfigDict(extra="allow")


class SchemaOpenAPISpecSecurityRequirement(BaseModel):  # TODO: too complicated for now
    model_config = ConfigDict(extra="allow")


class OpenAPISpec:
    """A class to parse and provide accessors for an OpenAPI v3 specification."""

    spec: dict[str, Any]
    paths: dict[str, SchemaOpenAPISpecPathItem]

    def __init__(self, filepath: Optional[str] = None, spec: Optional[dict[str, Any]] = None):
        """
        Initializes the OpenAPISpec instance by loading the OpenAPI spec.

        Args:
            filepath (str): Path to the OpenAPI spec file (JSON or YAML).
        """
        if filepath is not None:
            self.spec = self._load_spec(filepath)
        elif spec is not None:
            self.spec = spec
        else:
            raise ValueError("Either filepath or spec must be provided")

        self.paths = {}
        for path, path_data in self.spec.get("paths", {}).items():
            self.paths[path] = SchemaOpenAPISpecPathItem.model_validate(path_data)

    def _load_spec(self, filepath: str) -> dict[str, Any]:
        """
        Loads the OpenAPI specification from a JSON or YAML file.

        Args:
            filepath (str): The path to the OpenAPI file.

        Returns:
            Dict[str, Any]: The loaded OpenAPI specification.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                if filepath.endswith(".json"):
                    return cast(dict[str, Any], json.load(file))
                elif filepath.endswith((".yaml", ".yml")):
                    return cast(dict[str, Any], yaml.safe_load(file))
                else:
                    raise ValueError("Unsupported file format. Use JSON or YAML.")
        except Exception as e:
            raise RuntimeError(f"Failed to load OpenAPI file: {e}")

    # Properties
    @property
    def components(self) -> dict[str, Any]:
        """Returns the components of the OpenAPI spec."""
        return cast(dict[str, Any], self.spec.get("components", {}))

    @property
    def schemas(self) -> dict[str, Any]:
        """Returns the schemas of the OpenAPI spec."""
        return cast(dict[str, Any], self.components.get("schemas", {}))

    @property
    def info(self) -> dict[str, Any]:
        """Returns the info of the OpenAPI spec."""
        return cast(dict[str, Any], self.spec.get("info", {}))

    @property
    def title(self) -> Optional[str]:
        """Returns the title of the API."""
        return cast(Optional[str], self.info.get("title"))

    @property
    def version(self) -> Optional[str]:
        """Returns the version of the API."""
        return cast(Optional[str], self.info.get("version"))

    # Getters
    def get_schema(self, schema_name: str) -> Optional[dict[str, Any]]:
        """
        Retrieves a specific schema definition.

        Args:
            schema_name (str): The name of the schema.

        Returns:
            Dict[str, Any]: The schema definition, or None if not found.
        """
        return cast(Optional[dict[str, Any]], self.spec.get("components", {}).get("schemas", {}).get(schema_name))

    def get_schema_hierarchy(self) -> dict[str, Any]:
        """
        Organizes schemas into a hierarchical tree based on their dependencies.

        Returns:
            Dict[str, Any]: A dictionary representing the schema hierarchy where:
                - Keys are schema names
                - Values are dictionaries containing:
                    - 'schema': The schema definition
                    - 'dependencies': A dictionary of schemas this schema depends on
        """
        hierarchy: dict[str, Any] = {}
        schemas = self.spec.get("components", {}).get("schemas", {})

        # First pass: add all schemas to the hierarchy
        for schema_name, schema in schemas.items():
            hierarchy[schema_name] = {"schema": schema, "dependencies": {}}

        # Second pass: identify dependencies
        for schema_name, schema_info in hierarchy.items():
            schema = schema_info["schema"]
            self._add_dependencies(schema_name, schema, hierarchy)

        return hierarchy

    def _add_dependencies(
        self, schema_name: str, schema: dict[str, Any], hierarchy: dict[str, Any], path: Optional[list[str]] = None
    ) -> None:
        """
        Recursively identifies and adds dependencies for a schema.

        Args:
            schema_name (str): The name of the schema being processed
            schema (Dict[str, Any]): The schema definition
            hierarchy (Dict[str, Any]): The hierarchy being built
            path (List[str], optional): Path of schema names to detect circular references
        """
        if path is None:
            path = []

        # Prevent circular references
        if schema_name in path:
            return

        path = path + [schema_name]

        # Process properties if this is an object
        if schema.get("type") == "object" and "properties" in schema:
            for prop_name, prop_schema in schema.get("properties", {}).items():
                self._process_property(schema_name, prop_schema, hierarchy, path)

        # Process array items
        elif schema.get("type") == "array" and "items" in schema:
            self._process_property(schema_name, schema["items"], hierarchy, path)

        # Process allOf, oneOf, anyOf
        for key in ["allOf", "oneOf", "anyOf"]:
            if key in schema:
                for sub_schema in schema[key]:
                    self._process_property(schema_name, sub_schema, hierarchy, path)

    def _process_property(
        self, parent_schema_name: str, prop_schema: dict[str, Any], hierarchy: dict[str, Any], path: list[str]
    ) -> None:
        """
        Process a property to identify dependencies.

        Args:
            parent_schema_name (str): The name of the parent schema
            prop_schema (dict[str, Any]): The property schema
            hierarchy (dict[str, Any]): The hierarchy being built
            path (list[str]): Path of schema names to detect circular references
        """
        # Handle $ref
        if "$ref" in prop_schema:
            ref = prop_schema["$ref"]
            if ref.startswith("#/components/schemas/"):
                ref_schema_name = ref.split("/")[-1]

                # Add to dependencies if it's a known schema
                if ref_schema_name in hierarchy:
                    hierarchy[parent_schema_name]["dependencies"][ref_schema_name] = hierarchy[ref_schema_name]["schema"]
                    # Recursively process the referenced schema
                    self._add_dependencies(ref_schema_name, hierarchy[ref_schema_name]["schema"], hierarchy, path)

        # Recursively process nested objects
        elif prop_schema.get("type") == "object" and "properties" in prop_schema:
            for nested_prop_name, nested_prop_schema in prop_schema.get("properties", {}).items():
                self._process_property(parent_schema_name, nested_prop_schema, hierarchy, path)

        # Recursively process array items
        elif prop_schema.get("type") == "array" and "items" in prop_schema:
            self._process_property(parent_schema_name, prop_schema["items"], hierarchy, path)

        # Process allOf, oneOf, anyOf
        for key in ["allOf", "oneOf", "anyOf"]:
            if key in prop_schema:
                for sub_schema in prop_schema[key]:
                    self._process_property(parent_schema_name, sub_schema, hierarchy, path)

    def __repr__(self) -> str:
        """Returns a string representation of the OpenAPI specification details."""
        return f"<OpenAPISpec title='{self.title}' version='{self.version}' paths={len(self.paths)} schemas={len(self.schemas)}>"  # noqa: E501
