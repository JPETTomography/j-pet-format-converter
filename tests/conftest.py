import pytest


@pytest.fixture(scope="session")
def temp_directory(tmp_path_factory):
    fn = tmp_path_factory.mktemp("i2d_test")
    return fn
