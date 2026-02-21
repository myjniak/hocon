from pathlib import Path

from hocon import loads


def test_2_includes_relative_to_cwd():
    conf_filepath = Path(__file__).parent / "data" / "main.conf"
    result = loads(conf_filepath.read_text(), encoding="UTF-8")
    assert result == {"house": {"location": "서울 Nice street 42", "city": "서울"}}
