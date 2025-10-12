from pathlib import Path

from hocon import load


def test_1():
    conf_filepath = Path(__file__).parent / "data" / "main.conf"
    result = load(open(conf_filepath, encoding="UTF-8"))
    assert result == {"house": {"location": "서울 Nice street 42", "city": "서울"}}