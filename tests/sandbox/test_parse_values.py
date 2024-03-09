from hocon._parser import parse_dict_value


def test_1():
    value, _ = parse_dict_value("{c: 3} {d: 4},}", idx=0)
    assert value == {"c": 3, "d": 4}
