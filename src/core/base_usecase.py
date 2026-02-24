from abc import ABC, abstractmethod
from src.core.project import Project
from src.core.report import Report


class BaseUseCase(ABC):
    """Base class for all use cases."""
    
    def __init__(self, project: Project):
        self.project = project
        self.name = "base"
    
    @abstractmethod
    def report(self) -> Report:
        """Generate a report of issues found by this use case.
        
        Returns:
            Report: A Report object containing the issues found.
        """
        pass