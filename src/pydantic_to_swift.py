from pydantic import BaseModel

PYTHON_TO_SWIFT_TYPES = {int: "Int", float: "Double", str: "String", bool: "Bool", list: "Array", dict: "Dictionary"}


def generate_swiftdata_model(pydantic_model: type[BaseModel]) -> str:
    """Generate a SwiftData model from a Pydantic model."""
    model_name = pydantic_model.__name__
    fields = pydantic_model.model_fields

    swift_model = f"import SwiftData\n\n@Model\nclass {model_name} {{\n"

    for field_name, field_info in fields.items():
        print(field_info.annotation)
    #     field_type = field_info.annotation
    #     swift_type = PYTHON_TO_SWIFT_TYPES.get(field_type, "Any")

    #     if getattr(field_type, "__origin__", None) is Optional:
    #         swift_type = f"{PYTHON_TO_SWIFT_TYPES.get(field_type.__args__[0], 'Any')}?"

    #     elif getattr(field_type, "__origin__", None) is list:
    #         item_type = field_type.__args__[0] if field_type.__args__ else "Any"
    #         swift_type = f"[{PYTHON_TO_SWIFT_TYPES.get(item_type, 'Any')}]"

    #     default_value = field_info.default if field_info.default is not None else None
    #     default_str = f" = {repr(default_value)}" if default_value is not None else ""

    #     attribute_prefix = "@Attribute(.primaryKey) " if field_name == "id" else ""

    #     swift_model += (
    #         f"    {attribute_prefix}var {field_name}: {swift_type}{default_str}\n"
    #     )

    # init_params = ", ".join(
    #     f"{field_name}: {PYTHON_TO_SWIFT_TYPES.get(field_info.annotation, 'Any')}"
    #     for field_name, field_info in fields.items()
    # )
    # init_body = "\n        ".join(
    #     f"self.{field_name} = {field_name}" for field_name in fields
    # )

    # swift_model += f"\n    init({init_params}) {{\n        {init_body}\n    }}\n"
    # swift_model += "}"

    # return swift_model
    return ""
