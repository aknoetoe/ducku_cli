import os
import traceback
from src.use_cases.partial_lists import PartialMatch 
import argparse
from pathlib import Path
from io import StringIO
from contextlib import redirect_stdout
from src.use_cases.pattern_search import PatternSearch
from src.use_cases.unused_modules import UnusedModules
from src.use_cases.spellcheck import Misspellings
from src.core.project import Project

# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_GREEN = '\033[92m'

def get_version():
    """Get version from pyproject.toml."""
    try:
        import tomllib
    except ImportError:
        # Python < 3.11
        try:
            import tomli as tomllib
        except ImportError:
            return "unknown"

    # Get the project root (parent of bin directory)
    cli_file = Path(__file__)
    project_root = cli_file.parent.parent
    pyproject_path = project_root / "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data.get("project", {}).get("version", "unknown")
    except (FileNotFoundError, KeyError):
        return "unknown"

def colorized_title(text, color=Colors.BRIGHT_CYAN):
    """Create a colorized title with emoji and formatting."""
    return f"\n{Colors.BOLD}{color}🔍 {text}{Colors.RESET}\n" + "=" * (len(text) + 3) + "\n"

def start(base, output_format="text"):
    if not os.path.isdir(base):
        print(f"Path {base} doesn't exist")
        exit()
    try:
        use_cases_to_run = [
            (PartialMatch, "Partial Match Detection"),
            (PatternSearch, "Pattern Search Analysis"), 
            (UnusedModules, "Unused Modules Detection"),
            (Misspellings, "Misspellings Detection"),
        ]
        p = Project(base)
        found = False

        # JSON format: collect all results first (suppress debug output)
        if output_format == "json":
            import json
            results = {}
            # Capture stdout to suppress debug messages
            captured_output = StringIO()
            with redirect_stdout(captured_output):
                for uc_class, title in use_cases_to_run:
                    uci = uc_class(p)
                    enabled = getattr(p.config.use_case_options, uci.name).enabled
                    if not enabled:
                        continue
                    r = uci.report()
                    if r.has_issues():
                        found = True
                    # Convert to dict instead of nested JSON string
                    report_data = {
                        "issues": [
                            {
                                "message": issue.message,
                                "type": issue.type.value,
                                "metadata": issue.metadata
                            }
                            for issue in r.issues
                        ],
                        "total_issues": len(r.issues)
                    }
                    results[uci.name] = {
                        "title": title,
                        "report": report_data
                    }
            print(json.dumps(results, indent=2))
        # HTML format: output with HTML structure (suppress debug output)
        elif output_format == "html":
            print("<html><body>")
            # Capture stdout to suppress debug messages during report generation
            captured_output = StringIO()
            html_parts = []
            with redirect_stdout(captured_output):
                for uc_class, title in use_cases_to_run:
                    uci = uc_class(p)
                    enabled = getattr(p.config.use_case_options, uci.name).enabled
                    if not enabled:
                        continue
                    r = uci.report()
                    if r.has_issues():
                        found = True
                    html_parts.append(f"<h2>{title}</h2>")
                    report_str = r.to_html() if hasattr(r, 'to_html') else str(r)
                    if report_str and report_str.strip():
                        html_parts.append(report_str)
                    else:
                        html_parts.append("<p>✅ No issues found</p>")
            # Print all HTML after suppressing debug output
            for part in html_parts:
                print(part)
            print("</body></html>")
        # Text format (default): original behavior
        else:
            for uc_class, title in use_cases_to_run:
                uci = uc_class(p)
                enabled = getattr(p.config.use_case_options, uci.name).enabled
                if not enabled:
                    continue
                r = uci.report()
                if r.has_issues():
                    found = True
                print(colorized_title(title))
                report_str = str(r)
                if report_str and report_str.strip():  # Print the actual results
                    print(report_str)
                else:  # No issues found
                    print(f"{Colors.BRIGHT_GREEN}✅ No issues found{Colors.RESET}\n")

        # Check fail-on-issues: config file takes precedence, then env var
        fail_on_issues = p.config.fail_on_issues
        if fail_on_issues is None:
            fail_on_issues = os.getenv("DUCKU_FAIL_ON_ISSUES", "true").lower() == "true"
        if fail_on_issues and found:
            exit(1)
    except Exception as e:
        print(e)
        traceback.print_exc()

def main():
    """Entry point for the ducku CLI."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Ducku - Documentation analysis and code quality tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"ducku {get_version()}"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "html"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--target", "-t",
        type=str,
        help="Path to the project directory to analyze"
    )

    # Parse args
    args = parser.parse_args()

    MULTI_FOLDER = os.getenv("MULTI_FOLDER")
    PROJECT_PATH = args.target or os.getenv("PROJECT_PATH")
    if MULTI_FOLDER:
        for name in os.listdir(MULTI_FOLDER):
            full_path = os.path.join(MULTI_FOLDER, name)
            if os.path.isdir(full_path):
                if args.format == "text":
                    print(f"\n{Colors.BOLD}{Colors.BRIGHT_YELLOW}🏗️  PROJECT {name}{Colors.RESET}")
                    print("=" * (len(name) + 12))
                start(full_path, output_format=args.format)
    else:
        base = PROJECT_PATH if PROJECT_PATH else (input("Input the full path to the project: ")).strip()
        start(base, output_format=args.format)

# This allows the script to be run directly
if __name__ == "__main__":
    main()
