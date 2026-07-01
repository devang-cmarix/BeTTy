from langgraph.graph import StateGraph
from langgraph.graph import END

from states.gap_analysis_state import (
    GapAnalysisState
)

from nodes.load_profile_node import (
    load_profile_node
)

from nodes.generate_gap_analysis_node import (
    generate_gap_analysis_node
)

from nodes.save_gap_analysis_node import (
    save_gap_analysis_node
)

builder = StateGraph(
    GapAnalysisState
)

builder.add_node(
    "load_profile",
    load_profile_node
)

builder.add_node(
    "generate_gap_analysis",
    generate_gap_analysis_node
)

builder.add_node(
    "save_gap_analysis",
    save_gap_analysis_node
)

builder.set_entry_point(
    "load_profile"
)

builder.add_edge(
    "load_profile",
    "generate_gap_analysis"
)

builder.add_edge(
    "generate_gap_analysis",
    "save_gap_analysis"
)

builder.add_edge(
    "save_gap_analysis",
    END
)

gap_analysis_graph = (
    builder.compile()
)