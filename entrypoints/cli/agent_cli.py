"""
Command-line interface for the Agentic AI Production System.

This module provides a Click-based CLI with commands for:
- Asking questions to the agent (with streaming and verbose options)
- Ingesting documents for RAG
- Checking system health and status
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from typing import Any, Optional

import click
import requests
from loguru import logger
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner


# Configure logger for CLI
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <message>",
    level="INFO",
)

# Rich console for pretty output
console = Console()

# Default API configuration
DEFAULT_API_URL = "http://localhost:8000"


def get_api_url(ctx: click.Context) -> str:
    """
    Get API URL from context or environment.

    Args:
        ctx: Click context object.

    Returns:
        str: API base URL.
    """
    return ctx.obj.get("api_url", DEFAULT_API_URL) if ctx.obj else DEFAULT_API_URL


@click.group()
@click.option(
    "--api-url",
    envvar="AGENT_API_URL",
    default=DEFAULT_API_URL,
    help="Base URL of the Agentic AI API",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.pass_context
def cli(ctx: click.Context, api_url: str, verbose: bool) -> None:
    """
    Agentic AI Command-Line Interface.

    Interact with the Agentic AI production system directly from your terminal.
    Ask questions, ingest documents, and manage your AI assistant.

    Examples:

        \b
        # Ask a question
        agent ask "What is machine learning?"

        \b
        # Ask with verbose output
        agent ask --verbose "Explain neural networks"

        \b
        # Ingest a document
        agent ingest --type txt --content "Some text content"

        \b
        # Check system health
        agent health
    """
    ctx.ensure_object(dict)
    ctx.obj["api_url"] = api_url.rstrip("/")
    ctx.obj["verbose"] = verbose

    if verbose:
        logger.level("DEBUG")
        logger.debug("cli_initialized", api_url=api_url)


@cli.command("ask")
@click.argument("question")
@click.option(
    "--conversation-id",
    "-c",
    default=None,
    help="Conversation ID for multi-turn conversations",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed processing information",
)
@click.option(
    "--stream/--no-stream",
    default=True,
    help="Stream response tokens as they arrive",
)
@click.pass_context
def ask(
    ctx: click.Context,
    question: str,
    conversation_id: Optional[str],
    verbose: bool,
    stream: bool,
) -> None:
    """
    Ask a question to the Agentic AI assistant.

    QUESTION: The question or message to send to the agent.

    Examples:

        \b
        agent ask "What is the capital of France?"
        agent ask --verbose "Explain quantum computing"
        agent ask -c conv_123 "Follow-up question"
    """
    api_url = get_api_url(ctx)
    verbose = verbose or ctx.obj.get("verbose", False)

    logger.info(
        "ask_command_started",
        question_length=len(question),
        conversation_id=conversation_id,
        stream=stream,
    )

    if verbose:
        console.print(Panel(f"[bold blue]Question:[/bold blue] {question}"))
        console.print("[dim]Connecting to API...[/dim]")

    payload = {
        "message": question,
        "conversation_id": conversation_id,
    }

    try:
        if stream:
            _handle_streaming_response(api_url, payload, verbose)
        else:
            _handle_complete_response(api_url, payload, verbose)

    except requests.exceptions.ConnectionError:
        console.print(
            Panel(
                "[red]❌ Connection Error[/red]\n\n"
                f"Cannot connect to API at {api_url}\n"
                "Make sure the server is running.",
                border_style="red",
            )
        )
        sys.exit(1)
    except requests.exceptions.Timeout:
        console.print(
            Panel(
                "[red]❌ Timeout Error[/red]\n\n"
                "Request timed out. Please try again.",
                border_style="red",
            )
        )
        sys.exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"[red]❌ Error:[/red] {str(e)}",
                border_style="red",
            )
        )
        if verbose:
            logger.exception("ask_command_failed")
        sys.exit(1)


def _handle_streaming_response(
    api_url: str, payload: dict[str, Any], verbose: bool
) -> None:
    """
    Handle streaming chat response with live display.

    Args:
        api_url: Base API URL.
        payload: Request payload.
        verbose: Whether to show verbose output.
    """
    url = f"{api_url}/api/v1/chat/stream"

    start_time = time.time()
    full_response = ""
    chunk_count = 0

    if verbose:
        console.print("[dim]Streaming response...[/dim]")

    try:
        response = requests.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()

        # Use Rich Live display for streaming
        with Live(console=console, refresh_per_second=10) as live:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data: "):
                        try:
                            chunk_data = json.loads(decoded_line[6:])
                            chunk_text = chunk_data.get("chunk", "")
                            if chunk_text:
                                full_response += chunk_text
                                chunk_count += 1

                                # Update live display
                                md = Markdown(full_response + "▌")
                                live.update(
                                    Panel(
                                        md,
                                        title="[bold green]Assistant[/bold green]",
                                        border_style="green",
                                    )
                                )
                        except json.JSONDecodeError:
                            continue

        # Final display without cursor
        elapsed_ms = int((time.time() - start_time) * 1000)

        console.print()
        if verbose:
            console.print(
                f"[dim]Response complete: {chunk_count} chunks in {elapsed_ms}ms[/dim]"
            )

    except KeyboardInterrupt:
        console.print("\n[dim]Stream interrupted by user[/dim]")


def _handle_complete_response(
    api_url: str, payload: dict[str, Any], verbose: bool
) -> None:
    """
    Handle non-streaming (complete) chat response.

    Args:
        api_url: Base API URL.
        payload: Request payload.
        verbose: Whether to show verbose output.
    """
    url = f"{api_url}/api/v1/chat/complete"

    if verbose:
        console.print("[dim]Waiting for complete response...[/dim]")

    start_time = time.time()
    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()
    elapsed_ms = int((time.time() - start_time) * 1000)

    # Display response
    md = Markdown(data.get("message", ""))
    console.print(
        Panel(
            md,
            title="[bold green]Assistant[/bold green]",
            border_style="green",
        )
    )

    if verbose:
        console.print(
            f"\n[dim]"
            f"Conversation ID: {data.get('conversation_id', 'N/A')} | "
            f"Request ID: {data.get('request_id', 'N/A')} | "
            f"Latency: {elapsed_ms}ms"
            f"[/dim]"
        )


@cli.command("ingest")
@click.option(
    "--content",
    "-c",
    required=False,
    help="Raw text content to ingest",
)
@click.option(
    "--url",
    "-u",
    required=False,
    help="URL of the document to ingest",
)
@click.option(
    "--type",
    "-t",
    "doc_type",
    type=click.Choice(["txt", "pdf"]),
    default="txt",
    help="Document type",
)
@click.option(
    "--priority",
    "-p",
    type=click.Choice(["low", "normal", "high"]),
    default="normal",
    help="Processing priority",
)
@click.option(
    "--wait",
    "-w",
    is_flag=True,
    help="Wait for processing to complete",
)
@click.pass_context
def ingest(
    ctx: click.Context,
    content: Optional[str],
    url: Optional[str],
    doc_type: str,
    priority: str,
    wait: bool,
) -> None:
    """
    Ingest a document for RAG processing.

    Provide either --content (raw text) or --url (document URL).

    Examples:

        \b
        agent ingest --content "Some text to process"
        agent ingest --url https://example.com/doc.pdf --type pdf
        agent ingest -c "Text" -p high --wait
    """
    api_url = get_api_url(ctx)
    verbose = ctx.obj.get("verbose", False)

    if not content and not url:
        console.print(
            Panel(
                "[red]❌ Error[/red]\n\n"
                "Must provide either --content or --url",
                border_style="red",
            )
        )
        sys.exit(1)

    logger.info(
        "ingest_command_started",
        has_content=content is not None,
        has_url=url is not None,
        doc_type=doc_type,
        priority=priority,
    )

    payload = {
        "document_content": content,
        "document_url": url,
        "document_type": doc_type,
        "priority": priority,
    }

    try:
        response = requests.post(
            f"{api_url}/api/v1/ingest",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        task_id = data.get("task_id")

        console.print(
            Panel(
                f"[green]✅ Document Queued[/green]\n\n"
                f"[bold]Task ID:[/bold] `{task_id}`\n"
                f"[bold]Status:[/bold] {data.get('status')}\n"
                f"[bold]Estimated Time:[/bold] {data.get('estimated_time_seconds', 'N/A')}s",
                border_style="green",
            )
        )

        if wait and task_id:
            _wait_for_task(api_url, task_id, verbose)

    except requests.exceptions.RequestException as e:
        console.print(
            Panel(
                f"[red]❌ Ingestion Failed:[/red] {str(e)}",
                border_style="red",
            )
        )
        sys.exit(1)


def _wait_for_task(api_url: str, task_id: str, verbose: bool) -> None:
    """
    Wait for a task to complete with progress display.

    Args:
        api_url: Base API URL.
        task_id: Task identifier.
        verbose: Whether to show verbose output.
    """
    console.print(f"\n[dim]Waiting for task {task_id} to complete...[/dim]\n")

    max_wait = 300  # 5 minutes max
    elapsed = 0
    poll_interval = 2

    with Spinner("dots") as spinner:
        while elapsed < max_wait:
            try:
                response = requests.get(
                    f"{api_url}/api/v1/ingest/{task_id}",
                    timeout=10,
                )
                response.raise_for_status()

                data = response.json()
                status = data.get("status")
                progress = data.get("progress_percent", 0)

                if verbose:
                    spinner.update(text=f"Status: {status} | Progress: {progress}%")

                if status in ["completed", "failed", "cancelled"]:
                    break

                time.sleep(poll_interval)
                elapsed += poll_interval

            except requests.exceptions.RequestException:
                console.print("[red]Failed to check task status[/red]")
                return

    # Final status
    response = requests.get(f"{api_url}/api/v1/ingest/{task_id}", timeout=10)
    data = response.json()

    if data.get("status") == "completed":
        console.print(f"\n[green]✅ Task completed![/green]")
    elif data.get("status") == "failed":
        console.print(f"\n[red]❌ Task failed:[/red] {data.get('error', 'Unknown error')}")
    else:
        console.print(f"\n[yellow]⏸️ Task status:[/yellow] {data.get('status')}")


@cli.command("health")
@click.option(
    "--json-output",
    is_flag=True,
    help="Output health status as JSON",
)
@click.pass_context
def health(ctx: click.Context, json_output: bool) -> None:
    """
    Check the health status of the Agentic AI API.

    Examples:

        \b
        agent health
        agent health --json-output
    """
    api_url = get_api_url(ctx)

    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        response.raise_for_status()

        data = response.json()

        if json_output:
            click.echo(json.dumps(data, indent=2))
        else:
            status = data.get("status", "unknown")
            version = data.get("version", "N/A")
            timestamp = data.get("timestamp", "N/A")

            if status == "healthy":
                icon = "✅"
                style = "green"
            else:
                icon = "❌"
                style = "red"

            console.print(
                Panel(
                    f"[{style}]{icon} Status:[/{style}] [bold]{status}[/bold]\n\n"
                    f"[bold]Version:[/bold] {version}\n"
                    f"[bold]Timestamp:[/bold] {timestamp}",
                    border_style=style,
                )
            )

    except requests.exceptions.RequestException as e:
        if json_output:
            click.echo(json.dumps({"status": "unhealthy", "error": str(e)}))
        else:
            console.print(
                Panel(
                    f"[red]❌ API Unhealthy[/red]\n\n"
                    f"Cannot connect to {api_url}\n"
                    f"Error: {str(e)}",
                    border_style="red",
                )
            )
        sys.exit(1)


@cli.command("feedback")
@click.option(
    "--conversation-id",
    "-c",
    required=True,
    help="Conversation ID to provide feedback for",
)
@click.option(
    "--type",
    "-t",
    "feedback_type",
    type=click.Choice(["thumbs_up", "thumbs_down", "comment"]),
    required=True,
    help="Type of feedback",
)
@click.option(
    "--rating",
    "-r",
    type=click.IntRange(1, 5),
    help="Numeric rating (1-5)",
)
@click.option(
    "--comment",
    "-m",
    help="Text comment",
)
@click.pass_context
def feedback(
    ctx: click.Context,
    conversation_id: str,
    feedback_type: str,
    rating: Optional[int],
    comment: Optional[str],
) -> None:
    """
    Submit feedback for RLHF (Reinforcement Learning from Human Feedback).

    Examples:

        \b
        agent feedback -c conv_123 -t thumbs_up
        agent feedback -c conv_123 -t comment -m "Very helpful!"
    """
    api_url = get_api_url(ctx)

    payload = {
        "conversation_id": conversation_id,
        "feedback_type": feedback_type,
    }

    if rating is not None:
        payload["rating"] = rating
    if comment is not None:
        payload["comment"] = comment

    try:
        response = requests.post(
            f"{api_url}/api/v1/feedback",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        feedback_id = data.get("feedback_id")

        console.print(
            Panel(
                f"[green]✅ Feedback Submitted[/green]\n\n"
                f"[bold]Feedback ID:[/bold] `{feedback_id}`\n"
                f"[bold]Message:[/bold] {data.get('message')}",
                border_style="green",
            )
        )

    except requests.exceptions.RequestException as e:
        console.print(
            Panel(
                f"[red]❌ Feedback Failed:[/red] {str(e)}",
                border_style="red",
            )
        )
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
