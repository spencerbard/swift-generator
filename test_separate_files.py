import os
import shutil
import tempfile
from collections import defaultdict
from typing import Any, Dict, List

from src.openapi.openapi_to_swift import parse_openapi_to_swift, write_swift_files
from src.openapi.OpenAPISpec import OpenAPISpec

# A more realistic OpenAPI schema with paths section for testing the categorization logic
TEST_SPEC: Dict[str, Any] = {
    "openapi": "3.0.0",
    "info": {"title": "Test API", "version": "1.0.0"},
    "paths": {
        "/recipes": {
            "get": {
                "summary": "Get a list of recipes",
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RecipesResponse"}}},
                    },
                    "400": {
                        "description": "Bad request",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ValidationError"}}},
                    },
                },
            },
            "post": {
                "summary": "Create a new recipe",
                "requestBody": {
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CreateRecipeRequest"}}}
                },
                "responses": {
                    "201": {
                        "description": "Recipe created",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RecipeResponse"}}},
                    },
                    "500": {
                        "description": "Server error",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ServerError"}}},
                    },
                },
            },
        }
    },
    "components": {
        "schemas": {
            "RecipeSourceType": {"type": "string", "enum": ["url_content", "prompt_content"], "title": "RecipeSourceType"},
            "VolumeUnitTypeEnum": {
                "type": "string",
                "enum": ["tsp", "tbsp", "fl oz", "cup", "pt", "qt", "gal", "ml", "l"],
                "title": "VolumeUnitTypeEnum",
                "description": "Volume unit types for recipe measurements",
            },
            "ValidationError": {
                "type": "object",
                "properties": {"code": {"type": "string"}, "message": {"type": "string"}},
                "required": ["code", "message"],
                "title": "ValidationError",
            },
            "ServerError": {
                "type": "object",
                "properties": {"code": {"type": "string"}, "message": {"type": "string"}, "stack": {"type": "string"}},
                "required": ["code", "message"],
                "title": "ServerError",
            },
            "RecipeIngredient": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "amount": {"type": "number"},
                    "unit": {"$ref": "#/components/schemas/VolumeUnitTypeEnum"},
                },
                "required": ["name"],
                "title": "RecipeIngredient",
            },
            "RecipeResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "ingredients": {"type": "array", "items": {"$ref": "#/components/schemas/RecipeIngredient"}},
                    "sourceType": {"$ref": "#/components/schemas/RecipeSourceType"},
                },
                "required": ["id", "name"],
                "title": "RecipeResponse",
            },
            "RecipesResponse": {
                "type": "object",
                "properties": {
                    "recipes": {"type": "array", "items": {"$ref": "#/components/schemas/RecipeResponse"}},
                    "total": {"type": "integer"},
                },
                "required": ["recipes", "total"],
                "title": "RecipesResponse",
            },
            "CreateRecipeRequest": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "ingredients": {"type": "array", "items": {"$ref": "#/components/schemas/RecipeIngredient"}},
                    "sourceType": {"$ref": "#/components/schemas/RecipeSourceType"},
                },
                "required": ["name", "sourceType"],
                "title": "CreateRecipeRequest",
            },
        }
    },
}


def test_separate_files() -> None:
    """Test generating separate Swift files for each model based on OpenAPI semantics."""
    # Create a temporary directory for the output
    temp_dir = tempfile.mkdtemp()
    try:
        # Generate Swift models
        swift_models = parse_openapi_to_swift(spec=TEST_SPEC)

        # Write to separate files in categorized directories
        write_swift_files(swift_models, temp_dir)

        # Verify each expected subdirectory exists
        expected_dirs = ["Enums", "Errors", "Responses", "Nested", "Models"]
        for dir_name in expected_dirs:
            dir_path = os.path.join(temp_dir, dir_name)
            assert os.path.isdir(dir_path), f"Directory {dir_name} was not created"

        # Map each file to its category
        file_categories = defaultdict(list)

        # Check each subdirectory for files
        for dir_name in expected_dirs:
            dir_path = os.path.join(temp_dir, dir_name)
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                print(f"\n{dir_name} directory contains {len(files)} files:")
                for filename in sorted(files):
                    print(f"  - {filename}")
                    file_categories[dir_name].append(filename)

                    # Read the first few lines of the file to verify its contents
                    file_path = os.path.join(dir_path, filename)
                    with open(file_path, "r") as f:
                        content = f.read()
                        print(f"    First 80 chars: {content[:80]}...")

        # Validate file categorization based on the OpenAPI semantics
        assert any(
            filename.startswith("RecipeSourceType") for filename in file_categories["Enums"]
        ), "RecipeSourceType should be in Enums directory"

        assert any(
            filename.startswith("ValidationError") for filename in file_categories["Errors"]
        ), "ValidationError should be in Errors directory"
        assert any(
            filename.startswith("ServerError") for filename in file_categories["Errors"]
        ), "ServerError should be in Errors directory"

        assert any(
            filename.startswith("RecipeResponse") for filename in file_categories["Responses"]
        ), "RecipeResponse should be in Responses directory"
        assert any(
            filename.startswith("RecipesResponse") for filename in file_categories["Responses"]
        ), "RecipesResponse should be in Responses directory"

        assert any(
            filename.startswith("RecipeIngredient") for filename in file_categories["Nested"]
        ), "RecipeIngredient should be in Nested directory"

        print("\nAll files were correctly categorized!")

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_separate_files()
