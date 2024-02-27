from __future__ import print_function

import os
import invoke
from invoke import Collection

from compas_invocations import build
from compas_invocations import docs
from compas_invocations import tests
from compas_invocations.console import chdir


@invoke.task()
def lint(ctx):
    """Check the consistency of coding style."""
    print("Running ruff linter...")
    ctx.run("ruff check src tests")

    print("Running black linter...")
    ctx.run("black --check --diff --color src tests")


@invoke.task()
def format(ctx):
    """Reformat the code base using black."""
    print("Running black formatter...")
    ctx.run("black src tests")


@invoke.task()
def check(ctx):
    """Check the consistency of documentation, coding style and a few other things."""

    with chdir(ctx.base_folder):
        lint(ctx)

        print("Checking MANIFEST.in...")
        ctx.run("check-manifest")

        print("Checking metadata...")
        ctx.run("python setup.py check --strict --metadata")


ns = Collection(
    docs.help,
    # style.check,
    # style.lint,
    # style.format,
    check,
    lint,
    format,
    docs.docs,
    docs.linkcheck,
    tests.test,
    tests.testdocs,
    tests.testcodeblocks,
    build.prepare_changelog,
    build.clean,
    build.release,
    build.build_ghuser_components,
)
ns.configure(
    {
        "base_folder": os.path.dirname(__file__),
        "ghuser": {
            "source_dir": "src/compas_ghpython/components",
            "target_dir": "src/compas_ghpython/components/ghuser",
            "prefix": "COMPAS: ",
        },
    }
)
