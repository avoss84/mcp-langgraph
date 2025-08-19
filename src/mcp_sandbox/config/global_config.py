import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Determine the environment: "vm" (local machine) or "docker" (container local or remote)
using = "vm"
# using = "docker"

package_root = Path(__file__).parent.parent.parent.parent

# --------------------------------------------------------
# Define defaults based on the environment
match using:
    case "vm":
        defaults = {
            "CODE_DIR": str(package_root / "src" / "mcp_sandbox"),
            "DATA_PKG_DIR": str(package_root / "data"),  # internal data folder
            "GCP_PROJECT": "neme-ai-rnd-dev-prj-01",
            "MODEL_PROVIDER": "google",  # ollama
        }
    case "docker":
        defaults = {
            "CODE_DIR": "/app/src/mcp_sandbox",
            "DATA_PKG_DIR": "/app/data/",
            "GCP_PROJECT": "neme-ai-rnd-dev-prj-01",
            "MODEL_PROVIDER": "google",
        }
    case _:
        raise ValueError(f"Unknown environment: {using}")

# -----------------------------------------------------------
# Set environment variables with defaults if not already set
for env, value in defaults.items():
    os.environ.setdefault(env, value)

CODE_DIR: str = os.environ["CODE_DIR"]
DATA_PKG_DIR: str = os.environ["DATA_PKG_DIR"]
GCP_PROJECT: str = os.environ["GCP_PROJECT"]
MODEL_PROVIDER: str = os.environ["MODEL_PROVIDER"]
