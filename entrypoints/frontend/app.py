"""
Streamlit Chat UI for the Agentic AI Production System.

This module provides an interactive chat interface that connects to the FastAPI
backend and displays streaming responses in real-time using Server-Sent Events.
"""

from __future__ import annotations

import json
import time
from typing import Any, Generator

import requests
import streamlit as st
from loguru import logger
from requests.models import Response


# Configure page settings
st.set_page_config(
    page_title="Agentic AI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Configure loguru (Streamlit compatible)
logger.remove()
logger.add(lambda msg: st.write(msg), level="INFO")

# API Configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")


def make_request_streaming(
    url: str, data: dict[str, Any], headers: dict[str, str] | None = None
) -> Generator[str, None, None]:
    """
    Make a streaming HTTP POST request and yield response chunks.

    Args:
        url: The API endpoint URL.
        data: Request payload as a dictionary.
        headers: Optional HTTP headers.

    Yields:
        str: Text chunks from the streaming response.

    Raises:
        requests.RequestException: If the request fails.
    """
    try:
        response = requests.post(url, json=data, headers=headers, stream=True, timeout=120)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if decoded_line.startswith("data: "):
                    chunk_data = decoded_line[6:]  # Remove "data: " prefix
                    try:
                        chunk_obj = json.loads(chunk_data)
                        chunk_text = chunk_obj.get("chunk", "")
                        if chunk_text:
                            yield chunk_text
                    except json.JSONDecodeError:
                        continue

    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        raise
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to the API server. Is it running?")
        raise
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e}")
        raise
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        raise


def send_feedback(
    conversation_id: str,
    feedback_type: str,
    rating: int | None = None,
    comment: str | None = None,
) -> dict[str, Any]:
    """
    Send user feedback to the API.

    Args:
        conversation_id: The conversation ID to provide feedback for.
        feedback_type: Type of feedback (thumbs_up, thumbs_down, comment).
        rating: Optional numeric rating (1-5).
        comment: Optional text comment.

    Returns:
        dict: Feedback response from the API.
    """
    url = f"{API_BASE_URL}/api/v1/feedback"
    payload = {
        "conversation_id": conversation_id,
        "feedback_type": feedback_type,
    }

    if rating is not None:
        payload["rating"] = rating
    if comment is not None:
        payload["comment"] = comment

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to submit feedback: {e}")
        return {"error": str(e)}


def ingest_document(
    document_content: str,
    document_type: str,
    priority: str = "normal",
) -> dict[str, Any]:
    """
    Submit a document for ingestion.

    Args:
        document_content: Raw text content of the document.
        document_type: Type of document (pdf or txt).
        priority: Processing priority (low, normal, high).

    Returns:
        dict: Ingestion response with task ID.
    """
    url = f"{API_BASE_URL}/api/v1/ingest"
    payload = {
        "document_content": document_content,
        "document_type": document_type,
        "priority": priority,
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to ingest document: {e}")
        return {"error": str(e)}


def check_health() -> dict[str, Any]:
    """
    Check the health status of the API.

    Returns:
        dict: Health status response.
    """
    url = f"{API_BASE_URL}/health"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"status": "unhealthy", "error": "Cannot connect to API"}


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False


# Sidebar
with st.sidebar:
    st.title("🤖 Agentic AI")
    st.markdown("Production-grade RAG-powered assistant")

    # Health check
    health_status = check_health()
    if health_status.get("status") == "healthy":
        st.success("✅ API Connected")
    else:
        st.error("❌ API Disconnected")

    st.divider()

    # Conversation controls
    st.subheader("Conversation")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.rerun()

    if st.session_state.conversation_id:
        st.info(f"**ID:** `{st.session_state.conversation_id}`")

    st.divider()

    # Document ingestion
    st.subheader("📄 Document Ingestion")
    with st.form("ingest_form"):
        doc_content = st.text_area(
            "Paste document text",
            height=100,
            placeholder="Enter document content here...",
        )
        doc_type = st.selectbox("Document Type", ["txt", "pdf"])
        doc_priority = st.selectbox("Priority", ["low", "normal", "high"])

        submit_ingest = st.form_submit_button("Ingest Document", use_container_width=True)
        if submit_ingest and doc_content:
            with st.spinner("Submitting document for processing..."):
                result = ingest_document(doc_content, doc_type, doc_priority)
                if "task_id" in result:
                    st.success(f"✅ Task ID: `{result['task_id']}`")
                    st.info(f"Estimated time: {result.get('estimated_time_seconds', 'N/A')}s")
                else:
                    st.error(f"Failed: {result.get('error', 'Unknown error')}")

    st.divider()

    # Settings
    st.subheader("⚙️ Settings")
    api_url_input = st.text_input("API Base URL", value=API_BASE_URL)
    if api_url_input != API_BASE_URL:
        st.session_state.API_BASE_URL = api_url_input
        st.rerun()


# Main chat area
st.title("💬 Chat with Agentic AI")
st.markdown("Ask questions and get intelligent, context-aware responses powered by RAG.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "timestamp" in message:
            st.caption(f"Generated at: {message['timestamp']}")

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        if not st.session_state.is_generating:
            st.session_state.is_generating = True

            # Prepare request payload
            payload = {
                "message": prompt,
                "conversation_id": st.session_state.conversation_id,
            }

            # Create placeholder for streaming response
            response_placeholder = st.empty()
            full_response = ""

            try:
                # Make streaming request
                start_time = time.time()
                for chunk in make_request_streaming(
                    url=f"{API_BASE_URL}/api/v1/chat/stream",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                ):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")

                # Display final response without cursor
                response_placeholder.markdown(full_response)

                # Calculate latency
                latency_ms = int((time.time() - start_time) * 1000)

                # Add assistant message to history
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": full_response,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "latency_ms": latency_ms,
                    }
                )

                # Update conversation ID if provided in response
                # (in production, extract from SSE metadata or headers)

            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                response_placeholder.markdown(error_message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_message, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
                )
            finally:
                st.session_state.is_generating = False

# Feedback section
if len(st.session_state.messages) > 1:
    st.divider()
    st.subheader("⭐ Provide Feedback")

    col1, col2, col3 = st.columns([1, 1, 3])

    with col1:
        if st.button("👍 Helpful", use_container_width=True):
            if st.session_state.conversation_id:
                result = send_feedback(st.session_state.conversation_id, "thumbs_up")
                if "feedback_id" in result:
                    st.success("Thanks for the feedback!")
                else:
                    st.error("Failed to submit feedback")

    with col2:
        if st.button("👎 Not Helpful", use_container_width=True):
            if st.session_state.conversation_id:
                result = send_feedback(st.session_state.conversation_id, "thumbs_down")
                if "feedback_id" in result:
                    st.success("Thanks for the feedback!")
                else:
                    st.error("Failed to submit feedback")

    with col3:
        feedback_comment = st.text_input("Additional comments", placeholder="Optional...")
        if feedback_comment and st.session_state.conversation_id:
            if st.button("Submit Comment"):
                result = send_feedback(
                    st.session_state.conversation_id,
                    "comment",
                    comment=feedback_comment,
                )
                if "feedback_id" in result:
                    st.success("Comment submitted!")
                else:
                    st.error("Failed to submit comment")

# Footer
st.divider()
st.caption(
    "Powered by Agentic AI Production System | "
    f"Messages: {len(st.session_state.messages)} | "
    f"Conversation: {st.session_state.conversation_id or 'New'}"
)
