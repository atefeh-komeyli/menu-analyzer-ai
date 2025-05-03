import argparse
import os
import logging
import uvicorn
from dotenv import load_dotenv
from api import app as fastapi_app
from gradio_ui import build_ui

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("menu_analyzer")

load_dotenv()

if "OPENAI_API_KEY" not in os.environ:
    logger.error("OPENAI_API_KEY environment variable not set")
    raise EnvironmentError("OPENAI_API_KEY must be set as an environment variable")

# Constants
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
MAX_QUESTIONS = 5
MAX_MENU_ITEMS = 100


def run_gradio(host=DEFAULT_HOST, port=DEFAULT_PORT, share=False):
    """Start the Gradio web interface"""
    logger.info(f"Starting Gradio web interface on {host}:{port}")
    app = build_ui()  # Use build_ui from renamed gradio_ui.py
    app.launch(server_name=host, server_port=int(port), share=share)


def run_api(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Start the FastAPI server"""
    logger.info(f"Starting FastAPI server on {host}:{port}")
    uvicorn.run(fastapi_app, host=host, port=int(port))


def main():
    parser = argparse.ArgumentParser(
        description="Menu Analyzer AI - Run in Gradio or API mode"
    )
    parser.add_argument(
        "--mode",
        choices=["gradio", "api"],
        default="gradio",
        help="Run mode: 'gradio' for web interface or 'api' for API server",
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST, help=f"Host address (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port", default=DEFAULT_PORT, help=f"Port number (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public URL for sharing the Gradio interface",
    )
    args = parser.parse_args()

    # Start the application in the selected mode
    if args.mode == "gradio":
        run_gradio(host=args.host, port=args.port, share=args.share)
    else:  # args.mode == "api"
        run_api(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
