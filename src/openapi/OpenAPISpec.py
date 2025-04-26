import json
from typing import Any, Optional, cast

import yaml
from pydantic import BaseModel

from src.openapi.enums.HttpMethod import EnumHttpMethod
from src.openapi.enums.HttpStatusCode import EnumHttpStatusCode
from src.openapi.schemas.Reference import Reference
from src.openapi.schemas.Response import Response
from src.openapi.schemas.Schema import Schema
from src.openapi.schemas.Spec import Components, Paths, Spec


class ResponseNode(BaseModel):
    path: str
    method: EnumHttpMethod
    status_code: EnumHttpStatusCode
    response: Response | Reference


class OpenAPISpec:
    """A class to parse and provide accessors for an OpenAPI v3 specification."""

    value: Spec

    def __init__(self, filepath: Optional[str] = None, spec_dict: Optional[dict[str, Any]] = None):
        """Initializes the OpenAPISpec instance by loading the OpenAPI spec."""
        raw_value = None
        if filepath is not None:
            raw_value = self._load_spec_file(filepath)
        elif spec_dict is not None:
            raw_value = spec_dict
        else:
            raise ValueError("Either filepath or spec_dict must be provided")

        self.value = Spec.model_validate(raw_value)

    def _load_spec_file(self, filepath: str) -> dict[str, Any]:
        """Loads the OpenAPI specification from a JSON or YAML file."""
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

    @property
    def components(self) -> Components:
        if self.value.components is None:
            return Components(schemas={})
        return self.value.components

    @property
    def schemas(self) -> dict[str, Schema]:
        if self.components.schemas is None:
            return {}
        return self.components.schemas

    @property
    def paths(self) -> Paths:
        if self.value.paths is None:
            return Paths(root={})
        return self.value.paths

    @property
    def responses(self) -> list[ResponseNode]:
        responses = []
        for path, path_item in self.paths.root.items():
            for method, method_item in path_item.methods.items():
                for status_code, response in method_item.responses.root.items():
                    responses.append(
                        ResponseNode(
                            path=path,
                            method=method,
                            status_code=EnumHttpStatusCode.safe_init(status_code),
                            response=response,
                        )
                    )
        return responses

    def get_schema(self, schema_name: str) -> Optional[Schema]:
        """Retrieves a specific schema definition."""
        if self.schemas is None:
            return None
        return self.schemas.get(schema_name)

    def __repr__(self) -> str:
        """Returns a string representation of the OpenAPI specification details."""
        return f"<OpenAPISpec title='{self.value.info.title}' version='{self.value.info.version}'>"


if __name__ == "__main__":
    spec = OpenAPISpec(filepath="src/openapi/__examples/progress.json")
    # for schema_name, schema in spec.schemas.items():
    #     print(f"{schema_name}: {schema.model_dump_json(indent=2, exclude_unset=True, by_alias=True)}")
    #     print("--------------------------------")
    for path, path_item in spec.paths.root.items():
        for method, method_item in path_item.methods.items():
            print(f"{path} {method}: {method_item.model_dump_json(indent=2, exclude_unset=True, by_alias=True)}")
            print("--------------------------------")
    # for response in spec.responses:
    #     print(
    #         f"{response.path} {response.method} {response.status_code}: {response.response.model_dump_json(indent=2, exclude_unset=True, by_alias=True)}"  # noqa: E501
    #     )
