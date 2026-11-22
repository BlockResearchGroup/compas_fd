"""Record the COMPAS 2 baselines of ``compas_fd``.

Usage (from the package root, on the harness commit, before any change under ``src/``)::

    <brg-compas2 python> tests/baselines/record.py tests/baselines

The script refuses to run unless

* ``compas`` is a 2.x release,
* ``compas_fd`` is imported from a non-editable installation made from a Git revision
  (the commit is read from ``direct_url.json``), and
* the output directory holds no ``provenance.json`` yet (the fixtures are read-only).

It writes one ``<case>.npz`` per numerical case (inputs as ``in_<name>``, outputs as ``out_<name>``),
``constraints.json`` (fd-10), and ``provenance.json``.
A case that raises is reported and recorded in ``provenance.json``; it gets no fixture.
"""

import datetime
import importlib.metadata
import json
import pathlib
import platform
import sys
import traceback


def legacy_commit():
    """Check the environment and return the commit of the installed legacy package."""
    import compas

    if not compas.__version__.startswith("2."):
        raise SystemExit("Baselines are recorded with COMPAS 2 only; found compas {}.".format(compas.__version__))

    import compas_fd

    distribution = importlib.metadata.distribution("compas_fd")
    text = distribution.read_text("direct_url.json")
    info = json.loads(text) if text else {}
    commit = info.get("vcs_info", {}).get("commit_id")
    if not commit or info.get("dir_info", {}).get("editable"):
        raise SystemExit("compas_fd is not installed from a Git revision (direct_url.json: {}).".format(info))

    installed = pathlib.Path(str(distribution.locate_file("compas_fd"))).resolve()
    imported = pathlib.Path(compas_fd.__file__).resolve().parent
    if imported != installed:
        raise SystemExit("compas_fd is imported from {}, not from the installed legacy package {}.".format(imported, installed))

    return commit


def versions():
    names = ["compas", "compas_fd", "numpy", "scipy", "compas_occ"]
    result = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


def main(argv):
    if len(argv) != 2:
        raise SystemExit(__doc__)

    out = pathlib.Path(argv[1]).resolve()
    if (out / "provenance.json").exists():
        raise SystemExit("{} already holds recorded baselines. They are read-only and change only by decision.".format(out))

    commit = legacy_commit()

    import numpy

    import cases

    status = {}

    for name, case in cases.CASES.items():
        try:
            inputs, outputs = case()
        except Exception as error:
            traceback.print_exc()
            status[name] = "raised {}: {}".format(type(error).__name__, error)
            continue
        arrays = {"in_" + key: value for key, value in inputs.items()}
        arrays.update({"out_" + key: value for key, value in outputs.items()})
        numpy.savez_compressed(out / (name + ".npz"), **arrays)
        status[name] = "recorded"

    try:
        text = cases.fd_10()
    except Exception as error:
        traceback.print_exc()
        status["fd-10"] = "raised {}: {}".format(type(error).__name__, error)
    else:
        (out / cases.CONSTRAINTS_FILE).write_text(text + "\n", encoding="utf-8")
        status["fd-10"] = "recorded"

    provenance = {
        "package": "compas_fd",
        "commit": commit,
        "versions": versions(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "command": " ".join([sys.executable] + argv),
        "date": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "cases": dict(sorted(status.items())),
    }
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")

    for name, value in provenance["cases"].items():
        print(name, value)

    return 0 if all(value == "recorded" for value in status.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
