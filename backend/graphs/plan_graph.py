from langgraph.graph import (
    StateGraph,
    END
)

from states.plan_state import (
    PlanState
)

from nodes.load_user_node import (
    load_user_node
)

from nodes.generate_task_chunks_node import (
    generate_task_chunks_node
)

from nodes.assemble_plan_node import (
    assemble_plan_node
)

from nodes.save_plan_node import (
    save_plan_node
)

builder = StateGraph(
    PlanState
)

builder.add_node(
    "load_user",
    load_user_node
)

builder.add_node(
    "generate_task_chunks",
    generate_task_chunks_node
)

builder.add_node(
    "assemble_plan",
    assemble_plan_node
)

builder.add_node(
    "save_plan",
    save_plan_node
)

builder.set_entry_point(
    "load_user"
)

builder.add_edge(
    "load_user",
    "generate_task_chunks"
)

builder.add_edge(
    "generate_task_chunks",
    "assemble_plan"
)

builder.add_edge(
    "assemble_plan",
    "save_plan"
)

builder.add_edge(
    "save_plan",
    END
)

plan_graph = builder.compile()