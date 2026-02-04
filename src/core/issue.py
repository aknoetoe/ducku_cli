from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class IssueType(Enum):
    """Types of issues that can be reported by use cases."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    """Represents a single issue found by a use case."""
    message: str
    type: IssueType
    location: Optional[str] = None  # File path, line number, or other location info
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    def __str__(self) -> str:
        """Format issue as human-readable string."""
        type_prefix = f"[{self.type.value.upper()}]"
        location_str = f" at {self.location}" if self.location else ""
        return f"{type_prefix}{location_str}: {self.message}"


@dataclass
class UseCaseReport:
    """Standardized report returned by use cases."""
    issues: List[Issue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)  # For summary stats, etc.
    
    def add_issue(
        self,
        message: str,
        type: IssueType = IssueType.WARNING,
        location: Optional[str] = None,
        **metadata
    ) -> None:
        """Convenience method to add an issue to the report."""
        self.issues.append(Issue(message, type, location, metadata))
    
    def add_error(self, message: str, location: Optional[str] = None, **metadata) -> None:
        """Add an error issue."""
        self.add_issue(message, IssueType.ERROR, location, **metadata)
    
    def add_warning(self, message: str, location: Optional[str] = None, **metadata) -> None:
        """Add a warning issue."""
        self.add_issue(message, IssueType.WARNING, location, **metadata)
    
    def add_info(self, message: str, location: Optional[str] = None, **metadata) -> None:
        """Add an info issue."""
        self.add_issue(message, IssueType.INFO, location, **metadata)
    
    def has_errors(self) -> bool:
        """Check if report contains any errors."""
        return any(issue.type == IssueType.ERROR for issue in self.issues)
    
    def has_warnings(self) -> bool:
        """Check if report contains any warnings."""
        return any(issue.type == IssueType.WARNING for issue in self.issues)
    
    def error_count(self) -> int:
        """Count number of errors."""
        return sum(1 for issue in self.issues if issue.type == IssueType.ERROR)
    
    def warning_count(self) -> int:
        """Count number of warnings."""
        return sum(1 for issue in self.issues if issue.type == IssueType.WARNING)
    
    def is_empty(self) -> bool:
        """Check if report has no issues."""
        return len(self.issues) == 0
    
    def __str__(self) -> str:
        """Format report as human-readable string."""
        if not self.issues:
            return "No issues found."
        
        lines = []
        if self.metadata:
            lines.append("Report Summary:")
            for key, value in self.metadata.items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        lines.append("Issues:")
        for issue in self.issues:
            lines.append(f"  {issue}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "issues": [
                {
                    "message": issue.message,
                    "type": issue.type.value,
                    "location": issue.location,
                    "metadata": issue.metadata
                }
                for issue in self.issues
            ],
            "metadata": self.metadata
        }