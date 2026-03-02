"""
Tests for git_missing_docs use case.

Mock project layout (test/unit/mocks/projects/git_missing_docs/):
  README.md  — has "## Use Cases" with "### Partial Match" and "### Content Check"
  src/use_cases/partial_match.py  — functions find_partials, partial_match

Self-referential scenario:
  Changing partial_match.py without updating README -> should report.
  Changing partial_match.py AND README -> no report.
"""
from pathlib import Path

from src.core.documentation import Documentation, DocFile
from src.core.entity import collect_docs_entities
from src.helpers.comparison import paths_similar, PATH_RELEVANCE_THRESHOLD
from src.use_cases.git_missing_docs import find_missing_docs

_MOCK_ROOT = (Path(__file__).parent / ".." / "mocks" / "projects" / "git_missing_docs").resolve()
_README = _MOCK_ROOT / "README.md"


def _mock_docs():
    doc = Documentation()
    doc.process_file(_README)
    doc.process_content()
    return collect_docs_entities(doc)


# ---------------------------------------------------------------------------
# paths_similar smoke tests (inline paths, no filesystem dependency)
# ---------------------------------------------------------------------------

def test_paths_similar_use_case_file_to_section():
    """use_cases/partial_match.py should relate to the Partial Match section."""
    score = paths_similar(
        "src/use_cases/partial_match.py",
        "README.md::h1::My App::h2::Use Cases::h3::Partial Match::bullet_list",
    )
    assert score > PATH_RELEVANCE_THRESHOLD, f"got {score:.3f}"


def test_paths_similar_unrelated_paths_score_low():
    """A helpers file should not relate to the Use Cases section."""
    score = paths_similar(
        "src/helpers/comparison.py",
        "README.md::h1::My App::h2::Installation",
    )
    assert score < PATH_RELEVANCE_THRESHOLD, f"got {score:.3f}"


def test_paths_similar_related_scores_higher_than_unrelated():
    related = paths_similar(
        "src/use_cases/partial_match.py",
        "README.md::h1::My App::h2::Use Cases::h3::Partial Match::bullet_list",
    )
    unrelated = paths_similar(
        "src/use_cases/partial_match.py",
        "README.md::h1::My App::h2::Installation",
    )
    assert related > unrelated, f"related={related:.3f} unrelated={unrelated:.3f}"


# ---------------------------------------------------------------------------
# find_missing_docs integration tests against mock project
# ---------------------------------------------------------------------------

def test_reports_when_use_case_changed_but_readme_not():
    """Changing partial_match.py without touching README must raise an issue."""
    docs = _mock_docs()
    report = find_missing_docs(["src/use_cases/partial_match.py"], docs, _MOCK_ROOT)
    assert report.has_issues(), "Expected issue: code changed but README not"
    doc_files = {issue.metadata.get("doc_file") for issue in report.issues}
    assert "README.md" in doc_files, f"Expected README.md in doc_files, got {doc_files}"


def test_no_issue_when_readme_also_changed():
    """Changing both partial_match.py and README must produce no issue for README."""
    docs = _mock_docs()
    report = find_missing_docs(
        ["src/use_cases/partial_match.py", "README.md"], docs, _MOCK_ROOT
    )
    readme_issues = [i for i in report.issues if i.metadata.get("doc_file") == "README.md"]
    assert not readme_issues, f"Unexpected README issues: {readme_issues}"


def test_no_issue_when_only_doc_changed():
    """Changing only README produces no issues (no code changed)."""
    docs = _mock_docs()
    report = find_missing_docs(["README.md"], docs, _MOCK_ROOT)
    assert not report.has_issues()


def test_no_issue_for_empty_changeset():
    docs = _mock_docs()
    report = find_missing_docs([], docs, _MOCK_ROOT)
    assert not report.has_issues()


def test_no_issue_for_unrelated_code_file():
    """A file unrelated to documented use cases should not trigger a report."""
    docs = _mock_docs()
    # comparison.py has no match in the mock README
    report = find_missing_docs(["src/helpers/comparison.py"], docs, _MOCK_ROOT)
    assert not report.has_issues()
