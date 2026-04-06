"""CLI entrypoint — `agent ask "your query"`"""
from __future__ import annotations

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Agentic AI CLI")
    sub = parser.add_subparsers(dest="command")

    # agent ask "query"
    ask_parser = sub.add_parser("ask", help="Ask the agent a question")
    ask_parser.add_argument("query", help="Natural language query")
    ask_parser.add_argument("--session", default="cli-session", help="Session ID")

    args = parser.parse_args()

    if args.command == "ask":
        from orchestration.graph.state import AgentState
        from orchestration.graph.nodes import planner_node, executor_node

        state = AgentState(
            query=args.query,
            messages=[],
            plan=None,
            current_step=0,
            tool_results=[],
            final_answer=None,
            needs_replan=False,
            replan_count=0,
            context=None,
            metadata={"session_id": args.session},
        )

        print(f"🤔 Planning: {args.query}")
        state = planner_node(state)
        print(f"📋 Plan: {state['plan']}")

        while state["final_answer"] is None:
            state = executor_node(state)

        print(f"\n💡 Answer: {state['final_answer']}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
