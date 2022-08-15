from pydantic_avro.avro_to_pydantic import avsc_to_pydantic, generate_imports


def test_generate_imports():
    unique_types = {"Optional", "float", "datetime", "date", "int", "List", "Dict", "UUID"}

    all_imports = generate_imports(unique_types)

    assert all_imports[0] == "from datetime import date, datetime"
    assert all_imports[1] == "from typing import Dict, List, Optional"
    assert all_imports[2] == "from uuid import UUID"


def test_avsc_to_pydantic_empty():
    pydantic_code = avsc_to_pydantic({"name": "Test", "type": "record", "fields": []})
    assert "class Test(BaseModel):\n    pass" in pydantic_code


def test_avsc_to_pydantic_primitive():
    pydantic_code = avsc_to_pydantic(
        {
            "name": "Test",
            "type": "record",
            "fields": [
                {"name": "col1", "type": "string"},
                {"name": "col2", "type": "int"},
                {"name": "col3", "type": "long"},
                {"name": "col4", "type": "double"},
                {"name": "col5", "type": "float"},
                {"name": "col6", "type": "boolean"},
            ],
        }
    )
    assert (
        "class Test(BaseModel):\n"
        "    col1: str\n"
        "    col2: int\n"
        "    col3: int\n"
        "    col4: float\n"
        "    col5: float\n"
        "    col6: bool" in pydantic_code
    )


def test_avsc_to_pydantic_map():
    pydantic_code = avsc_to_pydantic(
        {
            "name": "Test",
            "type": "record",
            "fields": [
                {"name": "col1", "type": {"type": "map", "values": "string", "default": {}}},
            ],
        }
    )
    assert "class Test(BaseModel):\n" "    col1: Dict[str, str]" in pydantic_code


def test_avsc_to_pydantic_map_nested_object():
    pydantic_code = avsc_to_pydantic(
        {
            "name": "Test",
            "type": "record",
            "fields": [
                {
                    "name": "col1",
                    "type": {
                        "type": "map",
                        "values": {"type": "record", "name": "Nested", "fields": [{"name": "col1", "type": "string"}]},
                        "default": {},
                    },
                },
            ],
        }
    )
    assert "class Test(BaseModel):\n" "    col1: Dict[str, Nested]" in pydantic_code
    assert "class Nested(BaseModel):\n" "    col1: str" in pydantic_code


def test_avsc_to_pydantic_map_nested_array():
    pydantic_code = avsc_to_pydantic(
        {
            "name": "Test",
            "type": "record",
            "fields": [
                {
                    "name": "col1",
                    "type": {
                        "type": "map",
                        "values": {
                            "type": "array",
                            "items": "string",
                        },
                        "default": {},
                    },
                },
            ],
        }
    )
    assert "class Test(BaseModel):\n" "    col1: Dict[str, List[str]]" in pydantic_code


def test_avsc_to_pydantic_logical():
    pydantic_code = avsc_to_pydantic(
        {
            "name": "Test",
            "type": "record",
            "fields": [
                {
                    "name": "col1",
                    "type": {"type": "int", "logicalType": "date"},
                },
                {
                    "name": "col2",
                    "type": {"type": "long", "logicalType": "time-micros"},
                },
                {
                    "name": "col3",
                    "type": {"type": "long", "logicalType": "time-millis"},
                },
                {
                    "name": "col4",
                    "type": {"type": "long", "logicalType": "timestamp-micros"},
                },
                {
                    "name": "col5",
                    "type": {"type": "long", "logicalType": "timestamp-millis"},
                },
            ],
        }
    )
    assert (
        "class Test(BaseModel):\n"
        "    col1: date\n"
        "    col2: time\n"
        "    col3: time\n"
        "    col4: datetime\n"
        "    col5: datetime" in pydantic_code
    )


def test_avsc_to_pydantic_complex():
    pydantic_code = avsc_to_pydantic(
        {
            "name": "Test",
            "type": "record",
            "fields": [
                {
                    "name": "col1",
                    "type": {
                        "name": "Nested",
                        "type": "record",
                        "fields": [],
                    },
                },
                {
                    "name": "col2",
                    "type": {
                        "type": "array",
                        "items": "int",
                    },
                },
                {
                    "name": "col3",
                    "type": {
                        "type": "array",
                        "items": "Nested",
                    },
                },
            ],
        }
    )
    assert (
        "class Test(BaseModel):\n"
        "    col1: Nested\n"
        "    col2: List[int]\n"
        "    col3: List[Nested]\n" in pydantic_code
    )

    assert "class Nested(BaseModel):\n    pass\n" in pydantic_code


def test_default():
    pydantic_code = avsc_to_pydantic(
        {
            "name": "Test",
            "type": "record",
            "fields": [
                {"name": "col1", "type": "string", "default": "test"},
                {"name": "col2", "type": ["string", "null"], "default": None},
                {"name": "col3", "type": {"type": "map", "values": "string"}, "default": {"key": "value"}},
                {"name": "col4", "type": "boolean", "default": True},
                {"name": "col5", "type": "boolean", "default": False},
            ],
        }
    )
    assert (
        "class Test(BaseModel):\n"
        '    col1: str = "test"\n'
        "    col2: Optional[str] = None\n"
        '    col3: Dict[str, str] = {"key": "value"}\n'
        "    col4: bool = True\n"
        "    col5: bool = False\n" in pydantic_code
    )
