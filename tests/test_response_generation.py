import os

from src.openapi.OpenAPISpec import OpenAPISpec
from src.openapi.OpenAPISwiftModelGenerator import OpenAPISwiftModelGenerator
from src.openapi.parse_openapi_to_swift import parse_openapi_to_swift


def test_response_categorization(tmp_path: str) -> None:
    """
    Test that RecipeResponse is correctly categorized as a response model
    and placed in the Responses directory.
    """
    # Process the schema
    swift_models = parse_openapi_to_swift(filepath="tests/test_data/test_response_generation.json")

    # Verify that RecipeResponse was recognized as a response
    assert "RecipeResponse" in swift_models
    assert swift_models["RecipeResponse"]["type"] == "root"

    # Write the models to files
    output_dir = os.path.join(tmp_path, "Generated")
    from src.openapi.parse_openapi_to_swift import write_swift_files

    write_swift_files(swift_models, output_dir)

    # Check that RecipeResponse.swift exists in the Responses directory
    response_file_path = os.path.join(output_dir, "Root", "RecipeResponse.swift")
    assert os.path.exists(response_file_path)

    # Verify the file content
    with open(response_file_path, "r") as f:
        response_file_content = f.read()

    print(response_file_content)

    # Check for important parts of the model
    assert "struct RecipeResponseDTO: Codable, Hashable, Identifiable {" in response_file_content
    assert "final class RecipeResponse {" in response_file_content

    assert "struct RecipeSourceResponseDTO: Codable, Hashable, Identifiable {" in response_file_content
    assert "final class RecipeSourceResponse {" in response_file_content

    assert not os.path.exists(os.path.join(output_dir, "Nested", "RecipeSourceResponse.swift"))


def test_recipe_step_response_generation(tmp_path: str) -> None:
    """
    Test that RecipeStepResponse is correctly categorized as a response model
    and placed in the Responses directory.
    """

    openapi = OpenAPISpec(filepath="tests/test_data/test_response_generation.json")
    swift_model_generator = OpenAPISwiftModelGenerator(openapi)
    swift_model_code_str = swift_model_generator.generate_model("RecipeStepResponse")
    assert "final class RecipeStepResponse {" in swift_model_code_str
    assert "var order: Int" in swift_model_code_str
    assert "var descriptionText: String" in swift_model_code_str
    assert "var title: String?" in swift_model_code_str
    assert "var notes: String?" in swift_model_code_str
    assert "var imageUrls: [String]?" in swift_model_code_str
    assert "var originalText: String?" in swift_model_code_str
    assert "@Attribute(.unique) var id: String" in swift_model_code_str
