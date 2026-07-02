from langgraph.graph import (
    END,
    StateGraph
)

from nodes.intent_node import (
    intent_node
)

from nodes.planning_node import (
    planning_node
)

from nodes.tool_router_node import (
    tool_router_node
)

from nodes.response_node import (
    response_node
)

from states.supervisor_state import (
    SupervisorState
)

from nodes.context_builder_node import (
    context_builder_node
)

from nodes.load_memory_node import (
    load_memory_node
)

from nodes.save_memory_node import (
    save_memory_node
)

from nodes.summarize_memory_node import (
    summarize_memory_node
)

builder = StateGraph(

    SupervisorState

)

builder.add_node(
    "load_memory",
    load_memory_node
)

builder.add_node(

    "intent",

    intent_node

)

builder.add_node(

    "planning",

    planning_node

)

builder.add_node(

    "tool_router",

    tool_router_node

)

builder.add_node(

    "response",

    response_node

)

builder.add_node(
    "context_builder",
    context_builder_node
)

builder.add_node(
    "save_memory",
    save_memory_node
)

builder.add_node(
    "summarize_memory",
    summarize_memory_node
)

builder.set_entry_point(

    "load_memory"

)

builder.add_edge(
    "load_memory",
    "intent"
)

builder.add_edge(

    "intent",

    "planning"

)

builder.add_edge(

    "planning",

    "tool_router"

)

builder.add_edge(
    "tool_router",
    "context_builder"
)

builder.add_edge(
    "context_builder",
    "response"
)

builder.add_edge(
    "response",
    "save_memory"
)

builder.add_edge(
    "save_memory",
    "summarize_memory"
)

builder.add_edge(
    "summarize_memory",
    END
)

supervisor_graph = builder.compile()