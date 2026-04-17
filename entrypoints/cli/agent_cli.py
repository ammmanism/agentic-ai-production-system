import click
import asyncio
import json
from typing import Optional

# Using a robust mock for the Agent until full graph integration is mapped
class Agent:
    def __init__(self, session_id=None, verbose=False):
        self.session_id = session_id
        self.verbose = verbose
    async def run(self, query):
        if self.verbose:
            click.echo(">> [Verbose] Running LangGraph nodes...")
        return f"Simulated semantic response for: {query}"
    def clear_memory(self):
        # Clears vector store / Redis context
        pass

@click.group()
def cli():
    """Elite Agent CLI – interact with your AI agent from the terminal."""
    pass

@cli.command()
@click.argument("query")
@click.option("--session-id", default=None, help="Resume a previous conversation session")
@click.option("--verbose", is_flag=True, help="Show detailed reasoning and steps")
def ask(query: str, session_id: Optional[str], verbose: bool):
    """Ask the agent a question, e.g. agent ask "How is the system architecture?" """
    agent = Agent(session_id=session_id, verbose=verbose)
    response = asyncio.run(agent.run(query))
    click.echo(f"\n🤖 Agent: {response}\n")

@cli.command()
@click.option("--session-id", required=True, help="Session ID to clear")
def clear(session_id: str):
    """Clear the memory of a specific session."""
    agent = Agent(session_id=session_id)
    agent.clear_memory()
    click.echo(f"✅ Session {session_id} cleared.")

if __name__ == "__main__":
    cli()
