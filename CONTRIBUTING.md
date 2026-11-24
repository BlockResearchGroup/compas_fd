# Contributing

Contributions are welcome and very much appreciated!

## Code contributions

We accept code contributions through pull requests.
In short, this is how that works.

1. Fork [the repository](https://github.com/blockresearchgroup/compas_fd) and clone the fork.
2. Create and populate the locked environment using uv.

   ```bash
   uv sync --locked --group docs
   ```

3. Run the local checks before and after making your changes.

   ```bash
   uv run --no-sync ruff check src tests docs/examples
   uv run --no-sync ruff format --check src tests docs/examples
   uv run --no-sync pyright
   uv run --no-sync pytest --doctest-modules src/compas_fd tests
   uv run --no-sync python docs/examples/loaded_network.py
   uv run --no-sync mkdocs build --strict
   ```

4. Add a changelog entry for user-facing changes and
   [open a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests).

Keep maintained Python examples in `docs/examples/` and documentation images
in `docs/assets/images/`. Write examples as direct, step-by-step scripts.
Introduce functions only when they clarify the example or remove substantial
repetition. Use named sections with 80-character comment dividers for
parameters, model setup and major steps. Give Viewer setup and rendering their
own section. Add a trailing comma to longer function call argument lists so
Ruff formats them one argument per line. Use worked examples to demonstrate
inputs and results, and keep numerical assertions in `tests/`. The
loaded-network example is checked by Ruff and Pyright and executed in CI.

Keep package code focused on the solver and its helpers. Define clear input
and output contracts, validate inputs, and test the numerical results and
failure cases. Once correctness is verified, use measured baselines to guide
performance work. Use supported geometry and data structures with the standard
COMPAS Viewer and scene in examples. Keep custom scene objects and rendering
extensions out of the solver package.

When changing `docs/examples/viewer/`, use the interactive COMPAS 3 environment
to check types and run the affected examples with a desktop session.

```bash
uv run --no-sync pyright --pythonpath "$(command -v python)" docs/examples/viewer/*.py
```

## Bug reports

When [reporting a bug](https://github.com/blockresearchgroup/compas_fd/issues) please include:

* Operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

## Feature requests

When [proposing a new feature](https://github.com/blockresearchgroup/compas_fd/issues) please include:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
