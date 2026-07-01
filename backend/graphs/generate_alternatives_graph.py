from langgraph.graph import StateGraph
from langgraph.graph import END

from states.replacement_state import (
    ReplacementState
)

from nodes.load_task_node import (
    load_task_node
)

from nodes.load_plan_context_node import (
    load_plan_context_node
)

from nodes.generate_replacements_node import (
    generate_replacements_node
)


builder = StateGraph(
    ReplacementState
)

builder.add_node(
    "load_task",
    load_task_node
)

builder.add_node(
    "load_context",
    load_plan_context_node
)

builder.add_node(
    "generate_replacements",
    generate_replacements_node
)

builder.set_entry_point(
    "load_task"
)

builder.add_edge(
    "load_task",
    "load_context"
)

builder.add_edge(
    "load_context",
    "generate_replacements"
)

builder.add_edge(
    "generate_replacements",
    END
)

generate_alternatives_graph = builder.compile()