import importlib
import pkgutil

from compas.plugins import ExtensionPoint
from compas.plugins import PluginManager

import compas_fd

from compas_fd.constraints import Constraint


def test_constraint_classes_have_no_legacy_data_schema() -> None:
    classes = {Constraint, *Constraint.GEOMETRY_CONSTRAINT.values()}
    assert all(not hasattr(cls, "DATASCHEMA") for cls in classes)


def test_all_package_modules_import():
    modules = [module.name for module in pkgutil.walk_packages(compas_fd.__path__, prefix="compas_fd.")]

    for module in modules:
        importlib.import_module(module)


def test_install_plugin_is_discoverable():
    install = ExtensionPoint("https://plugins.compas.dev/", "install", "installable_rhino_packages")
    (implementation,) = [plugin for plugin in PluginManager().collect(install) if plugin.plugin.__name__ == "compas_fd.install"]

    assert implementation.priority == 1
    assert implementation.method() == ["compas_fd"]
