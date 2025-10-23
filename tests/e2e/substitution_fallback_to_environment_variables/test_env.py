import pytest

import hocon
from hocon.exceptions import HOCONSubstitutionUndefinedError
from tests.utils import set_env

pytestmark = pytest.mark.f13


def test_basic():
    with set_env(HOCON_VAR="take me!"):
        result = hocon.loads("key=${HOCON_VAR}")
    assert result == {"key": "take me!"}


def test_block_env_with_null():
    """An application can explicitly block looking up a substitution in the environment
    by setting a value in the configuration, with the same name as the environment variable.
    """
    with set_env(HOME="I shall be ignored"):
        result = hocon.loads("HOME=null, key=${HOME}")
    assert result == {"HOME": None, "key": None}


def test_empty_string_env_var():
    """Env variables set to the empty string are kept as such (set to empty string, rather than undefined)"""
    with set_env(HOCON_EMPTY=""):
        result = hocon.loads("key=${HOCON_EMPTY}")
    assert result == {
        "key": "",
    }


def test_no_env_var():
    """When env variable doesn't exist or user does not have enough permissions to access the variable,
    exception should be raised.
    """
    with pytest.raises(HOCONSubstitutionUndefinedError):
        hocon.loads("key=${HOCON_EMPTY}")
