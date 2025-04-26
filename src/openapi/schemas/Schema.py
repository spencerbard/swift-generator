from typing import Any, Optional

from pydantic import BaseModel

from src.jsonschema.JSONSchema import JSONSchema
from src.openapi.schemas.ExternalDocumentation import ExternalDocumentation


class XML(BaseModel):
    name: Optional[str] = None
    namespace: Optional[str] = None
    prefix: Optional[str] = None
    attribute: Optional[bool] = None
    wrapped: Optional[bool] = None


class Discriminator(BaseModel):
    propertyName: Optional[str] = None
    mapping: Optional[dict[str, str]] = None


class Schema(JSONSchema):
    xml: Optional[XML] = None
    externalDocs: Optional[ExternalDocumentation] = None
    example: Optional[Any] = None  # This is actually defined as Any
    discriminator: Optional[Discriminator] = None

    def get_references(self) -> list[str]:
        """Returns a list of schema names directly referenced by this schema."""
        references = set()

        def _extract_references(schema_item: JSONSchema) -> None:
            """Extract references from a schema item."""
            # Check for direct reference
            if schema_item.ref_ and schema_item.ref_.startswith("#/components/schemas/"):
                ref_schema_name = schema_item.ref_.split("/")[-1]
                references.add(ref_schema_name)

            # Check properties if it's an object type
            if schema_item.type == "object" and schema_item.properties:
                for _, prop_schema in schema_item.properties.items():
                    _extract_references(prop_schema)

            # Check items if it's an array type
            if schema_item.type == "array" and schema_item.items:
                if isinstance(schema_item.items, list):
                    for item in schema_item.items:
                        _extract_references(item)
                else:
                    _extract_references(schema_item.items)

            # Check for references in anyOf, oneOf, allOf
            for composite_list in [schema_item.anyOf, schema_item.oneOf, schema_item.allOf]:
                if composite_list:
                    for item in composite_list:
                        _extract_references(item)

        # Start the extraction with self
        _extract_references(self)

        return list(references)
