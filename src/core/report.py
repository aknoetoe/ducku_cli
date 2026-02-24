"""Report data structures for use case results."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List
import json
import html


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

    def to_json(self) -> str:
        """Convert report to JSON format."""
        return json.dumps({
            "issues": [
                {
                    "message": issue.message,
                    "type": issue.type.value,
                    "metadata": issue.metadata
                }
                for issue in self.issues
            ],
            "total_issues": len(self.issues)
        }, indent=2)

    def to_html(self) -> str:
        """Convert report to HTML format."""
        if not self.issues:
            return ""

        html_parts = ["<ul>"]
        for issue in self.issues:
            icon = "🔴" if issue.type == IssueType.ERROR else "⚠️"
            escaped_message = html.escape(issue.message)
            html_parts.append(f"  <li>{icon} {escaped_message}</li>")
        html_parts.append("</ul>")

        return "\n".join(html_parts)

    def format(self, format_type: str = "text") -> str:
        """Format the report according to the specified format type.

        Args:
            format_type: One of 'text', 'json', or 'html'

        Returns:
            Formatted report string
        """
        if format_type == "json":
            return self.to_json()
        elif format_type == "html":
            return self.to_html()
        else:  # text (default)
            return str(self)
