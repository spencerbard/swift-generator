from src.openapi.schemas.Response import Responses


def test_responses() -> None:
    input = {
        "200": {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "schema": {
                        "items": {"$ref": "#/components/schemas/RecipeResponse"},
                        "type": "array",
                        "title": "Response List Recipes For User Recipes Get",
                    }
                }
            },
        }
    }
    responses = Responses.model_validate(input)
    print(responses.model_dump_json(exclude_unset=True, by_alias=True, indent=2))
    assert list(input.keys()) == ["200"]

    two_hundred_resp = responses.root.get("200")
    assert two_hundred_resp is not None
    assert two_hundred_resp.model_dump(by_alias=True, exclude_unset=True) == input["200"]
