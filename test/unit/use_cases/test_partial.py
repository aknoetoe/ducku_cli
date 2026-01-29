from pathlib import Path
from src.core.project import Project
from src.use_cases.partial_lists import PartialMatch

def test_partial_uc():
    path = Path(__file__).parent / ".." / "mocks" / "projects" / "parallel_entities"
    p = Project(path)
    uc = PartialMatch(p)
    report = uc.report()
    # The test should check that we get a Report object
    assert report is not None
    # Print for debugging
    if report.has_issues():
        print(str(report))