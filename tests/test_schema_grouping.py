import json
import os

from src.openapi.OpenAPISpec import OpenAPISpec
from src.openapi.parse_openapi_to_swift import SchemasGroupedByDeps, group_schemas_by_deps


def test_group_schemas_by_deps() -> None:
    """Test that schemas are correctly grouped by their dependencies."""
    # Load the test data
    test_file_path = os.path.join(os.path.dirname(__file__), "test_data", "test_schema_grouping.json")
    with open(test_file_path, "r") as f:
        spec_dict = json.load(f)

    # Create an OpenAPISpec object
    openapi = OpenAPISpec(spec_dict=spec_dict)

    # Call the function to test
    result = group_schemas_by_deps(openapi)

    # Assertions to validate the result
    assert isinstance(result, SchemasGroupedByDeps)
    assert isinstance(result.schema_groups, dict)
    assert isinstance(result.shared_schemas, dict)

    # Verify all root schemas are accurate
    assert sorted(list(result.schema_groups.keys())) == [
        "AuthResponse",
        "CreateRecipeSourceRequest",
        "GroceryListIncomingInviteResponse",
        "GroceryListOutgoingInviteResponse",
        "GroceryListResponse",
        "HTTPValidationError",
        "InviteUserRequest",
        "RecipeResponse",
        "RecipeSourceTaskRequest",
        "RecipeUpdateRequest",
        "RefreshRequest",
        "RespondToInviteRequest",
        "SignupRequest",
    ]

    # Verify all shared schemas are accurate
    assert sorted(list(result.shared_schemas.keys())) == ["GroceryListInviteStatus", "RecipeSourceType"]

    for group_name, group_schemas in result.schema_groups.items():
        match group_name:
            case "AuthResponse":
                assert sorted(list(group_schemas.keys())) == ["AuthResponse", "SessionResponse", "UserResponse"]
            case "CreateRecipeSourceRequest":
                assert sorted(list(group_schemas.keys())) == ["CreateRecipeSourceRequest"]
            case "GroceryListIncomingInviteResponse":
                assert sorted(list(group_schemas.keys())) == ["GroceryListIncomingInviteResponse"]
            case "GroceryListOutgoingInviteResponse":
                assert sorted(list(group_schemas.keys())) == ["GroceryListOutgoingInviteResponse"]
            case "GroceryListResponse":
                assert sorted(list(group_schemas.keys())) == [
                    "GroceryItemResponse",
                    "GroceryListMemberResponse",
                    "GroceryListResponse",
                ]
            case "HTTPValidationError":
                assert sorted(list(group_schemas.keys())) == ["HTTPValidationError", "ValidationError"]
            case "InviteUserRequest":
                assert sorted(list(group_schemas.keys())) == ["InviteUserRequest"]
            case "RecipeResponse":
                assert sorted(list(group_schemas.keys())) == [
                    "CountMeasurementSchema",
                    "MealTypeEnum",
                    "OtherMeasurementSchema",
                    "RecipeIngredientResponse",
                    "RecipeIngredientSectionResponse",
                    "RecipeParsingStatus",
                    "RecipeResponse",
                    "RecipeSourceResponse",
                    "RecipeStepResponse",
                    "RecipeStepSectionResponse",
                    "RecipeVersionResponse",
                    "VolumeMeasurementSchema",
                    "VolumeUnitTypeEnum",
                    "WeightMeasurementSchema",
                    "WeightUnitTypeEnum",
                ]
            case "RecipeSourceTaskRequest":
                assert sorted(list(group_schemas.keys())) == ["RecipeSourceTaskRequest"]
            case "RecipeUpdateRequest":
                assert sorted(list(group_schemas.keys())) == ["MealType", "RecipeUpdateRequest"]
            case "RefreshRequest":
                assert sorted(list(group_schemas.keys())) == ["RefreshRequest"]
            case "RespondToInviteRequest":
                assert sorted(list(group_schemas.keys())) == ["RespondToInviteRequest"]
            case "SignupRequest":
                assert sorted(list(group_schemas.keys())) == ["SignupRequest"]
            case _:
                raise ValueError(f"Unexpected group name {group_name}")
