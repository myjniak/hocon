import contextlib
import os


@contextlib.contextmanager
def set_env(**environ):
    """
    Temporarily set the process environment variables.

    with set_env(PLUGINS_DIR='test/plugins'):
    ...   "PLUGINS_DIR" in os.environ
    True

    "PLUGINS_DIR" in os.environ
    False

    :param environ: Environment variables to set
    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)
