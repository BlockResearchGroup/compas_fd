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
in `docs/assets/images/`. The loaded-network example is checked by Ruff and
Pyright and executed in CI. The historical COMPAS 2 viewer scripts are
retained in `examples/legacy/`.

## Bug reports

When [reporting a bug](https://github.com/blockresearchgroup/compas_fd/issues) please include:

* Operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

## Feature requests

When [proposing a new feature](https://github.com/blockresearchgroup/compas_fd/issues) please include:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
