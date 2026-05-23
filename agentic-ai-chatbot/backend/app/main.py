"""Backend entrypoint for local checks and module imports."""

from __future__ import annotations

from backend.app.agents.langgraph_backend import (
    chatbot,
    ingest_pdf,
    retrieve_all_threads,
    thread_document_metadata,
)


def main() -> None:
    """Print a concise readiness summary for the backend package."""
    threads = retrieve_all_threads()
    print("LangGraph backend package is ready.")
    print(f"Loaded threads: {len(threads)}")
    print("Run the Streamlit UI from frontend/streamlit/streamlit_frontend.py")


if __name__ == "__main__":
    main()