"""Development tasks."""

import os
from pathlib import Path
from shutil import which

from duty import duty

PROJECT_SLUG = "stuco_app"
PY_SRC_PATHS = (Path(_) for _ in (PROJECT_SLUG,))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
TESTING = os.environ.get("TESTING", "0") in {"1", "true"}
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI

TAG_REPO_TEMPLATE = """
echo "Start Agent"
eval $(ssh-agent -s)
echo "Add Key"
cat dm_gitbot_key | tr -d '\r' | ssh-add -
echo "List Identities"
ssh-add -l
export GIT_TRACE=1
export GIT_PYTHON_TRACE=full
git config --global user.email "dm-gitbot@cisco.com"
git config --global --replace-all user.name "DM Gitlab Bot"
cicd_tool tag_repo_with_version RELEASE_CANDIDATE_FLAG
"""


@duty(
    pre=[
        "check_code_quality",
        "check_types",
        "check_dependencies",
        "bandit",
    ],
)
def check(ctx):  # noqa: W0613 (no use for the context argument)
    """
    Check it all!

    Arguments:
        ctx: The context instance (passed automatically).
    """  # noqa: D400 (exclamation mark is funnier)


@duty
def check_code_quality(ctx, files=PY_SRC, disable_noqa="False"):
    """
    Check the code quality.

    Arguments:
        ctx: The context instance (passed automatically).
        files: The files to check.
    """
    ctx.run(
        f"ruff check {files} ",
        title="Checking code quality",
        pty=PTY,
    )


@duty
def check_dependencies(ctx):
    """
    Check for vulnerabilities in dependencies.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    nofail = False
    safety = which("safety")
    if not safety:
        pipx = which("pipx")
        if pipx:
            safety = f"{pipx} run safety"
        else:
            safety = "safety"
            nofail = True
    ctx.run(
        f"/poetry_venv/bin/poetry export -f requirements.txt --without-hashes | {safety} check --stdin --full-report  --ignore 47833 --ignore 46499 --ignore 51668 --ignore 65213",  # noqa: E501
        title="Checking dependencies",
        pty=PTY,
        nofail=nofail,
    )


@duty
def check_types(ctx):
    """
    Check that the code is correctly typed.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        f"mypy --config-file config/mypy.ini --no-namespace-packages --non-interactive --install-types {PY_SRC}",
        title="Type-checking",
        pty=PTY,
    )


@duty(silent=True)
def clean(ctx):
    """
    Delete temporary files.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("rm -rf .coverage*")
    ctx.run("rm -rf .mypy_cache")
    ctx.run("rm -rf .pytest_cache")
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf pip-wheel-metadata")
    ctx.run("rm -rf site")
    ctx.run("rm -f .spg/.just-downloaded")
    ctx.run("rm -f requirements.txt")
    ctx.run("rm -f dev-requirements.txt")
    ctx.run("rm -f *.log")
    ctx.run("rm -rf test_log_dir")
    ctx.run("find . -type d -name __pycache__ | xargs rm -rf")
    ctx.run("find . -name '*.rej' -delete")


@duty(silent=True)
def clean_coverage(ctx):
    """
    Delete temporary files.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("rm -rf .coverage*")


@duty(pre=[clean], silent=True)
def deep_clean(ctx):
    """Delete all temporary files (including virtual environment).

    Args:
        ctx: The context instance (passed automatically).
    """
    ctx.run("rm -rf /venv")


@duty
def format(ctx):  # noqa: W0622 (we don't mind shadowing the format builtin)
    """
    Run formatting tools on the code.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run(f"black {PY_SRC}", title="Formatting code", pty=PTY)


@duty(capture=False, silent=False)
def prepare_bumpversion(ctx):
    ctx.run("cp config/.bumpversion.cfg .", title="Copying bumpversion config file", pty=PTY)


@duty(capture=False, silent=False)
def verify_not_released(ctx):
    """
    Ensure that the current version of this project has not been published yet.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        "cicd_tool verify_not_released",
        title="Verifying that version has not been released",
        pty=PTY,
    )


@duty(pre=[prepare_bumpversion], capture=False, silent=False)
def tag_version(ctx, release_candidate_flag=""):
    """
    Tag git with the calculated version based on branch.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    dm_gitbot_key_string = os.getenv("DM_GITBOT_SSH_PRIVATE_KEY", "KEYNOTFOUND")
    ctx.run(
        f'echo "{dm_gitbot_key_string}" > dm_gitbot_key',
        title="Create dm_gitbot key file",
        pty=PTY,
    )
    tag_repo_script_contents = TAG_REPO_TEMPLATE.replace("RELEASE_CANDIDATE_FLAG", release_candidate_flag)
    ctx.run(
        f'echo "{tag_repo_script_contents}" > tag_repo.sh',
        title="Create tag_repo shell script",
        pty=PTY,
    )
    ctx.run(
        "cat tag_repo.sh",
        title="Display tag_repo shell script",
        pty=PTY,
    )
    ctx.run("chmod 777 tag_repo.sh", title="Set script to executable", pty=PTY)
    ctx.run("bash tag_repo.sh", title="Run Script", pty=PTY)
    ctx.run(
        "rm -f .bumpversion.cfg ",  # noqa: E501
        title="Cleanup 1",
        pty=PTY,
        capture=False,
    )
    ctx.run(
        "git config --global --unset user.email ",  # noqa: E501
        title="Cleanup 2",
        pty=PTY,
        capture=False,
    )
    ctx.run(
        f"git checkout pyproject.toml .spg/version.txt {PROJECT_SLUG}/__init__.py",  # noqa: E501
        title="Cleanup 3",
        pty=PTY,
        capture=False,
    )


@duty(pre=[clean_coverage])
def test(ctx, type="unit", match="", capture=True, min_coverage_pct=25):
    """
    Run the test suite.

    Arguments:
        ctx: The context instance (passed automatically)
        type: The type of test '*' | 'unit' | 'integration'
        match: A pytest expression to filter selected tests
        capture: True | False
        min_coverage_pct the minimum coverage percentage required
    """
    CAPTURE = capture is True
    ctx.run(
        [
            "pytest",
            "-c",
            "config/pytest.ini",
            "-n",
            "1",
            "-k",
            match,
            "tests" if type == "*" else f"tests/{type}",
        ],
        title="Running tests",
        capture=CAPTURE,
        pty=PTY,
    )
    if type == "integration":
        ctx.run(
            ["coverage", "report"],
            title="Producing Coverage Report",
            capture=False,
        )
    else:
        ctx.run(
            ["coverage", "report", f"--fail-under={min_coverage_pct}"],
            title="Producing Coverage Report",
            capture=False,
        )


@duty
def update_dependencies(
    ctx,
):
    """
    Update all dependencies to their latest available verisons.

    dummy task just to get the task to show up in help for Make."""

    ctx.run(
        "/poetry_venv/bin/poetry update",
        title="Upgrading dependencies to their latest versions",
        pty=PTY,
    )


@duty
def bandit(ctx, files=PY_SRC):
    """
    Run Bandit Security Checks on the project.

    Arguments:
        ctx: The context instance (passed automatically).
        files: The files to check.
    """
    ctx.run(
        f"bandit -r {files}",
        title="Checking for Common Security Issues with Bandit",
        capture=False,
        pty=PTY,
    )


@duty
def black(ctx, files=PY_SRC):
    """
    Run black the uncompromising Python code formatter on the project.

    Arguments:
        ctx: The context instance (passed automatically).
        files: The files to check.
    """
    ctx.run(
        f"black {files} tests",
        title="Running black code formatter on the project",
        capture=False,
        pty=PTY,
    )


@duty
def bump_patch(ctx):
    """
    Bump version to the next patch number.

    dummy task just to get the task to show up in help for Make."""
    pass


@duty
def bump_minor(ctx):
    """
    Bump version to the next minor number.

    dummy task just to get the task to show up in help for Make."""
    pass


@duty
def bump_major(ctx):
    """
    Bump version to the next major number.

    dummy task just to get the task to show up in help for Make."""
    pass


@duty
def coverage(ctx):
    """
    Run Coverage on the project.

    dummy task just to get the task to show up in help for Make."""
    pass


@duty
def documentation(ctx):
    """
    Generate Documentation.

    dummy task just to get the task to show up in help for Make."""
    pass


@duty
def build(ctx):
    """
    Build Distribution Files and Wheel.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("/poetry_venv/bin/poetry build", title="Generating Distribution Files", pty=PTY)


@duty(pre=[prepare_bumpversion], capture=False, silent=False)
def publish(ctx, artifactory_user=None, artifactory_password=None, branch_name="dummy"):
    """
    Package the library for PyPi / Artifactory.
    """
    ctx.run(
        "rm -f dist/*",
        title="Clean up any old distributions",
        pty=PTY,
    )
    ctx.run(
        f"cicd_tool prepare_pypi_version {branch_name}",
        title=f"Preparing Package Versioning for Release from branch: {branch_name}",
        pty=PTY,
    )
    if artifactory_password and artifactory_user:
        ctx.run(
            "/poetry_venv/bin/poetry config repositories.cisco_artifactory 'https://engci-maven-master.cisco.com/artifactory/api/pypi/seceng-pypi-local'",  # noqa: E501
            title="Set Artifactory Repository Url",
            pty=PTY,
        )
        ctx.run(
            f"/poetry_venv/bin/poetry publish -r cisco_artifactory -u {artifactory_user} -p {artifactory_password} --build",  # noqa: E501
            title=f"Publishing to Cisco Artifactory with build for release from branch='{branch_name}'",
            pty=PTY,
        )
    else:
        ctx.run(
            "/poetry_venv/bin/poetry build",
            title=f"Generating Distribution Files from branch='{branch_name}' - not deploying to Artifactory - no artifactory_user and password specified",  # noqa: E501
            pty=PTY,
        )
    ctx.run(
        f"rm -f .bumpversion.cfg && git checkout pyproject.toml .spg/version.txt {PROJECT_SLUG}/__init__.py",
        title="Cleanup",
        pty=PTY,
    )


@duty
def clean_bundle(ctx):
    """
    Clean up any previous distribution files.

    dummy task just to get the task to show up in help for Make."""
    pass


@duty
def requirements_files(ctx):
    """
    Create legacy requirements files (requirements.txt and dev-requirements.txt) from pyproject.toml file.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    # /poetry_venv/bin/poetry export -f requirements.txt -o requirements.txt
    ctx.run(
        [
            "/poetry_venv/bin/poetry",
            "export",
            "-f",
            "requirements.txt",
            "--dev",
            "-o",
            "dev-requirements.txt",
        ],
        title="Creating dev-requirements.txt",
    )
    ctx.run(
        [
            "/poetry_venv/bin/poetry",
            "export",
            "-f",
            "requirements.txt",
            "-o",
            "requirements.txt",
        ],
        title="Creating requirements.txt",
    )
