from __future__ import annotations

from abc import ABC
from dataclasses import _MISSING_TYPE, Field, dataclass, fields
from typing import get_args, get_origin, TypeVar, Optional, Union, Callable, Any

JsonParserSubclass = TypeVar('JsonParserSubclass', bound='JsonParser')


def is_required(field: Field) -> bool:
    """
    Check if the field of a dataclass is required.
    """
    default_value_missing: bool = type(field.default) == _MISSING_TYPE
    default_factory_missing: bool = type(field.default_factory) == _MISSING_TYPE
    return not is_optional(field) and default_factory_missing and default_value_missing


def clear_union(input_type: type) -> type:
    """Removes unions from the type."""
    while get_origin(input_type) == Union:
        input_type = get_args(input_type)[0]
    return input_type


def is_list(field: Field) -> bool:
    """Check if the field of a dataclass is a list."""
    return get_origin(clear_union(field.type)) is list


def is_dict(field: Field) -> bool:
    """Check if the field of a dataclass is a dict."""
    return get_origin(clear_union(field.type)) is dict


def is_optional(field: Field) -> bool:
    """Check if the field is of Optional[type] (Union[type, None]) type."""
    return type(None) in get_args(field.type)


def is_json_parser_subclass(field: Field) -> bool:
    """Check if the field type is directly a subclass of JsonParser, can be optional."""
    return get_origin(clear_union(field.type)) is None and issubclass(clear_union(field.type), JsonParser)


def get_inner_type(composite_type: type) -> Optional[type]:
    """
    Extract type of an item from collection:
    list[int] -> int
    dict[str, int] -> int
    int -> None
    dict[str, list[dict[int, list[list[float]]]]] -> float
    """
    origins = {list, dict, Union}
    if get_origin(composite_type) not in origins:
        return

    while get_origin(composite_type) in origins:
        args = [arg for arg in get_args(composite_type) if not issubclass(arg, type(None))]
        composite_type = args[-1] if args else None
    return composite_type


def contains_json_parser(field: Field) -> bool:
    """Checks if the field of a dataclass contains objects of JsonParser type."""
    return issubclass(get_inner_type(field.type), JsonParser)


class ParsingStrategies:
    """Class containing methods for parsing json depending on what type currently parsed field is."""

    @classmethod
    def get_parsing_method(cls, field: Field) -> Callable[[Field, dict], Any]:
        """Determines what parsing method to choose for given field and returns it."""
        if is_list(field) and contains_json_parser(field):
            return cls.parse_json_parser_list

        if is_dict(field) and contains_json_parser(field):
            return cls.parse_json_parser_dict

        # in case types like list[str] that cause error in issubclass
        if is_json_parser_subclass(field):
            return cls.parse_json_parser_object

        return cls.parse_base_type

    @staticmethod
    def parse_json_parser_list(field: Field, json: dict) -> list[JsonParserSubclass]:
        """Parse a list of JsonParser objects."""
        # TODO: type detecting is recursive but parsing is not
        inner_type: type = get_inner_type(field.type)
        return [inner_type.from_json(item) for item in json[field.name]]

    @staticmethod
    def parse_json_parser_dict(field: Field, json: dict) -> dict[Union[str, int], JsonParserSubclass]:
        """Parse a dict of JsonParser objects."""
        # TODO: type detecting is recursive but parsing is not
        inner_type: type = get_inner_type(field.type)
        return {key: inner_type.from_json(value) for key, value in json[field.name].items()}

    @staticmethod
    def parse_json_parser_object(field: Field, json: dict) -> JsonParserSubclass:
        """Parse a JsonParser object"""
        return clear_union(field.type).from_json(json[field.name])

    @staticmethod
    def parse_base_type(field: Field, json: dict):
        """Parse a type that is neither JsonParser nor a collection containing it"""
        return json[field.name]



@dataclass
class JsonParser(ABC):
    """
    Abstract class made to be inherited by dataclasses.
    It uses the dataclass fields to determine a needed structure of json file and parse it.
    """

    @classmethod
    def from_json(cls, json: dict) -> Optional[JsonParserSubclass]:
        """
        Parses json string and returns an instance of the class.
        The required fields are defined as those that have no default value or default factory.
        If a required field is missing from json string KeyError will be thrown.
        """
        initializer: dict = {}

        field: Field
        for field in fields(cls):
            if is_optional(field) and field.name not in json:
                initializer[field.name] = None
                continue

            if field.name not in json and is_required(field):
                raise KeyError(f"Json passed to {cls.__name__} does not contain required key: \"{field.name}\"")

            if field.name not in json and not is_optional(field):
                continue

            initializer[field.name] = ParsingStrategies.get_parsing_method(field)(field, json)
        return cls(**initializer)
