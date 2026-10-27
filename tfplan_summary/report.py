"""Parse Terraform plan JSON and render a concise change report."""

from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResourceChange:
    address: str
    actions: tuple[str, ...]

    @property
    def operation(self) -> str:
        action_set = set(self.actions)
        if action_set == {"create", "delete"}:
            return "replace"
        if len(self.actions) == 1 and self.actions[0] in {
            "create",
            "update",
            "delete",
            "no-op",
            "read",
        }:
            return self.actions[0]
        return "other"


@dataclass(frozen=True)
class PlanSummary:
    changes: tuple[ResourceChange, ...]

    @property
    def counts(self) -> Counter[str]:
        return Counter(change.operation for change in self.changes)

    @property
    def destructive_changes(self) -> tuple[ResourceChange, ...]:
        return tuple(
            change
            for change in self.changes
            if change.operation in {"delete", "replace"}
        )

    def render(self) -> str:
        counts = self.counts
        lines = [
            "Terraform plan summary",
            f"Resources changed: {len(self.changes)}",
            (
                f"Create: {counts['create']}  "
                f"Update: {counts['update']}  "
                f"Delete: {counts['delete']}  "
                f"Replace: {counts['replace']}"
            ),
        ]

        if self.destructive_changes:
            lines.append("\nDestructive changes:")
            for change in self.destructive_changes:
                label = "replace" if change.operation == "replace" else "delete"
                lines.append(f"  {label}: {change.address}")
        else:
            lines.append("\nNo resources will be destroyed.")

        other_changes = tuple(
            change for change in self.changes if change.operation not in {"delete", "replace"}
        )
        if other_changes:
            lines.append("\nOther changes:")
            for change in other_changes:
                lines.append(f"  {change.operation}: {change.address}")

        return "\n".join(lines)


def summarize_plan(plan: dict[str, Any]) -> PlanSummary:
    """Extract resource changes from a Terraform show -json document."""
    if not isinstance(plan, dict):
        raise ValueError("plan JSON must contain an object")

    raw_changes = plan.get("resource_changes", [])
    if raw_changes is None:
        raw_changes = []
    if not isinstance(raw_changes, list):
        raise ValueError("resource_changes must be a list")

    changes = []
    for item in raw_changes:
        if not isinstance(item, dict):
            raise ValueError("each resource change must be an object")

        change = item.get("change")
        if not isinstance(change, dict):
            raise ValueError("each resource change must contain a change object")

        address = item.get("address")
        actions = change.get("actions")
        if not isinstance(address, str) or not isinstance(actions, list):
            raise ValueError("each resource change needs an address and actions list")
        if not all(isinstance(action, str) for action in actions):
            raise ValueError("resource actions must be strings")
        if actions == ["no-op"]:
            continue

        changes.append(ResourceChange(address, tuple(actions)))

    return PlanSummary(tuple(changes))