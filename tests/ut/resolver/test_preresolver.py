from hocon._main import parse
from hocon.resolver._preresolver import preresolve
from hocon.strings import UnquotedString
from hocon.unresolved import UnresolvedDuplicateValue, UnresolvedSubstitution, UnresolvedConcatenation


def test_pre_deduplication_1():
    data = """
        a: {a: 1}
        a: 5
        a: {b: 2}
        a: {c: 3}
        """
    parsed = parse(data)
    preresolved = preresolve(parsed)
    assert preresolved == {
        "a": UnresolvedDuplicateValue(
            [{"b": 2}, {"c": 3}]
        )
    }


def test_pre_deduplication_2():
    data = """
        a: {a: 1}
        a: {b: 2}
        a: {c: 3}
        """
    parsed = parse(data)
    preresolved = preresolve(parsed)
    assert preresolved == {
        "a": UnresolvedDuplicateValue(
            [{"a": 1}, {"b": 2}, {"c": 3}]
        )
    }


def test_pre_deduplication_3():
    data = """
        a: {a: 1}
        a: {b: 2}
        a: {c: 3}
        a: 10
        """
    parsed = parse(data)
    preresolved = preresolve(parsed)
    assert preresolved == {"a": 10}


def test_pre_deduplication_4():
    data = """
        a: {a: 1}
        a: {b: ${a.b}}
        a: {c: 3}
        """
    parsed = parse(data)
    preresolved = preresolve(parsed)
    assert preresolved == {
        "a": UnresolvedDuplicateValue(
            [
                {"a": 1},
                {"b": UnresolvedSubstitution(["a", "b"], False)},
                {"c": 3}
            ]
        )
    }


def test_pre_concatenation_1():
    data = """
            a = [1, 2] [3, 4] [
              5,
              6
            ]
            """
    parsed = parse(data)
    preresolved = preresolve(parsed)
    assert preresolved == {
        "a": [1, 2, 3, 4, 5, 6]
    }


def test_pre_concatenation_2():
    data = """
            a = {a: 1} {b:2} {c:3}
            """
    parsed = parse(data)
    preresolved = preresolve(parsed)
    assert preresolved == {
        "a": UnresolvedConcatenation([{"a": 1}, {"b": 2}, {"c": 3}])
    }


def test_pre_concatenation_3():
    data = """
            a = {a: 1} {b:${?a.a}} {c:3}
            """
    parsed = parse(data)
    preresolved = preresolve(parsed)
    assert preresolved == {
        "a": UnresolvedConcatenation([
            {"a": 1},
            {"b": UnresolvedSubstitution(["a", "a"], True)},
            {"c": 3}
        ])
    }


def test_all():
    data = """
            a = {a: 1} {b:hi ${?a.a} mom} {c:3}
            a: {a: 4} {b: 5} {c: 6}
            """
    parsed = parse(data)
    preresolved = preresolve(parsed)
    expected = {
        "a": UnresolvedDuplicateValue([
            UnresolvedConcatenation([
                {"a": 1},
                {"b": UnresolvedConcatenation([
                    UnquotedString("hi"),
                    UnquotedString(" "),
                    UnresolvedSubstitution(["a", "a"], True),
                    UnquotedString(" "),
                    UnquotedString("mom")
                ])},
                {"c": 3}
            ]),
            UnresolvedConcatenation([
                {"a": 4},
                {"b": 5},
                {"c": 6}
            ])
        ])
    }
    assert preresolved == expected
