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

from nodes.update_task_node import (
    update_task_node
)

from nodes.save_task_history_node import (
    save_task_history_node
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
    "generate",
    generate_replacements_node
)

builder.add_node(
    "update",
    update_task_node
)

builder.add_node(
    "save",
    save_task_history_node
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
    "generate"
)

builder.add_edge(
    "generate",
    "update"
)

builder.add_edge(
    "update",
    "save"
)

builder.add_edge(
    "save",
    END
)

replacement_graph = builder.compile()