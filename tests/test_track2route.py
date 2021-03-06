"""Test general package info."""
import pathlib

from track2route import __version__


def get_version_from_poetry() -> str:
    """Get version from poetry's pyproject.toml.
    Raises:
        ValueError: If key 'version' could not be found
    Returns:
        str: The version number.
    """
    current_path = pathlib.Path.cwd()
    with current_path.joinpath("pyproject.toml").open("r") as file:
        for line in file:
            if line.startswith("version = "):
                return line.replace("version = ", "").strip()[1:-1]
    raise ValueError("No version found in poetry")


def test_version():
    """Run version test."""
    assert __version__ == get_version_from_poetry()
