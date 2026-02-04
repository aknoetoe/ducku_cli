from dataclasses import dataclass
from typing import Optional


@dataclass
class UseCaseResult:
    """Structured result from a use case analysis."""
    message: str
    critical: bool = False
    
    def __bool__(self) -> bool:
        """Return True if there are issues (non-empty message)."""
        return bool(self.message.strip())
    
    def __str__(self) -> str:
        """Return the message for backward compatibility."""
        return self.message
