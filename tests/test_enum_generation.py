import json
import os
import tempfile
from typing import Any, Dict, Generator

import pytest

from src.openapi.OpenAPISpec import OpenAPISpec
from src.openapi.OpenAPISwiftModelGenerator import OpenAPISwiftModelGenerator


@pytest.fixture
def volume_unit_enum_schema() -> Dict[str, Any]:
    """Create a sample OpenAPI schema with the VolumeUnitTypeEnum."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {},
        "components": {
            "schemas": {
                "VolumeUnitTypeEnum": {
                    "type": "string",
                    "enum": ["tsp", "tbsp", "fl oz", "cup", "pt", "qt", "gal", "ml", "l"],
                    "title": "VolumeUnitTypeEnum",
                }
            }
        },
    }


@pytest.fixture
def temp_enum_schema_file(volume_unit_enum_schema: Dict[str, Any]) -> Generator[str, None, None]:
    """Create a temporary file with the enum schema."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    with open(temp_file.name, "w") as f:
        json.dump(volume_unit_enum_schema, f)

    yield temp_file.name

    # Clean up after the test
    os.unlink(temp_file.name)


def test_direct_enum_generation(temp_enum_schema_file: str) -> None:
    """Test that enum schemas are properly converted to Swift enums using the model generator directly."""
    # Get the VolumeUnitTypeEnum schema
    openapi = OpenAPISpec(filepath=temp_enum_schema_file)

    # Generate Swift model for the VolumeUnitTypeEnum schema
    swift_code = OpenAPISwiftModelGenerator(openapi).generate_model("VolumeUnitTypeEnum")
    print(swift_code)

    # Check that the code contains an enum declaration
    assert "enum VolumeUnitTypeEnum: String, Codable {" in swift_code

    # Check that all enum values are correctly defined
    assert 'case tsp = "tsp"' in swift_code
    assert 'case tbsp = "tbsp"' in swift_code
    assert 'case flOz = "fl oz"' in swift_code  # Spaces converted to camelCase
    assert 'case cup = "cup"' in swift_code
    assert 'case pt = "pt"' in swift_code
    assert 'case qt = "qt"' in swift_code
    assert 'case gal = "gal"' in swift_code
    assert 'case ml = "ml"' in swift_code
    assert 'case l = "l"' in swift_code
