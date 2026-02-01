import json
import string
import pytest
from hypothesis import given, strategies, settings, Phase

from hocon import loads
from hocon.constants import UNQUOTED_STR_FORBIDDEN_CHARS, WHITE_CHARS
from hocon.exceptions import HOCONError

WHITESPACE = strategies.text(WHITE_CHARS, min_size=0, max_size=3)
UNQUOTED_KEY_CHARS = string.ascii_letters + string.digits + "_-"


@strategies.composite
def hocon_key(draw):
    result = draw(
        strategies.text(
            UNQUOTED_KEY_CHARS,
            min_size=1,
            max_size=10,
        )
    )
    if "include" in result:
        result = result.replace("include", '"include"')
    result = result.replace(r"//", "bb")
    return result


@strategies.composite
def hocon_string(draw):
    result = draw(
        strategies.text(
            alphabet=strategies.characters(
                blacklist_categories=["Cs"],
                blacklist_characters=list(UNQUOTED_STR_FORBIDDEN_CHARS) + list(WHITE_CHARS),
            ),
            min_size=1,
            max_size=20,
        )
    )
    result = result.replace(r"//", "bb")
    return result


def hocon_number():
    return strategies.one_of(
        strategies.integers(min_value=-1000, max_value=1000).map(str),
        strategies.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False,
        ).map(lambda f: repr(round(f, 4))),
    )


def hocon_scalar():
    return strategies.one_of(
        hocon_string(),
        hocon_number(),
        strategies.sampled_from(["true", "false", "null"]),
    )


@strategies.composite
def hocon_array(draw, depth):
    ws = draw(WHITESPACE)
    values = draw(
        strategies.lists(
            hocon_value(depth + 1),
            min_size=0,
            max_size=4,
        )
    )
    sep = draw(strategies.sampled_from([",", "\n"]))
    inner = sep.join(values)
    return f"[{ws}{inner}{ws}]"


@strategies.composite
def hocon_object(draw, depth):
    ws = draw(WHITESPACE)
    entries = []

    for _ in range(draw(strategies.integers(min_value=0, max_value=4))):
        key = draw(hocon_key())
        val = draw(hocon_value(depth + 1))
        sep = draw(strategies.sampled_from(["=", ":"]))
        spacing = draw(WHITESPACE)
        entries.append(f"{key}{spacing}{sep}{spacing}{val}")

    entry_sep = draw(strategies.sampled_from([",", "\n"]))
    body = entry_sep.join(entries)
    return f"{{{ws}{body}{ws}}}"


@strategies.composite
def hocon_value(draw, depth=0):
    if depth > 3:
        return draw(hocon_scalar())

    return draw(
        strategies.one_of(
            hocon_scalar(),
            hocon_array(depth),
            hocon_object(depth),
        )
    )


@strategies.composite
def hocon_document(draw):
    """
    Root-level HOCON object *without* braces is legal.
    """
    entries = []

    for _ in range(draw(strategies.integers(min_value=1, max_value=5))):
        key = draw(hocon_key())
        val = draw(hocon_value())
        sep = draw(strategies.sampled_from(["=", ":"]))
        spacing = draw(WHITESPACE)
        entries.append(f"{key}{spacing}{sep}{spacing}{val}")
    entry_sep = draw(strategies.sampled_from(["\n", "\n\n"]))
    return entry_sep.join(entries)


@pytest.mark.skip(reason="Undeterministic tests, for local execution only.")
@given(hocon_document())
@settings(max_examples=10000, phases=[Phase.generate])
def test_with_hypothesis(doc):
    try:
        result = loads(doc)
    except HOCONError:
        print(doc)
        raise
    print(json.dumps(result, indent=4))
    print("_______________________________________________________")
