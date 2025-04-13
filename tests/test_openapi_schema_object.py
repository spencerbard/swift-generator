import json

import pytest

from src.openapi.OpenAPISchemaObject import OpenAPISchemaObject


def test_openapi_schema_object() -> None:
    json_obj = json.load(open("src/openapi/examples/progress.json"))
    pydantic_obj = OpenAPISchemaObject.model_validate(json_obj, strict=True)
    print(pydantic_obj)
