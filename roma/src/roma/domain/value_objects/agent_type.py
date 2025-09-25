"""
AgentType enumeration for ROMA v2.0

Defines the five agent types used in the ROMA framework:
- ATOMIZER: Determines if task needs decomposition
- PLANNER: Breaks complex tasks into subtasks
- EXECUTOR: Performs actual work (including RETRIEVE)
- AGGREGATOR: Combines results from subtasks
- PLAN_MODIFIER: Adjusts plans based on feedback
"""

from enum import Enum
from typing import Literal


class AgentType(str, Enum):
    """
    ROMA agent type enumeration for the 5-agent architecture.
    """

    ATOMIZER = "atomizer"  # Task decomposition decision
    PLANNER = "planner"  # Task breakdown into subtasks
    EXECUTOR = "executor"  # Atomic task execution
    AGGREGATOR = "aggregator"  # Result synthesis
    PLAN_MODIFIER = "plan_modifier"  # Plan adjustment and modification

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "AgentType":
        """
        Convert string to AgentType.

        Args:
            value: String representation of agent type

        Returns:
            AgentType enum value

        Raises:
            ValueError: If value is not a valid agent type
        """
        try:
            return cls(value.lower())
        except ValueError as e:
            valid_types = [t.value for t in cls]
            raise ValueError(f"Invalid agent type '{value}'. Valid types: {valid_types}") from e

    @property
    def is_atomizer(self) -> bool:
        """Check if this is an ATOMIZER agent type."""
        return self == AgentType.ATOMIZER

    @property
    def is_planner(self) -> bool:
        """Check if this is a PLANNER agent type."""
        return self == AgentType.PLANNER

    @property
    def is_executor(self) -> bool:
        """Check if this is an EXECUTOR agent type."""
        return self == AgentType.EXECUTOR

    @property
    def is_aggregator(self) -> bool:
        """Check if this is an AGGREGATOR agent type."""
        return self == AgentType.AGGREGATOR

    @property
    def is_plan_modifier(self) -> bool:
        """Check if this is a PLAN_MODIFIER agent type."""
        return self == AgentType.PLAN_MODIFIER


# Type hints for use in other modules
AgentTypeLiteral = Literal["atomizer", "planner", "executor", "aggregator", "plan_modifier"]
