"""Office source documents with an input-only reconstruction contract.

The private extraction map describes paths, scalar types and visible cell
locations. It contains no scenario values, answer values or calculation traces.
"""

from .documents import render_task, restore_scenario

__all__ = ["render_task", "restore_scenario"]
