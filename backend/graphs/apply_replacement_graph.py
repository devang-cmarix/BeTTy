from langgraph.graph import StateGraph
from langgraph.graph import END

from states.replacement_state import (
    ReplacementState
)

from nodes.load_task_node import (
    load_task_node
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
    "update_task",
    update_task_node
)

builder.add_node(
    "save_history",
    save_task_history_node
)

builder.set_entry_point(
    "load_task"
)

builder.add_edge(
    "load_task",
    "update_task"
)

builder.add_edge(
    "update_task",
    "save_history"
)

builder.add_edge(
    "save_history",
    END
)

apply_replacement_graph = builder.compile()