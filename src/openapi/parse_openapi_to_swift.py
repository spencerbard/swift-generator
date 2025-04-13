import json
from collections import defaultdict
from typing import Any, Dict, Optional

from src.openapi.OpenAPISpec import OpenAPISpec
from src.openapi.OpenAPISwiftModelGenerator import OpenAPISwiftModelGenerator


def parse_openapi_to_swift(filepath: Optional[str] = None, spec: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Parses an OpenAPI JSON file and generates Swift models.

    Args:
        filepath (Optional[str]): Path to the OpenAPI JSON file
        spec (Optional[Dict[str, Any]]): The OpenAPI spec.

    Returns:
        Dict[str, Any]: A dictionary of schema names, their Swift code, and metadata.
    """
    openapi = OpenAPISpec(filepath=filepath, spec=spec)
    swift_model_generator = OpenAPISwiftModelGenerator(openapi)

    # Get the schema hierarchy
    hierarchy = openapi.get_schema_hierarchy()
    print(f"Hierarchy: {json.dumps(hierarchy, indent=2)}")
    return

    # Generate Swift models with metadata
    swift_models = {}

    # Process schemas in dependency order
    processed = set()

    # Track which schemas are referenced and by whom
    referenced_by = defaultdict(set)
    for schema_name, schema_data in hierarchy.items():
        for dep_name in schema_data["dependencies"]:
            referenced_by[dep_name].add(schema_name)

    # Identify nested models that are used by only one other model
    exclusive_nested_models = {}
    for model_name, referrers in referenced_by.items():
        if len(referrers) == 1:
            parent_model = next(iter(referrers))
            exclusive_nested_models[model_name] = parent_model

    # Track which models are responses, errors, etc.
    response_schemas = set()
    error_schemas = set()

    # If we have a full spec with paths, analyze it to identify response/error schemas
    if hasattr(openapi, "spec") and openapi.spec and "paths" in openapi.spec:
        paths = openapi.spec["paths"]
        for path, path_data in paths.items():
            for method, method_data in path_data.items():
                if method.lower() in ["get", "post", "put", "delete", "patch"] and "responses" in method_data:
                    for status_code, response_data in method_data["responses"].items():
                        if "content" in response_data and "application/json" in response_data["content"]:
                            content = response_data["content"]["application/json"]
                            if "schema" in content:
                                schema = content["schema"]
                                if "$ref" in schema:
                                    ref = schema["$ref"]
                                    if ref.startswith("#/components/schemas/"):
                                        schema_name = ref.split("/")[-1]
                                        # Categorize based on status code
                                        if status_code.startswith("2"):  # 2xx success
                                            response_schemas.add(schema_name)
                                        elif status_code.startswith(("4", "5")):  # 4xx or 5xx error
                                            error_schemas.add(schema_name)

    # Models to be included inline in their parent model
    models_to_inline = set()

    # First pass - process all schemas to determine types
    for schema_name in hierarchy:
        # Get schema and determine its type
        schema = openapi.get_schema(schema_name)
        schema_type = "model"  # default type

        if schema is not None:
            if schema_name in referenced_by:
                schema_type = "enum" if "enum" in schema else "nested"
                if schema_name in exclusive_nested_models:
                    parent = exclusive_nested_models[schema_name]
                    if parent in response_schemas or parent in error_schemas:
                        models_to_inline.add(schema_name)
                        schema_type = "inline"
            elif "enum" in schema:
                schema_type = "enum"
            elif schema_name in response_schemas:
                schema_type = "response"
            elif schema_name in error_schemas or ("Error" in schema_name and schema.get("type") == "object"):
                schema_type = "error"

        swift_models[schema_name] = {"type": schema_type}

    def process_schema(schema_name: str) -> None:
        if schema_name in processed:
            return

        # Process dependencies first
        for dep_name in hierarchy[schema_name]["dependencies"]:
            if dep_name in hierarchy and dep_name not in processed and dep_name not in models_to_inline:
                process_schema(dep_name)

        # Get schema
        schema_type = swift_models[schema_name]["type"]

        # Skip inline models - they'll be included with their parent
        if schema_type == "inline":
            processed.add(schema_name)
            return

        # Generate Swift code for this schema
        swift_code = swift_model_generator.generate_model(schema_name)

        # Store code with metadata
        swift_models[schema_name]["code"] = swift_code
        processed.add(schema_name)

    # Process all schemas except those to be inlined
    for schema_name in hierarchy:
        if schema_name not in processed and swift_models[schema_name]["type"] != "inline":
            process_schema(schema_name)

    def find_exclusive_models(
        schema_name: str, models_to_inline: set[str], previous_schemas_checked: set[str]
    ) -> list[str]:
        if schema_name in previous_schemas_checked:
            return []

        previous_schemas_checked.add(schema_name)
        exclusive_models = []
        for name, parent in exclusive_nested_models.items():
            if parent == schema_name and name in models_to_inline:
                exclusive_models.append(name)
                exclusive_models.extend(find_exclusive_models(name, models_to_inline, previous_schemas_checked))

        return exclusive_models

    # Now create combined files for response/error models with their exclusive nested models
    for schema_name, model_data in swift_models.items():
        exclusive_models = find_exclusive_models(schema_name, models_to_inline, set())

        if exclusive_models:
            # Get the main model code
            main_code = model_data["code"]
            inline_codes = []

            # Get all the nested model codes
            for nested_name in exclusive_models:
                if nested_name in swift_models:
                    # Generate code for this nested model
                    nested_code = swift_model_generator.generate_model(nested_name)
                    inline_codes.append(nested_code)

            # Combine codes, putting nested models first
            combined_code = "\n\n".join(inline_codes + [main_code])
            swift_models[schema_name]["code"] = combined_code

    # Filter out models that were inlined
    swift_models = {name: data for name, data in swift_models.items() if data.get("type") != "inline"}

    return swift_models


def write_swift_files(swift_models: Dict[str, Any], output_dir: str) -> None:
    """
    Writes the generated Swift models to separate files in the output directory,
    organizing them into subfolders based on OpenAPI schema semantics.

    Args:
        swift_models: Dictionary of schema names with their Swift code and metadata
        output_dir: Directory to write the files to
    """
    import os

    # Create main output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create subdirectories for different model types
    enum_dir = os.path.join(output_dir, "Enums")
    error_dir = os.path.join(output_dir, "Errors")
    response_dir = os.path.join(output_dir, "Responses")
    nested_dir = os.path.join(output_dir, "Nested")
    model_dir = os.path.join(output_dir, "Models")

    os.makedirs(enum_dir, exist_ok=True)
    os.makedirs(error_dir, exist_ok=True)
    os.makedirs(response_dir, exist_ok=True)
    os.makedirs(nested_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)

    # Category counts
    category_counts = {"Enums": 0, "Errors": 0, "Responses": 0, "Nested": 0, "Models": 0}

    # Create file for each model in the appropriate subdirectory
    for model_name, model_data in swift_models.items():
        if "code" not in model_data:
            continue  # Skip models that were marked for inlining

        model_code = model_data["code"]
        model_type = model_data["type"]

        # Determine the appropriate directory for this model
        if model_type == "enum":
            # This is an enum - put in Enums directory
            target_dir = enum_dir
            category_counts["Enums"] += 1
        elif model_type == "error":
            # This is an error model - put in Errors directory
            target_dir = error_dir
            category_counts["Errors"] += 1
        elif model_type == "response":
            # This is a response model - put in Responses directory
            target_dir = response_dir
            category_counts["Responses"] += 1
        elif model_type == "nested":
            # This is a nested model - put in Nested directory
            target_dir = nested_dir
            category_counts["Nested"] += 1
        else:
            # This is another model type - put in Models directory
            target_dir = model_dir
            category_counts["Models"] += 1

        # Create file path
        file_path = os.path.join(target_dir, f"{model_name}.swift")

        # Write the Swift file
        with open(file_path, "w") as f:
            # Add file header
            header = ["//", "// Generated code - do not modify", "//", "", "import Foundation", "import SwiftData", ""]
            f.write("\n".join(header))
            f.write("\n")
            f.write(model_code)
            f.write("\n")

    # Print summary of generated files
    print(f"Generated Swift files in {output_dir}:")
    for category, count in category_counts.items():
        if count > 0:
            print(f"  - {category}: {count} files")
    print(f"Total: {sum(category_counts.values())} files")


if __name__ == "__main__":
    import argparse
    import os
    import shutil

    parser = argparse.ArgumentParser(description="Generate Swift models from OpenAPI spec")
    parser.add_argument("--openapi", default="src/openapi/examples/progress.json", help="Path to OpenAPI spec file")
    parser.add_argument(
        "--output",
        default="/Users/spencerbard/code/progress/progress-ios/Progress/Data/Generated",
        help="Output directory for Swift files",
    )
    args = parser.parse_args()

    # Generate Swift models
    swift_models = parse_openapi_to_swift(filepath=args.openapi)

    # shutil.rmtree(args.output)

    # # Write models to separate files in organized directories
    # write_swift_files(swift_models, args.output)
