import json
import os
import tempfile
from typing import Any, Generator

import pytest

from src.openapi.OpenAPISpec import OpenAPISpec
from src.openapi.OpenAPISwiftModelGenerator import OpenAPISwiftModelGenerator


@pytest.fixture
def sample_schema() -> dict[str, Any]:
    """Create a sample OpenAPI schema with an array schema."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {},
        "components": {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "properties": {"id": {"type": "integer", "x_unique_key": True}, "name": {"type": "string"}},
                    "required": ["id", "name"],
                },
                "Pets": {"type": "array", "items": {"$ref": "#/components/schemas/Pet"}},
            }
        },
    }


@pytest.fixture
def temp_schema_file(sample_schema: dict[str, Any]) -> Generator[str, None, None]:
    """Create a temporary file with the sample schema."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    with open(temp_file.name, "w") as f:
        json.dump(sample_schema, f)

    yield temp_file.name

    # Clean up after the test
    os.unlink(temp_file.name)


def test_array_schema_generation(temp_schema_file: str) -> None:
    """Test that array schemas are properly converted to Swift array types."""
    # Get the Pets schema
    openapi = OpenAPISpec(temp_schema_file)

    # Generate Swift model for the Pets schema
    swift_code = OpenAPISwiftModelGenerator(openapi).generate_model("Pets")

    # The expected Swift code should define an array property
    # Currently, this will fail because the generator doesn't handle top-level array schemas correctly
    expected_code_fragment = "@Model\nfinal class Pets {"
    assert expected_code_fragment in swift_code

    # It should have a property that's an array of Pet objects
    expected_property = "var items: [Pet]"
    assert expected_property in swift_code

    # It should have an initializer for the array
    expected_initializer = "init(items: [Pet])"
    assert expected_initializer in swift_code


def test_unique_key_handling(temp_schema_file: str) -> None:
    """Test that x-unique-key extension is properly converted to @Attribute(.unique)."""
    # Get the Pet schema which has id with x-unique-key: true
    openapi = OpenAPISpec(temp_schema_file)

    # Generate Swift model for the Pet schema
    swift_code = OpenAPISwiftModelGenerator(openapi).generate_model("Pet")

    # Check that the id property has the @Attribute(.unique) annotation
    assert "@Attribute(.unique) var id: Int" in swift_code

    # Check that the name property doesn't have the unique attribute
    assert "@Attribute(.unique) var name:" not in swift_code
    assert "var name: String" in swift_code
