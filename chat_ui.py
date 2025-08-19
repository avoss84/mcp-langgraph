import random
from logging import Logger
from datetime import datetime
import requests
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from PIL import Image
from mcp_sandbox.services.logger import LoggerFactory


def get_logger() -> Logger:
    if "logger" not in st.session_state:
        st.session_state.logger = LoggerFactory(
            handler_type="Stream", verbose=True
        ).create_module_logger()
    return st.session_state.logger


def display_logo() -> None:
    try:
        logo = Image.open("data/NemetschekGroup_Black+Grey_Logo.png")
        st.image(logo, width=350)
    except FileNotFoundError:
        st.write("🤖 **MCP Chat Interface**")


def call_mcp_client(query: str, progress_bar=None, status_text=None) -> dict:
    """Call the MCP client and return the response with progress tracking."""
    logger = get_logger()

    if status_text:
        status_text.text("🔄 Sending query to MCP client...")
    if progress_bar:
        progress_bar.progress(10)

    try:
        # URL for local or dockerized MCP client
        # Try Docker service name first (for containerized deployment), then localhost (for development)
        urls_to_try = [
            "http://mcp-client:8080/calculate",  # Docker service-to-service communication (containerized)
            "http://localhost:8080/calculate",  # Local MCP client (development)
            "http://localhost:8081/calculate",  # Dockerized MCP client (host access)
        ]

        response = None
        used_url = None

        for url in urls_to_try:
            try:
                if status_text:
                    status_text.text(f"🔄 Trying {url}...")
                if progress_bar:
                    progress_bar.progress(30)

                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={"query": query},
                    timeout=60,
                    verify=False,
                )
                used_url = url
                break
            except requests.exceptions.ConnectionError:
                continue

        if not response:
            return {
                "error": "Could not connect to MCP client on any port (8000 or 8081). Make sure the client is running.",
                "status": "connection_error",
            }

        if status_text:
            status_text.text("🔄 Processing your query...")
        if progress_bar:
            progress_bar.progress(70)

        logger.info(f"Connected to MCP client at: {used_url}")
        logger.info(f"Response status: {response.status_code}")

        if progress_bar:
            progress_bar.progress(90)

        if response.status_code == 200:
            result = response.json()
            if status_text:
                status_text.text("✅ Query completed successfully!")
            if progress_bar:
                progress_bar.progress(100)

            return {
                "answer": result.get("answer", "No answer found"),
                "status": "success",
                "url_used": used_url,
                "response_time": response.elapsed.total_seconds(),
            }
        else:
            return {
                "error": f"MCP client returned error: {response.status_code} - {response.text}",
                "status": "api_error",
            }

    except requests.exceptions.Timeout:
        return {
            "error": "Request timed out. The MCP client is taking too long to respond.",
            "status": "timeout",
        }
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "status": "error"}


logger = get_logger()


# ------------------------------------------------------
def main():
    # App title and sidebar
    st.set_page_config(
        page_title="MCP Chat Interface",
        page_icon="🤖",
    )

    with st.sidebar:
        # Header with logo
        display_logo()
        st.title("MCP Agent Chat 💬")

        # Connection status
        st.subheader("🔗 Connection Status")
        if st.button("Test Connection"):
            with st.spinner("Testing connection..."):
                test_result = call_mcp_client("Hello", None, None)
                if test_result.get("status") == "success":
                    st.success(
                        f"✅ Connected to: {test_result.get('url_used', 'Unknown')}"
                    )
                else:
                    st.error(
                        f"❌ Connection failed: {test_result.get('error', 'Unknown error')}"
                    )

        # Example queries
        st.subheader("💡 Example Queries")
        example_queries = [
            # "What is 10 multiplied by 5?",
            "Calculate 20 + 15 and divide by 5",
            "Multiply 2 by 3, add 4, and square the result",
            # "What is 100 divided by 4?",
            "Calculate (5 + 3) * 2 and raise to power of 2",
        ]

        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.example_query = query

    # Store chat history as LangChain message objects
    if "messages" not in st.session_state:
        initial_message = random.choice(
            [
                "Hello! I'm your MCP Agent assistant. I can help you with mathematical calculations using both local tools (division, power) and MCP server tools (multiplication, addition).",
                "Hi! I'm connected to an MCP (Model Context Protocol) server. Ask me to perform calculations and I'll show you how I use different tools to solve them!",
                "Welcome! I can help you with math problems using my MCP tools. Try asking me to multiply, add, divide, or raise numbers to powers!",
            ]
        )
        st.session_state.messages = [AIMessage(content=initial_message)]

    # Handle example query selection
    if hasattr(st.session_state, "example_query"):
        st.session_state.messages.append(
            HumanMessage(content=st.session_state.example_query)
        )
        delattr(st.session_state, "example_query")
        st.rerun()

    # Display chat messages with enhanced formatting
    for i, message in enumerate(st.session_state.messages):
        role = "assistant" if isinstance(message, AIMessage) else "user"
        with st.chat_message(role):
            if (
                role == "assistant"
                and hasattr(message, "metadata")
                and message.metadata
            ):
                # Display metadata if available
                if message.metadata.get("url_used"):
                    st.caption(f"🔗 Connected to: {message.metadata['url_used']}")
                if message.metadata.get("response_time"):
                    st.caption(
                        f"⏱️ Response time: {message.metadata['response_time']:.2f}s"
                    )

            st.write(message.content)

            if role == "assistant":
                # Add feedback for assistant messages
                feedback = getattr(message, "feedback", None)
                st.session_state[f"feedback_{i}"] = feedback
                st.feedback(
                    "thumbs",
                    key=f"feedback_{i}",
                    disabled=feedback is not None,
                    on_change=lambda idx=i: save_feedback(idx),
                )

    # User input
    if prompt := st.chat_input("Ask me to perform calculations..."):
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.write(prompt)

    # Generate response if last message is from user
    if isinstance(st.session_state.messages[-1], HumanMessage):
        with st.chat_message("assistant"):
            # Create progress tracking elements
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Call MCP client with progress tracking
            query = st.session_state.messages[-1].content
            result = call_mcp_client(query, progress_bar, status_text)

            # Clear progress elements
            progress_bar.empty()
            status_text.empty()

            # Display result based on status
            if result.get("status") == "success":
                response_text = result["answer"]

                # Create metadata for the message
                metadata = {
                    "url_used": result.get("url_used"),
                    "response_time": result.get("response_time"),
                    "timestamp": datetime.now().isoformat(),
                }

                # # Display success info
                # st.success(
                #     f"✅ Query processed successfully in {result.get('response_time', 0):.2f}s"
                # )
                # st.info(f"🔗 Used: {result.get('url_used', 'Unknown endpoint')}")

                # Display the answer
                st.write(response_text)

                # Add to message history with metadata
                ai_message = AIMessage(content=response_text)
                ai_message.metadata = metadata
                st.session_state.messages.append(ai_message)

            else:
                # Handle errors
                error_message = (
                    f"❌ **Error:** {result.get('error', 'Unknown error occurred')}"
                )
                st.error(error_message)
                st.session_state.messages.append(AIMessage(content=error_message))

            # Add feedback option
            st.feedback(
                "thumbs",
                key=f"feedback_{len(st.session_state.messages)-1}",
                on_change=lambda idx=len(st.session_state.messages) - 1: save_feedback(
                    idx
                ),
            )


def save_feedback(index):
    """Save feedback for a message."""
    if f"feedback_{index}" in st.session_state:
        st.session_state.messages[index].feedback = st.session_state[
            f"feedback_{index}"
        ]


# ----------------------------
if __name__ == "__main__":
    main()
