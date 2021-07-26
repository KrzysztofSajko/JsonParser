from test_config import TestConfig
from json import load
from dataclasses import fields, Field
from jsonParser import JsonParser, get_inner_type, clear_union, get_origin


def test_types():
    for f in fields(TestConfig):
        print(f"{f.name}:")
        print(f"\traw type: {f.type}")
        print(f"\tunion cleared type: {clear_union(f.type)}")
        print(f"\torigin: {get_origin(f.type)}")
        print(f"\tjson parser subclass: {get_origin(clear_union(f.type)) is None and issubclass(clear_union(f.type), JsonParser)}")

def test_parsing_sample_config():
    with open("sample_config.json", encoding="UTF-8") as json_file:
        config_json: dict = load(json_file)
    try:
        config: TestConfig = TestConfig.from_json(config_json)
    except KeyError as e:
        raise SystemExit(f"Error when handling config file: {e}") from e
    field: Field
    for field in fields(config):
        print(f"{field.name}: {config.__dict__[field.name]}")


def main() -> None:
    test_parsing_sample_config()
    # test_types()


if __name__ == '__main__':
    main()
