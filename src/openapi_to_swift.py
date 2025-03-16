import yaml
from typing import Dict, Any


def parse_openapi_yaml(yaml_file: str) -> Dict[str, Any]:
    """
    Parses an OpenAPI YAML file and extracts schemas.

    Args:
        yaml_file (str): Path to the OpenAPI YAML file.

    Returns:
        Dict[str, Any]: A dictionary of schema definitions.
    """
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)

    # Extract components/schemas from OpenAPI
    return data.get("components", {}).get("schemas", {})


def openapi_to_python_types(schema: Dict[str, Any]) -> str:
    """
    Converts OpenAPI schema types to Python types.

    Args:
        schema (Dict[str, Any]): OpenAPI schema definition.

    Returns:
        str: Python type.
    """
    type_mapping = {
        "integer": "int",
        "number": "float",
        "string": "str",
        "boolean": "bool",
        "array": "list",
        "object": "dict",
    }

    if "type" in schema:
        if schema["type"] == "array":
            item_type = openapi_to_python_types(schema.get("items", {}))
            return f"list[{item_type}]"
        return type_mapping.get(schema["type"], "Any")

    return "Any"
