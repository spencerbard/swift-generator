from pydantic import BaseModel
from src.pydantic_to_swift import generate_swiftdata_model


class User(BaseModel):
    id: int
    name: str
    email: str | None = None
    age: int = 18
    scores: list[float]


def test_generate_swiftdata_model() -> None:
    swift_model = generate_swiftdata_model(User)
    # assert "class User" in swift_model
    # assert "@Model" in swift_model
    # assert "var id: Int" in swift_model
    # assert "var email: String?" in swift_model
