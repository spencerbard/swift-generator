def to_camel_case(snake_str: str) -> str:
    """
    Converts a snake_case string to camelCase.

    Args:
        snake_str (str): The snake_case string

    Returns:
        str: The camelCase string
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])
