from test_config import TestConfig
from json import load
from dataclasses import fields, Field


def main() -> None:
    with open("sample_config.json", encoding="UTF-8") as json_file:
        config_json: dict = load(json_file)
    try:
        config: TestConfig = TestConfig.from_json(config_json)
    except KeyError as e:
        raise SystemExit(f"Error when handling config file: {e}") from e
    field: Field
    for field in fields(config):
        print(f"{field.name}: {config.__dict__[field.name]}")


if __name__ == '__main__':
    main()
