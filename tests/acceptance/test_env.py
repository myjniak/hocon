import pytest

import hocon
from tests.utils import set_env

pytestmark = pytest.mark.f13


def test_resolvable_nested_substitutions_should_ignore_env():
    data = """    
    a: 1
    b: ${a}
    c: ${b}
    d: ${c}
    e: ${f}
    """
    with set_env(a="Ignore me!", b="Ignore me!", c="Ignore me!", d="Ignore me!", f="Don't ignore me!"):
        result = hocon.loads(data)
    assert result == {
        "a": 1,
        "b": 1,
        "c": 1,
        "d": 1,
        "e": "Don't ignore me!"
    }


def test_resolvable_nested_substitutions_should_ignore_env_2():
    data = """    
    joe_company: { employees: [${joe}] }
    joe: { name: joe, height: 192, lives_in: ${ny} }
    ny: { "name": "New York", "country": ${ny_country} }
    joe_country: ${joe.lives_in.country}
    """
    my_env = {
        "ny": "Ignore me!",
        "joe": "Ignore me!",
        "joe.lives_in.country": "Ignore me!",
        "ny_country": "USA"
    }
    with set_env(**my_env):
        result = hocon.loads(data)
    assert result == {
        "ny": {
            "name": "New York",
            "country": "USA"
        },
        "joe": {
            "name": "joe",
            "height": 192,
            "lives_in": {
                "name": "New York",
                "country": "USA"
            }
        },
        "joe_company": {
            "employees": [
                {
                    "name": "joe",
                    "height": 192,
                    "lives_in": {
                        "name": "New York",
                        "country": "USA"
                    }
                }
            ]
        },
        "joe_country": "USA"
    }
