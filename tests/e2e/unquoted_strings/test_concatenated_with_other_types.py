"""
truefoo parses as the boolean token true followed by the unquoted string foo.
However, footrue parses as the unquoted string footrue.
Similarly, 10.0bar is the number 10.0 then the unquoted string bar but bar10.0 is the unquoted string bar10.0.
(In practice, this distinction doesn't matter much because of value concatenation)
"""
import hocon
import pytest


pytestmark = [pytest.mark.f8, pytest.mark.f10]


@pytest.mark.parametrize("data, expected", [
    ("[truefoo]", [True]),
    ("[footrue]", ["footrue"]),
    ("[10.0bar]", ["10.0bar"]),
    ("[bar10.0]", ["bar10.0"])
])
def test_concatenation_with_other_types(data: str, expected: list):
    assert hocon.loads(data) == expected
