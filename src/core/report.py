"""Report data structures for use case results."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class IssueType(Enum):
    """Type of issue found by a use case."""
    ERROR = "error"
    WARNING = "warning"


@dataclass
class Issue:
    """Represents a single issue found by a use case."""
    message: str
    type: IssueType
    metadata: dict = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation of the issue."""
        icon = "🔴" if self.type == IssueType.ERROR else "⚠️"
        return f"{icon} {self.message}"


@dataclass
class Report:
    """Report containing issues found by a use case."""
    issues: List[Issue] = field(default_factory=list)
    
    def add_issue(self, message: str, level: IssueType, **metadata) -> None:
        """Add an issue to the report.

        Args:
            message: The issue message
            level: The issue level (IssueType.ERROR or IssueType.WARNING)
            **metadata: Additional metadata to attach to the issue
        """
        self.issues.append(Issue(message=message, type=level, metadata=metadata))
    
    def has_issues(self) -> bool:
        """Check if the report has any issues."""
        return len(self.issues) > 0
    
    def __str__(self) -> str:
        """String representation of the report."""
        if not self.issues:
            return ""
        return "\n".join(str(issue) for issue in self.issues)
    
    def __bool__(self) -> bool:
        """Boolean representation - True if there are issues."""
        return self.has_issues()