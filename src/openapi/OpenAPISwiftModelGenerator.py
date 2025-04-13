from typing import Any, Dict, List

from src.openapi.OpenAPISpec import OpenAPISpec
from src.utils import to_camel_case


class OpenAPISwiftModelGenerator:
    """Generates SwiftData models from OpenAPI schemas."""

    def __init__(self, schema: OpenAPISpec) -> None:
        """Initialize the Swift model generator."""
        self.schema = schema

    def _import_statements(self) -> str:
        """Returns the import statements for the SwiftData models."""
        return "\n".join(["import Foundation", "import SwiftData"])

    def _handle_simple_schema(self, schema: Dict[str, Any]) -> List[str]:
        """Handle simple schemas without object properties."""
        # Handle enums separately
        if "enum" in schema:
            return self._handle_enum_schema(schema)

        # Get the Swift type for this schema
        openapi_type = schema.get("type", "string")
        swift_type = self._openapi_type_to_swift(schema, True)

        swift_code = []
        # Add a property with the correct type
        swift_code.append(f"    var value: {swift_type}")

        # Add description as a comment if available
        if "description" in schema:
            swift_code.insert(0, f"    // {schema['description']}")

        # Add initializer with the correct type
        swift_code.append("")

        # For string types, provide an empty string default
        if openapi_type == "string":
            swift_code.append(f'    init(value: {swift_type} = "") {{')
        # For numeric types, provide a zero default
        elif openapi_type in ["integer", "number"]:
            swift_code.append(f"    init(value: {swift_type} = 0) {{")
        # For boolean, default to false
        elif openapi_type == "boolean":
            swift_code.append(f"    init(value: {swift_type} = false) {{")
        # For other types, no default
        else:
            swift_code.append(f"    init(value: {swift_type}) {{")

        swift_code.append("        self.value = value")
        swift_code.append("    }")

        return swift_code

    def _handle_enum_schema(self, schema: Dict[str, Any]) -> List[str]:
        """Generate Swift code for an enum schema."""
        swift_code = []

        # Get the base type of the enum
        base_type = schema.get("type", "string")

        # Add description as a comment if available
        if "description" in schema:
            swift_code.append(f"// {schema['description']}")

        # For string enums, we create a proper Swift enum
        if base_type == "string":
            # Create a Swift enum with String raw value and Codable conformance
            swift_code.append("enum Value: String, Codable {")

            # Add enum cases
            for value in schema["enum"]:
                # Handle values with spaces or special characters for case name
                # First convert to camelCase for the case name
                case_name = to_camel_case(value)

                # Remove spaces and special characters to ensure a valid Swift identifier
                case_name = "".join(c for c in case_name if c.isalnum())

                # Ensure case name doesn't start with a digit
                if case_name and case_name[0].isdigit():
                    case_name = "value" + case_name

                # Handle empty case name (if original value was just special chars)
                if not case_name:
                    case_name = f"value{len(swift_code)}"  # Use index as fallback

                swift_code.append(f'    case {case_name} = "{value}"')

            swift_code.append("}")

        # For numeric or boolean enums, we still need to use a typealias approach
        # since Swift enums can't have raw values of arbitrary numbers
        else:
            swift_base_type = self._openapi_type_to_swift(schema, True)
            swift_code.append(f"typealias Value = {swift_base_type}")
            swift_code.append("")

            # Add static constants for each enum value
            for value in schema["enum"]:
                # Create a constant name (prefix with type for clarity)
                const_name = f"{base_type}_{value}".upper()
                # Remove any spaces or special characters from constant name
                const_name = "".join(c for c in const_name if c.isalnum() or c == "_")
                swift_code.append(f"let {const_name}: {swift_base_type} = {value}")

        return swift_code

    def _handle_array_schema(self, schema: Dict[str, Any]) -> List[str]:
        """Handle array type schemas."""
        # Get the item type from the array schema
        item_schema = schema["items"]
        item_type = "Any"

        # Handle reference to another schema
        if "$ref" in item_schema:
            ref = item_schema["$ref"]
            if ref.startswith("#/components/schemas/"):
                item_type = ref.split("/")[-1]
        # Handle inline type definition
        elif "type" in item_schema:
            item_type = self._openapi_type_to_swift(item_schema, True)

        # Add array property
        swift_code = []
        swift_code.append(f"    var items: [{item_type}]")

        # Add initializer
        swift_code.append("")
        swift_code.append(f"    init(items: [{item_type}]) {{")
        swift_code.append("        self.items = items")
        swift_code.append("    }")

        return swift_code

    def _snake_to_camel_case(self, snake_case: str) -> str:
        """Convert snake_case to camelCase."""
        components = snake_case.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    def _generate_coding_keys(self, properties: Dict[str, Any]) -> List[str]:
        """Generate CodingKeys enum for a DTO."""
        swift_code = []
        swift_code.append("    enum CodingKeys: String, CodingKey {")

        # Group properties that don't need custom mapping
        standard_props = []
        custom_props = []

        for prop_name in properties.keys():
            swift_prop_name = to_camel_case(prop_name)

            # Check if property name needs remapping (snake_case to camelCase)
            if prop_name == swift_prop_name or prop_name == swift_prop_name.lower():
                standard_props.append(swift_prop_name)
            else:
                custom_props.append((swift_prop_name, prop_name))

        # Add standard properties first if any
        if standard_props:
            swift_code.append(f"        case {', '.join(standard_props)}")

        # Add custom mappings
        for swift_name, original_name in custom_props:
            swift_code.append(f'        case {swift_name} = "{original_name}"')

        swift_code.append("    }")

        return swift_code

    def _handle_object_schema(self, schema: Dict[str, Any]) -> List[str]:
        """
        Handle object type schemas.

        Args:
            schema: The OpenAPI schema
            swift_code: The list of Swift code lines being built
            required_props: List of required property names
        """
        required_props = schema.get("required", [])
        properties = schema.get("properties", {})

        swift_code = []

        # Keep track of renamed properties
        renamed_props = {}

        # Swift reserved keywords that need to be renamed
        swift_reserved_keywords = {
            "description": "descriptionText",
            "class": "classType",
            "import": "importSource",
            "public": "publicFlag",
            "private": "privateFlag",
            "internal": "internalFlag",
            "protocol": "protocolType",
            "struct": "structType",
            "enum": "enumType",
            "extension": "extensionType",
            "func": "function",
            "var": "variable",
            "let": "constant",
            "init": "initialize",
            "self": "selfValue",
            "super": "superValue",
            "true": "trueValue",
            "false": "falseValue",
            "type": "typeValue",
            "associatedtype": "associatedTypeValue",
            "operator": "operatorValue",
            "return": "returnValue",
            "default": "defaultValue",
        }

        # First add property declarations
        for prop_name, prop_schema in properties.items():
            swift_type = self._openapi_type_to_swift(prop_schema, prop_name in required_props)
            swift_prop_name = to_camel_case(prop_name)

            # Handle reserved Swift keywords
            if swift_prop_name in swift_reserved_keywords:
                renamed_props[swift_prop_name] = swift_reserved_keywords[swift_prop_name]
                swift_prop_name = swift_reserved_keywords[swift_prop_name]

            # Check if this property should be unique (using x-unique-key extension)
            is_unique = prop_schema.get("x-unique-key", False)

            # Add property with appropriate attributes
            if is_unique:
                swift_code.append(f"    @Attribute(.unique) var {swift_prop_name}: {swift_type}")
            else:
                swift_code.append(f"    var {swift_prop_name}: {swift_type}")

        # Add initializer
        swift_code.append("")
        swift_code.append("    init(")

        # Add initializer parameters
        init_params = []
        for prop_name, prop_schema in properties.items():
            swift_type = self._openapi_type_to_swift(prop_schema, prop_name in required_props)
            swift_prop_name = to_camel_case(prop_name)
            param_name = swift_prop_name

            # Handle reserved Swift keywords
            if swift_prop_name in renamed_props:
                param_name = renamed_props[swift_prop_name]

            # Optional properties get default value of nil
            if prop_name not in required_props and "?" in swift_type:
                init_params.append(f"{param_name}: {swift_type} = nil")
            else:
                init_params.append(f"{param_name}: {swift_type}")

        swift_code.append("        " + ",\n        ".join(init_params))
        swift_code.append("    ) {")

        # Add property assignments
        for prop_name in properties.keys():
            swift_prop_name = to_camel_case(prop_name)

            # Handle reserved Swift keywords
            if swift_prop_name in renamed_props:
                renamed_prop = renamed_props[swift_prop_name]
                swift_code.append(f"        self.{renamed_prop} = {renamed_prop}")
            else:
                swift_code.append(f"        self.{swift_prop_name} = {swift_prop_name}")

        swift_code.append("    }")

        return swift_code

    def _generate_dto_struct(self, schema_name: str, schema: Dict[str, Any]) -> str:
        """
        Generate a Swift DTO struct for an object schema.

        Args:
            schema_name: Name of the schema
            schema: The OpenAPI schema

        Returns:
            Swift code for a DTO struct
        """
        dto_name = f"{schema_name}DTO"
        required_props = schema.get("required", [])
        properties = schema.get("properties", {})

        swift_code = [f"struct {dto_name}: Codable, Hashable, Identifiable {{"]

        # Add properties
        for prop_name, prop_schema in properties.items():
            swift_type = self._openapi_type_to_swift(prop_schema, prop_name in required_props)
            swift_prop_name = to_camel_case(prop_name)

            # Use 'let' for all DTO properties
            swift_code.append(f"    let {swift_prop_name}: {swift_type}")

        # Add CodingKeys if we have properties with snake_case that need to be mapped
        has_snake_case = any("_" in prop_name for prop_name in properties.keys())
        if has_snake_case:
            swift_code.append("")
            swift_code.extend(self._generate_coding_keys(properties))

        # Close the struct
        swift_code.append("}")

        return "\n".join(swift_code)

    def _generate_model_with_dto_conveniences(self, schema_name: str, schema: Dict[str, Any]) -> str:
        """
        Generate a SwiftData model with convenience methods for working with DTOs.

        Args:
            schema_name: Name of the schema
            schema: The OpenAPI schema

        Returns:
            Swift code for a SwiftData model with DTO convenience methods
        """
        required_props = schema.get("required", [])
        properties = schema.get("properties", {})
        dto_name = f"{schema_name}DTO"

        # Start building the Swift class
        swift_code = ["@Model"]
        swift_code.append(f"final class {schema_name} {{")

        # Keep track of renamed properties
        renamed_props = {}

        # Swift reserved keywords that need to be renamed
        swift_reserved_keywords = {
            "description": "descriptionText",
            "class": "classType",
            "import": "importSource",
            "public": "publicFlag",
            "private": "privateFlag",
            "internal": "internalFlag",
            "protocol": "protocolType",
            "struct": "structType",
            "enum": "enumType",
            "extension": "extensionType",
            "func": "function",
            "var": "variable",
            "let": "constant",
            "init": "initialize",
            "self": "selfValue",
            "super": "superValue",
            "true": "trueValue",
            "false": "falseValue",
            "type": "typeValue",
            "associatedtype": "associatedTypeValue",
            "operator": "operatorValue",
            "return": "returnValue",
            "default": "defaultValue",
        }

        # Add property declarations
        for prop_name, prop_schema in properties.items():
            swift_type = self._openapi_type_to_swift(prop_schema, prop_name in required_props)
            swift_prop_name = to_camel_case(prop_name)

            # Handle reserved Swift keywords
            if swift_prop_name in swift_reserved_keywords:
                renamed_props[swift_prop_name] = swift_reserved_keywords[swift_prop_name]
                swift_prop_name = swift_reserved_keywords[swift_prop_name]

            # Check if this property should be unique (using x-unique-key extension)
            is_unique = prop_schema.get("x-unique-key", False) or prop_name == "id"

            # Add property with appropriate attributes
            if is_unique:
                swift_code.append(f"    @Attribute(.unique) var {swift_prop_name}: {swift_type}")
            else:
                swift_code.append(f"    var {swift_prop_name}: {swift_type}")

        # Add standard initializer
        swift_code.append("")
        swift_code.append("    init(")

        # Add initializer parameters
        init_params = []
        for prop_name, prop_schema in properties.items():
            swift_type = self._openapi_type_to_swift(prop_schema, prop_name in required_props)
            swift_prop_name = to_camel_case(prop_name)
            param_name = swift_prop_name

            # Handle reserved Swift keywords
            if swift_prop_name in renamed_props:
                param_name = renamed_props[swift_prop_name]

            # Optional properties get default value of nil
            if prop_name not in required_props and "?" in swift_type:
                init_params.append(f"{param_name}: {swift_type} = nil")
            else:
                init_params.append(f"{param_name}: {swift_type}")

        swift_code.append("        " + ",\n        ".join(init_params))
        swift_code.append("    ) {")

        # Add property assignments
        for prop_name in properties.keys():
            swift_prop_name = to_camel_case(prop_name)

            # Handle reserved Swift keywords
            if swift_prop_name in renamed_props:
                renamed_prop = renamed_props[swift_prop_name]
                swift_code.append(f"        self.{renamed_prop} = {renamed_prop}")
            else:
                swift_code.append(f"        self.{swift_prop_name} = {swift_prop_name}")

        swift_code.append("    }")

        # Add convenience initializer from DTO
        swift_code.append("")
        swift_code.append(f"    convenience init(item: {dto_name}) {{")
        swift_code.append("        self.init(")

        # Add parameter mappings from DTO to model
        dto_params = []
        for prop_name in properties.keys():
            swift_prop_name = to_camel_case(prop_name)
            param_name = swift_prop_name

            # Handle reserved Swift keywords
            if swift_prop_name in renamed_props:
                param_name = renamed_props[swift_prop_name]

            dto_params.append(f"{param_name}: item.{swift_prop_name}")

        swift_code.append("            " + ",\n            ".join(dto_params))
        swift_code.append("        )")
        swift_code.append("    }")

        # Add update method from DTO
        swift_code.append("")
        swift_code.append(f"    func update(fromDTO dto: {dto_name}) {{")

        # Add property assignments from DTO
        for prop_name in properties.keys():
            swift_prop_name = to_camel_case(prop_name)

            # Handle reserved Swift keywords
            if swift_prop_name in renamed_props:
                renamed_prop = renamed_props[swift_prop_name]
                swift_code.append(f"        self.{renamed_prop} = dto.{swift_prop_name}")
            else:
                swift_code.append(f"        self.{swift_prop_name} = dto.{swift_prop_name}")

        swift_code.append("    }")

        # Close the class
        swift_code.append("}")

        return "\n".join(swift_code)

    def generate_model(self, schema_name: str) -> str:
        """
        Generates SwiftData model code from an OpenAPI schema.

        Args:
            schema_name (str): The name of the schema/model
            schema (Dict[str, Any]): The OpenAPI schema definition

        Returns:
            str: Swift code for a SwiftData model
        """
        schema = self.schema.get_schema(schema_name)
        if schema is None:
            raise ValueError(f"Schema {schema_name} not found")

        # Handle enums separately - they should not be SwiftData models
        if "enum" in schema:
            enum_code = self._handle_enum_schema(schema)
            # Replace "Value" with the actual schema name in the enum definition
            enum_code = [
                line.replace("enum Value", f"enum {schema_name}") if "enum Value" in line else line for line in enum_code
            ]
            enum_code = [
                line.replace("typealias Value", f"typealias {schema_name}") if "typealias Value" in line else line
                for line in enum_code
            ]
            return "\n".join(enum_code)

        # For object types, generate both a DTO and a SwiftData model
        if schema.get("type") == "object" and "properties" in schema:
            dto_code = self._generate_dto_struct(schema_name, schema)
            model_code = self._generate_model_with_dto_conveniences(schema_name, schema)
            return f"{dto_code}\n\n{model_code}"

        # For array types, use the existing array schema handler
        if schema.get("type") == "array" and "items" in schema:
            swift_code = ["@Model"]
            swift_code.append(f"final class {schema_name} {{")
            swift_code.extend(self._handle_array_schema(schema))
            swift_code.append("}")
            return "\n".join(swift_code)

        # For simple types, use the existing simple schema handler
        swift_code = ["@Model"]
        swift_code.append(f"final class {schema_name} {{")
        swift_code.extend(self._handle_simple_schema(schema))
        swift_code.append("}")
        return "\n".join(swift_code)

    def _openapi_type_to_swift(self, prop_schema: Dict[str, Any], is_required: bool) -> str:
        """
        Converts an OpenAPI property type to a Swift type.

        Args:
            prop_schema (Dict[str, Any]): The OpenAPI property schema
            is_required (bool): Whether the property is required

        Returns:
            str: The corresponding Swift type
        """
        # Handle anyOf with schema reference and null
        if "anyOf" in prop_schema:
            # Look for a schema reference in the anyOf array
            ref_type = None
            has_null = False

            for option in prop_schema["anyOf"]:
                if "$ref" in option:
                    ref = option["$ref"]
                    if ref.startswith("#/components/schemas/"):
                        ref_type = ref.split("/")[-1]
                elif option.get("type") == "null":
                    has_null = True

            # If we found a reference and null type, it's an optional reference
            if ref_type:
                # If nullable or explicitly not required, make it optional
                if has_null or not is_required:
                    return str(f"{ref_type}?")
                return str(ref_type)

        # Handle direct references to other schemas
        if "$ref" in prop_schema:
            ref = prop_schema["$ref"]
            if ref.startswith("#/components/schemas/"):
                ref_type = ref.split("/")[-1]
                return f"{ref_type}{'?' if not is_required else ''}"

        # Handle arrays
        if prop_schema.get("type") == "array" and "items" in prop_schema:
            item_type = self._openapi_type_to_swift(prop_schema["items"], True)  # Array items are always required
            return f"[{item_type}]{'?' if not is_required else ''}"

        # Handle primitive types
        type_mapping = {
            "string": "String",
            "integer": "Int",
            "number": "Double",
            "boolean": "Bool",
            "object": "Dictionary<String, Any>",  # Generic object
        }

        # Handle string formats
        format_mapping = {"date": "Date", "date-time": "Date", "uuid": "UUID", "email": "String", "uri": "URL"}

        # Get the base type
        openapi_type = prop_schema.get("type", "object")
        swift_type = type_mapping.get(openapi_type, "Any")

        # Apply format if available
        if openapi_type == "string" and "format" in prop_schema:
            format_type = prop_schema["format"]
            swift_type = format_mapping.get(format_type, swift_type)

        # Add optionality if not required
        if not is_required:
            swift_type += "?"

        return swift_type
