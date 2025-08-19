.PHONY: format type-check type-check-strict lint unit-test 
.PHONY: local-ui local-mcp-client local-mcp-server all-services stop-all-services
.PHONY: up-full down-full rm-all rm-all-full

ROOT_FOLDER ?= src/mcp_sandbox

# For local streamlit server
STREAMLIT_HOST ?= 127.0.0.1
STREAMLIT_PORT ?= 5001

# =============================================================================
# CODE QUALITY TARGETS
# =============================================================================

# Type checking with different strictness levels
type-check:
	uv run mypy $(ROOT_FOLDER)

type-check-strict:
	uv run mypy $(ROOT_FOLDER) --strict

# Code formatting only
format:
	uv run black $(ROOT_FOLDER)
	uv run ruff check $(ROOT_FOLDER) --fix

# Combined format and type check (lenient)
lint:
	uv run black $(ROOT_FOLDER)
	uv run ruff check $(ROOT_FOLDER) --fix
	uv run mypy $(ROOT_FOLDER)

# Run unit tests
unit-test:
	uv run pytest tests/ -v

# =============================================================================
# LOCAL SERVICE TARGETS
# =============================================================================

# Start local Streamlit UI
local-ui:
	uv run streamlit run ./chat_ui.py --server.address $(STREAMLIT_HOST) --server.port $(STREAMLIT_PORT)

# Start local MCP client
local-mcp-client:
	uv run ./app_mcp_client.py

# Start local MCP server
local-mcp-server:
	uv run $(ROOT_FOLDER)/resources/mcp_server.py

# Start all services locally (MCP server, client, and chat UI)
all-services: 
	@echo "🚀 Starting all services locally..."
	@echo "📝 MCP Server will run on stdio"
	@echo "🌐 MCP Client will run on http://localhost:8080"
	@echo "💬 Chat UI will run on http://$(STREAMLIT_HOST):$(STREAMLIT_PORT)"
	@echo "Starting MCP Server in background..."
	@nohup uv run $(ROOT_FOLDER)/resources/mcp_server.py > /dev/null 2>&1 & \
	sleep 2 && echo "Starting MCP Client in background..." && \
	nohup uv run ./app_mcp_client.py > /dev/null 2>&1 & \
	sleep 3 && echo "Starting Chat UI in foreground..." && \
	uv run streamlit run ./chat_ui.py --server.address $(STREAMLIT_HOST) --server.port $(STREAMLIT_PORT)

# Stop all locally running services
stop-all-services:
	@echo "🛑 Stopping all local services..."
	-pkill -f "uv run.*mcp_server.py" || true
	-pkill -f "uv run.*app_mcp_client.py" || true
	-pkill -f "uv run streamlit.*chat_ui.py" || true
	@echo "✅ All local services stopped"

# =============================================================================
# DOCKER TARGETS
# =============================================================================

# Start complete Docker stack (MCP client + server + chat UI)
up-full:
	docker compose up -d

# Stop complete Docker stack
down-full:
	docker compose down --volumes --remove-orphans

# Remove all Docker containers and images
rm-all:
	docker compose down --rmi all --volumes --remove-orphans

# Remove all Docker resources from full stack
rm-all-full:
	docker compose down --rmi all --volumes --remove-orphans
