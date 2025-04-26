import shutil
from collections import defaultdict
from typing import Any, Dict, Optional

from pydantic import BaseModel

from src.openapi.OpenAPISpec import OpenAPISpec
from src.openapi.OpenAPISwiftModelGenerator import OpenAPISwiftModelGenerator
from src.openapi.schemas.Schema import Schema


class SchemaGroup(BaseModel):
    root_schema_name: str
    root_schema: Schema
    ref_levels: dict[str, int]
    schemas: dict[str, Schema]


class SchemasGroupedByDeps(BaseModel):
    schema_groups: list[SchemaGroup]
    shared_schemas: dict[str, Schema]


def group_schemas_by_deps(openapi: OpenAPISpec) -> SchemasGroupedByDeps:
    # For each schema, get the names of the schemas that reference it
    referenced_by = defaultdict(set)
    for schema_name, schema in openapi.schemas.items():
        for reference in schema.get_references():
            referenced_by[reference].add(schema_name)

    # Get the schema_name, schema pairs for all schemas that are not referenced by any other schema
    root_schemas = [x for x in openapi.schemas.items() if x[0] not in referenced_by]

    schema_groups: list[SchemaGroup] = []
    for root_schema_name, root_schema in root_schemas:
        schema_group = SchemaGroup(
            root_schema_name=root_schema_name,
            root_schema=root_schema,
            ref_levels={root_schema_name: 0},
            schemas={root_schema_name: root_schema},
        )
        references_to_check = set(root_schema.get_references())
        references_checked: set[str] = set(root_schema_name)

        while not all(referenced_schema_name in references_checked for referenced_schema_name in references_to_check):
            referenced_schema_name = references_to_check.pop()

            # Skip if we've already checked this schema or it's already in the group
            if referenced_schema_name in references_checked or referenced_schema_name in schema_group.schemas:
                continue

            # Get the referenced schema
            referenced_schema = openapi.schemas.get(referenced_schema_name)
            if not referenced_schema:
                raise ValueError(f"Could not find schema: {referenced_schema_name}")

            if all(name in schema_group.schemas for name in referenced_by[referenced_schema_name]):
                schema_group.schemas[referenced_schema_name] = referenced_schema
                cur_level = max(schema_group.ref_levels[name] for name in referenced_by[referenced_schema_name])
                schema_group.ref_levels[referenced_schema_name] = cur_level + 1
                for reference in referenced_schema.get_references():
                    if reference not in schema_group.schemas:
                        references_to_check.add(reference)

                # Reset the references checked set to recheck if references might be now all in the group
                references_checked = set()

            references_checked.add(referenced_schema_name)

        schema_groups.append(schema_group)

    all_schemas_in_groups: set[str] = set()
    for schema_group in schema_groups:
        all_schemas_in_groups.add(schema_group.root_schema_name)
        all_schemas_in_groups.update(schema_group.schemas.keys())
    shared_schemas = {k: v for k, v in openapi.schemas.items() if k not in all_schemas_in_groups}

    return SchemasGroupedByDeps(schema_groups=schema_groups, shared_schemas=shared_schemas)


def parse_openapi_to_swift(filepath: Optional[str] = None, spec_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Parses an OpenAPI JSON file and generates Swift models.

    Args:
        filepath: Path to the OpenAPI JSON file
        spec_dict: The OpenAPI spec as a dictionary

    Returns:
        Dict[str, Any]: A dictionary of schema names, their Swift code, and metadata.
    """
    openapi = OpenAPISpec(filepath=filepath, spec_dict=spec_dict)
    swift_model_generator = OpenAPISwiftModelGenerator(openapi)

    # Get the schema hierarchy
    schema_groups = group_schemas_by_deps(openapi)

    # Generate Swift models with metadata
    swift_models = {}
    for schema_group in schema_groups.schema_groups:
        schemas_ordered = sorted(schema_group.schemas.keys(), key=lambda x: schema_group.ref_levels[x])
        code = "\n\n".join(swift_model_generator.generate_model(schema_name) for schema_name in schemas_ordered)
        swift_models[schema_group.root_schema_name] = {"type": "root", "code": code}
    for schema_name in schema_groups.shared_schemas:
        swift_models[schema_name] = {"type": "shared", "code": swift_model_generator.generate_model(schema_name)}

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

    # Delete the output directory if it exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # Create main output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create subdirectories for different model types
    root_dir = os.path.join(output_dir, "Root")
    shared_dir = os.path.join(output_dir, "Shared")

    os.makedirs(root_dir, exist_ok=True)
    os.makedirs(shared_dir, exist_ok=True)

    # Category counts
    category_counts = {"Root": 0, "Shared": 0}

    # Create file for each model in the appropriate subdirectory
    for model_name, model_data in swift_models.items():
        if "code" not in model_data:
            continue  # Skip models that were marked for inlining

        model_code = model_data["code"]
        model_type = model_data["type"]

        # Determine the appropriate directory for this model
        if model_type == "root":
            target_dir = root_dir
            category_counts["Root"] += 1
        else:
            target_dir = shared_dir
            category_counts["Shared"] += 1

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

    parser = argparse.ArgumentParser(description="Generate Swift models from OpenAPI spec")
    parser.add_argument("--openapi", default="src/openapi/__examples/progress.json", help="Path to OpenAPI spec file")
    parser.add_argument(
        "--output",
        default="/Users/spencerbard/code/progress/progress-ios/Progress/Data/Generated",
        help="Output directory for Swift files",
    )
    args = parser.parse_args()

    # Generate Swift models
    swift_models = parse_openapi_to_swift(filepath=args.openapi)

    # Write models to separate files in organized directories
    write_swift_files(swift_models, args.output)
