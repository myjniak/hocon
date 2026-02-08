"""Test with examples from pyhocon."""
from pathlib import Path

import hocon
from tests.utils import set_env


def test_example():
    with set_env(HOME="home_env_var"):
      result = hocon.load(open(Path(__file__).parent / "data" / "pyhocon_readme1.conf"))
    assert result == {
        "databases": {
            "active": True,
            "enable_logging": False,
            "resolver": None,
            "home_dir": "home_env_var",
            "mysql": {
                "host": "abc.com",
                "port": 3306,
                "username": "scott",
                "password": "tiger",
                "retries": 3
            },
            "ips": [
                "192.168.0.1",
                "192.168.0.2",
                "192.168.0.3"
            ]
        },
        "motd": "\n            Hello \"man\"!\n            How is it going?\n         ",
        "retries_msg": "You have 3 retries"
    }


def test_example2():
    result = hocon.load(open(Path(__file__).parent / "data" / "pyhocon_readme2.conf"))
    assert result == {
        "data-center-generic": {
            "cluster-size": 6
        },
        "data-center-east": {
            "cluster-size": 6,
            "name": "east"
        },
        "default-jvm-opts": ["-XX:+UseParNewGC"],
        "large-jvm-opts": ["-XX:+UseParNewGC", "-Xm16g"]
    }
