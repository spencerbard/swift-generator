from src.openapi_parser import (
    parse_openapi_yaml,
    openapi_to_python_types,
)


def test_parse_openapi_yaml():
    schemas = parse_openapi_yaml("example_openapi.yaml")
    assert "User" in schemas


def test_openapi_to_python_types():
    assert openapi_to_python_types({"type": "string"}) == "str"
    assert openapi_to_python_types({"type": "integer"}) == "int"
    assert (
        openapi_to_python_types({"type": "array", "items": {"type": "number"}})
        == "list[float]"
    )
