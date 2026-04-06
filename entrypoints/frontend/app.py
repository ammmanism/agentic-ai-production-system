"""Gradio frontend — conversational UI for the Agentic AI system."""
from __future__ import annotations

import os
import time

try:
    import gradio as gr  # type: ignore
    HAS_GRADIO = True
except ImportError:
    HAS_GRADIO = False


def chat_fn(message: str, history: list) -> str:
    """Call the backend agent and return the answer."""
    try:
        import requests  # type: ignore

        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        resp = requests.post(
            f"{base_url}/chat/stream",
            json={"session_id": "gradio", "query": message, "stream": False},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("answer", "No answer returned.")
    except Exception as exc:  # noqa: BLE001
        # Fallback: return error message
        return f"⚠️ Error contacting agent API: {exc}"


def build_ui() -> "gr.Blocks":
    with gr.Blocks(title="Agentic AI Production System", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🧠 Agentic AI Production System")
        gr.Markdown("Ask anything — the agent will plan, retrieve, and synthesise an answer.")
        chatbot = gr.ChatInterface(
            fn=chat_fn,
            chatbot=gr.Chatbot(height=500),
            textbox=gr.Textbox(placeholder="Ask me anything…"),
            examples=[
                "What is LangGraph and why use it?",
                "How does hybrid RAG retrieval work?",
                "Calculate: (15 + 7) * 3",
            ],
        )
    return demo


if __name__ == "__main__":
    if not HAS_GRADIO:
        print("Install gradio: pip install gradio")
    else:
        ui = build_ui()
        ui.launch(server_port=7860, share=False)
