import importlib

import pytest

import compas_fd


def test_trivial():
    print(compas_fd.__version__)
    assert True


@pytest.mark.parametrize(
    "name",
    [
        "compas_fd",
        "compas_fd.constraints",
        "compas_fd.loads",
        "compas_fd.solvers",
        "compas_fd.types",
    ],
)
def test_public_module_imports(name):
    assert importlib.import_module(name).__name__ == name


def test_install_plugin_is_removed():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("compas_fd.install")
    assert not hasattr(compas_fd, "__all_plugins__")
