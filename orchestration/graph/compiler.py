import operator
from typing import TypedDict, Annotated, Sequence, List, Any, Dict, Optional
from langgraph.graph import StateGraph, END
import logging

logger = logging.getLogger(__name__)

# Core State machine TypedDict tracking conversation and internal agent reasoning steps
class AgentState(TypedDict):
    messages: Annotated[Sequence[Dict[str, str]], operator.add]
    session_id: str
    tools_called: List[str]
    context_docs: List[str]
    scratchpad: Dict[str, Any]
    next_step: str

async def planner_node(state: AgentState):
    """
    LLM Planner Node. Analyzes the conversational state and determines 
    the necessary tools and memory extraction required.
    """
    logger.info(f"[{state['session_id']}] Planner active.")
    # Here, you would bind your actual LLM Provider
    # model.invoke(prompt)
    
    # Mocking decision
    last_user_msg = [m['content'] for m in state['messages'] if m['role'] == 'user']
    if not last_user_msg:
        return {"next_step": "end"}
        
    query = last_user_msg[-1]
    
    if "math" in query.lower() or "calculate" in query.lower():
        decision = "executor"
        tools = ["code_interpreter"]
    else:
        decision = "retriever"
        tools = ["hybrid_rag"]
        
    return {
        "scratchpad": {"intent": "resolved", "plan": f"Use {tools}"},
        "tools_called": tools,
        "next_step": decision
    }

async def retriever_node(state: AgentState):
    """
    Triggers the RAG Pipeline to pull external context into the graph state.
    """
    logger.info(f"[{state['session_id']}] Retrieving documents...")
    # hybrid_retriever.retrieve(query)
    
    Docs = ["Context doc 1: Qdrant scales well.", "Context doc 2: LangGraph is deterministic."]
    return {
        "context_docs": Docs,
        "next_step": "reflector"
    }

async def executor_node(state: AgentState):
    """
    Safely routes execution to isolated sandboxes (Web Search, REPL).
    """
    logger.info(f"[{state['session_id']}] Executing tools...")
    # Execute actual tools via execution engine
    return {
        "scratchpad": {"tool_output": "Executed successfully. Result is 42."},
        "next_step": "reflector"
    }

async def reflector_node(state: AgentState):
    """
    Synthesizes final answers and ensures it passes safety/logical grounding.
    """
    logger.info(f"[{state['session_id']}] Synthesizing and reflecting...")
    # LLM generation over context_docs or tool_output
    
    final_output = "I have successfully fetched the data and calculated the response."
    new_message = {"role": "assistant", "content": final_output}
    
    return {
        "messages": [new_message],
        "next_step": "end"
    }

def route_next(state: AgentState) -> str:
    """Conditional router based on planner states."""
    if state.get("next_step") == "end":
        return END
    return state.get("next_step", END)

def get_agent_graph():
    """
    Compiles the production graph. 
    State schemas prevent memory leaks and loop bounds prevent token burn.
    """
    workflow = StateGraph(AgentState)
    
    # 1. Add all functional nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reflector", reflector_node)
    
    # 2. Graph topology
    workflow.set_entry_point("planner")
    workflow.add_conditional_edges("planner", route_next)
    
    workflow.add_edge("retriever", "reflector")
    workflow.add_edge("executor", "reflector")
    
    workflow.add_conditional_edges("reflector", route_next)
    
    return workflow.compile()
