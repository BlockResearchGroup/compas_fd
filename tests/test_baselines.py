"""Comparison against the COMPAS 2 baselines in ``tests/baselines`` (read-only fixtures).

Every case of ``tests/baselines/cases.py`` is run again. The regenerated inputs must equal
the stored inputs exactly. Float outputs must satisfy ``abs(new - base) <= ATOL + RTOL * abs(base)``;
integer outputs and all shapes must be equal. The maximum absolute and relative deviation
per output is printed (``pytest -rP``); the relative deviation is taken over the non-zero baseline values.
"""

import importlib.util
import pathlib

import compas
import numpy as np
import pytest

BASELINES = pathlib.Path(__file__).parent / "baselines"

ATOL = 1e-9
RTOL = 1e-9


def _load_cases():
    spec = importlib.util.spec_from_file_location("compas_fd_baseline_cases", BASELINES / "cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cases = _load_cases()


def deviation(new, base):
    """Maximum absolute deviation, and maximum relative deviation over the non-zero baseline values."""
    difference = np.abs(new - base)
    max_abs = float(difference.max()) if difference.size else 0.0
    nonzero = base != 0
    max_rel = float((difference[nonzero] / np.abs(base[nonzero])).max()) if nonzero.any() else 0.0
    return max_abs, max_rel


@pytest.mark.parametrize("name", list(cases.CASES))
def test_baseline(name):
    if name in cases.BACKENDS:
        pytest.importorskip(cases.BACKENDS[name])

    with np.load(BASELINES / (name + ".npz"), allow_pickle=False) as fixture:
        stored = {key: fixture[key] for key in fixture.files}

    inputs, outputs = cases.CASES[name]()

    assert sorted(stored) == sorted(["in_" + key for key in inputs] + ["out_" + key for key in outputs])

    for key, new in inputs.items():
        base = stored["in_" + key]
        assert new.dtype == base.dtype, key
        assert new.shape == base.shape, key
        assert np.array_equal(new, base), "input {} differs from the stored input".format(key)

    failed = []

    for key, new in outputs.items():
        base = stored["out_" + key]
        assert new.dtype == base.dtype, key
        assert new.shape == base.shape, key
        if np.issubdtype(base.dtype, np.floating):
            max_abs, max_rel = deviation(new, base)
            print("{} {}: max abs deviation {:.3e}, max rel deviation {:.3e}".format(name, key, max_abs, max_rel))
            if not np.all(np.abs(new - base) <= ATOL + RTOL * np.abs(base)):
                failed.append(key)
        else:
            assert np.array_equal(new, base), key

    assert not failed, "outputs beyond tolerance: {}".format(failed)


def test_baseline_constraint_data():
    """fd-10: the COMPAS 2 JSON of the constraints loads to the same constraints, and round-trips."""
    text = (BASELINES / cases.CONSTRAINTS_FILE).read_text(encoding="utf-8")

    loaded = compas.json_loads(text)
    expected = cases.fd_10_constraints()

    assert [type(constraint) for constraint in loaded] == [type(constraint) for constraint in expected]
    assert [constraint.__data__ for constraint in loaded] == [constraint.__data__ for constraint in expected]
    assert [constraint._rhino_guid for constraint in loaded] == [None, cases.RHINO_GUID, None, None]

    again = compas.json_loads(compas.json_dumps(loaded))

    assert [type(constraint) for constraint in again] == [type(constraint) for constraint in loaded]
    assert [constraint.__data__ for constraint in again] == [constraint.__data__ for constraint in loaded]
