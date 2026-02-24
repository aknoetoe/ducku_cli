"""Tests for CLI format argument."""

import subprocess
import sys
import json
from pathlib import Path


def test_text_format():
    """Test that --format text returns text output."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"

    result = subprocess.run(
        [sys.executable, str(cli_path), "--format", "text"],
        capture_output=True,
        text=True,
        env={"PROJECT_PATH": str(Path(__file__).parent.parent.parent)}
    )

    assert result.returncode in [0, 1]  # May have issues found
    # Text format should have ANSI colors or emojis
    assert "🔍" in result.stdout or "Partial Match" in result.stdout


def test_json_format():
    """Test that --format json returns valid JSON."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"

    result = subprocess.run(
        [sys.executable, str(cli_path), "--format", "json"],
        capture_output=True,
        text=True,
        env={"PROJECT_PATH": str(Path(__file__).parent.parent.parent)}
    )

    assert result.returncode in [0, 1]  # May have issues found

    # Should be valid JSON
    try:
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        # Should have use case results
        assert len(data) > 0
        # Each use case should have title and report
        for use_case_name, use_case_data in data.items():
            assert "title" in use_case_data
            assert "report" in use_case_data
            assert "issues" in use_case_data["report"]
            assert "total_issues" in use_case_data["report"]
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON output: {e}\n{result.stdout}")


def test_html_format():
    """Test that --format html returns HTML output."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"

    result = subprocess.run(
        [sys.executable, str(cli_path), "--format", "html"],
        capture_output=True,
        text=True,
        env={"PROJECT_PATH": str(Path(__file__).parent.parent.parent)}
    )

    assert result.returncode in [0, 1]  # May have issues found

    # Should be HTML
    assert "<html>" in result.stdout
    assert "<body>" in result.stdout
    assert "</body>" in result.stdout
    assert "</html>" in result.stdout
    # Should have headers for use cases
    assert "<h2>" in result.stdout


def test_format_short_flag():
    """Test that -f works as shorthand for --format."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"

    result = subprocess.run(
        [sys.executable, str(cli_path), "-f", "json"],
        capture_output=True,
        text=True,
        env={"PROJECT_PATH": str(Path(__file__).parent.parent.parent)}
    )

    assert result.returncode in [0, 1]
    # Should be valid JSON
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


def test_invalid_format():
    """Test that invalid format choice shows error."""
    cli_path = Path(__file__).parent.parent.parent / "bin" / "cli.py"

    result = subprocess.run(
        [sys.executable, str(cli_path), "--format", "invalid"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 2  # Argument parsing error
    assert "invalid choice" in result.stderr.lower()
