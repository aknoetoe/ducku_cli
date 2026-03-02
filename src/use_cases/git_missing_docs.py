import re
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

from src.core.base_usecase import BaseUseCase
from src.core.code.dispatcher import collect_code_entities_from_content, SUPPORTED_EXTENSIONS
from src.core.entity import EntitiesContainer, collect_docs_entities, entities_for_comparison
from src.core.project import Project
from src.core.report import Report, IssueType
from src.helpers.comparison import paths_similar, PATH_RELEVANCE_THRESHOLD

_DOC_EXTENSIONS = {'.md', '.markdown', '.adoc', '.asciidoc'}


def _is_code_file(filepath: str) -> bool:
    return Path(filepath).suffix.lower() in SUPPORTED_EXTENSIONS


def _is_doc_file(filepath: str) -> bool:
    return Path(filepath).suffix.lower() in _DOC_EXTENSIONS


def _source_file(parent: str) -> str:
    """Extract the source filename from a container parent path.

    e.g. '/abs/path/README.md::h2::Use Cases::...' -> 'README.md'
    """
    return Path(parent.split("::")[0]).name


def _relativize(parent: str, project_root: Path) -> str:
    """Strip project_root prefix from the path component of a container parent."""
    path_part, _, rest = parent.partition("::")
    try:
        rel = str(Path(path_part).relative_to(project_root))
    except ValueError:
        return parent  # Already relative or outside project_root
    return rel + ("::" + rest if rest else "")


def _best_doc_match(
    code_parent: str,
    docs_entities: List[EntitiesContainer],
) -> Tuple[Optional[EntitiesContainer], float]:
    """Return the doc container most similar to code_parent, with its score."""
    best_score = 0.0
    best_container = None
    for doc in docs_entities:
        score = paths_similar(code_parent, doc.parent)
        if score > best_score:
            best_score = score
            best_container = doc
    return best_container, best_score


def find_missing_docs(
    changed_files: List[str],
    docs_entities: List[EntitiesContainer],
    project_root: Path,
) -> Report:
    """Report code changes that lack corresponding documentation updates.

    Args:
        changed_files: relative file paths from git diff (e.g. ["src/foo.py", "README.md"])
        docs_entities: all doc entity containers for the project
        project_root: absolute path to the project root, used to resolve code files
    """
    changed_code = [p for p in changed_files if _is_code_file(p)]
    changed_doc_files = {Path(p).name for p in changed_files if _is_doc_file(p)}

    code_containers: List[EntitiesContainer] = []
    for filepath in changed_code:
        collect_code_entities_from_content(project_root / filepath, code_containers)

    # Only containers under some header carry meaningful doc structure for path mapping;
    # standalone lists (no ::hN:: in path) are noise.
    header_docs = [c for c in docs_entities if re.search(r'::h[1-6]::', c.parent)]

    result = Report()
    for code_container in entities_for_comparison(code_containers):
        relative_parent = _relativize(code_container.parent, project_root)
        best_doc, best_score = _best_doc_match(relative_parent, header_docs)
        if best_score < PATH_RELEVANCE_THRESHOLD:
            continue
        doc_file = _source_file(best_doc.parent)
        if doc_file not in changed_doc_files:
            result.add_issue(
                f"Code changed but related docs not updated:\n"
                f" - Code: {relative_parent} ({code_container.type})\n"
                f" - Related docs: {best_doc.parent}\n"
                f" - Doc file: {doc_file} (not in changed files)",
                level=IssueType.WARNING,
                code_source=relative_parent,
                docs_source=best_doc.parent,
                doc_file=doc_file,
            )
    return result


class GitMissingDocs(BaseUseCase):
    def __init__(self, project: Project):
        super().__init__(project)
        self.name = "git_missing_docs"

    def report(self) -> Report:
        changed_files = _git_diff_files(self.project.project_root)
        if not changed_files:
            return Report()
        docs_entities = collect_docs_entities(self.project.documentation)
        return find_missing_docs(changed_files, docs_entities, self.project.project_root)


def _git_diff_files(project_root: Path) -> List[str]:
    """Return relative paths of files changed in the last commit."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^1"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            return []
        return [
            line.strip()
            for line in proc.stdout.splitlines()
            if line.strip() and (project_root / line.strip()).exists()
        ]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
