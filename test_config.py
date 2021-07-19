from jsonParser import JsonParser
from dataclasses import dataclass, field


@dataclass
class InnerTestConfig(JsonParser):
    """A test dataclass with sample fields ment to be used inside collection fields of bigger test class"""
    str_field: str
    int_field: int
    optional_list_int_field: list[int] = field(default_factory=list)


@dataclass
class TestConfig(JsonParser):
    """A test dataclass with different sample fields"""
    str_field: str
    int_field: int
    list_str_field: list[str]
    dict_str_str_field: dict[str, str]
    inner_config_field: InnerTestConfig
    list_inner_config_field: list[InnerTestConfig]
    dict_inner_config_field: dict[str, InnerTestConfig]
    list_list_int_field: list[list[int]]
