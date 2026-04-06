from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import planner_node, executor_node, reflector_node

def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reflector", reflector_node)
    
    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges(
        "executor",
        lambda state: "reflector" if state.needs_replan else END,
    )
    graph.add_edge("reflector", "planner")
    
    return graph.compile()
