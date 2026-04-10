"""Orchestration controllers — planner."""
from __future__ import annotations

import logging
import os
import json
from typing import List

logger = logging.getLogger(__name__)


def decompose_query(query: str) -> List[str]:
    """
    Break a user query into an ordered sequence of sub-tasks.
    Calls ChatOpenAI using generic Langchain if available.
    """
    logger.info("Planner decomposing query: %s", query)
    
    if os.getenv("OPENAI_API_KEY"):
        try:
            from langchain.chat_models import init_chat_model
            from langchain.schema import HumanMessage, SystemMessage
            
            llm = init_chat_model("gpt-3.5-turbo", model_provider="openai")
            prompt = f"Decompose the following user query into a sequence of tool execution steps. The query: '{query}'. Provide the steps as a JSON list of strings. Include 'web_search' in the step string if a web search is needed."
            
            response = llm.invoke([
                SystemMessage(content="You are a helpful planning assistant. Always respond with a valid JSON array of strings."), 
                HumanMessage(content=prompt)
            ])
            steps = json.loads(response.content)
            if isinstance(steps, list):
                return [str(s) for s in steps]
        except Exception as e:
            logger.warning(f"Failed to use LLM for planner, falling back to basic plan: {e}")
            
    return [
        f"web_search for relevant context for: {query}",
        "Identify key facts and constraints",
        "Synthesise a final, grounded answer",
    ]
