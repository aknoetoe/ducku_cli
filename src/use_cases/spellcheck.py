from src.core.project import Project
from src.core.base_usecase import BaseUseCase
from src.core.report import Report, IssueType
import codespell_lib
import io
from contextlib import redirect_stdout, redirect_stderr


class Misspellings(BaseUseCase):
    def __init__(self, project: Project):
        super().__init__(project)
        self.name = "spellcheck"

    def report(self) -> Report:
        result = Report()

        # Capture output from codespell
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Get all documentation files to check
        doc_files = []
        for dp in self.project.documentation.doc_parts:
            if dp.source.type == "file" and "path" in dp.source.metadata:
                doc_files.append(dp.source.metadata["path"])

        if not doc_files:
            result.add_issue("No documentation files found to check for misspellings.", level=IssueType.WARNING)
            return result

        try:
            # Run codespell with captured output
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exit_code = codespell_lib.main(
                    '--ignore-words-list', 'Ducku,ducku',  # Ignore our project name
                    '--quiet-level', '2',  # Only show misspellings
                    *doc_files
                )

            output = stdout_capture.getvalue()
            error_output = stderr_capture.getvalue()

            if exit_code == 0 and not output:
                return result
            elif output:
                # Parse the output line by line
                for line in output.strip().split('\n'):
                    if line.strip():
                        result.add_issue(f"Misspelling: {line}", level=IssueType.WARNING, raw_output=line)
            elif error_output:
                result.add_issue(f"Error checking misspellings: {error_output}", level=IssueType.ERROR, error=error_output)

        except (OSError, ValueError) as e:
            result.add_issue(f"Error running misspelling check: {str(e)}", level=IssueType.ERROR, exception=str(e))

        return result