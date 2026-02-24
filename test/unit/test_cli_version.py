"""Tests for CLI version and target arguments."""

import subprocess
import sys
from pathlib import Path


def test_version_argument():
    """Test that --version returns the correct version."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"

    # Test --version
    result = subprocess.run(
        [sys.executable, str(cli_path), "--version"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "ducku" in result.stdout
    assert "1.2.0" in result.stdout


def test_version_short_argument():
    """Test that -v returns the correct version."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"

    # Test -v
    result = subprocess.run(
        [sys.executable, str(cli_path), "-v"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "ducku" in result.stdout
    assert "1.2.0" in result.stdout


def test_target_argument():
    """Test that --target specifies the project path."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"
    project_path = Path(__file__).parent.parent.parent

    result = subprocess.run(
        [sys.executable, str(cli_path), "--target", str(project_path), "--format", "json"],
        capture_output=True,
        text=True
    )

    assert result.returncode in [0, 1]  # May have issues found
    # Should produce JSON output
    import json
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


def test_target_short_argument():
    """Test that -t works as shorthand for --target."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"
    project_path = Path(__file__).parent.parent.parent

    result = subprocess.run(
        [sys.executable, str(cli_path), "-t", str(project_path), "--format", "json"],
        capture_output=True,
        text=True
    )

    assert result.returncode in [0, 1]
    import json
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


def test_target_overrides_env():
    """Test that --target takes precedence over PROJECT_PATH env var."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"
    project_path = Path(__file__).parent.parent.parent

    # Set PROJECT_PATH to nonexistent directory, but use --target with valid path
    result = subprocess.run(
        [sys.executable, str(cli_path), "--target", str(project_path), "--format", "json"],
        capture_output=True,
        text=True,
        env={"PROJECT_PATH": "/nonexistent"}
    )

    # Should succeed because --target overrides env var
    assert result.returncode in [0, 1]
    import json
    data = json.loads(result.stdout)
    assert isinstance(data, dict)
