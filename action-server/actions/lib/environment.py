import os


def get_env(name):
    value = os.environ.get(name)
    if value is None:
        raise Exception(f"Environment variable '{name}' is not set.")
    return value
