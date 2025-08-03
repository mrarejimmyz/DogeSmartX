"""
Complete AVAI (Avishek's Very Awesome Intelligence) Agent System with Full Tool Integration
Optimized for local GGUF models while maintaining all functionality.
Dedicated to our beloved brother Avishek.
"""

import argparse
import asyncio
import os
import sys
import time
import signal
import threading
import traceback
from pathlib import Path
from typing import Optional

# Global state for shutdown coordination
_shutdown_event = threading.Event()
_cleanup_lock = threading.Lock()
_cleanup_in_progress = False

def handle_shutdown_signal(signum, frame):
    """Handle shutdown signals gracefully."""
    global _cleanup_in_progress
    
    # Use lock to prevent multiple threads from running cleanup simultaneously
    with _cleanup_lock:
        if _cleanup_in_progress:
            print("\n⚠️ Forced shutdown requested, terminating immediately...")
            sys.exit(1)
            
        _cleanup_in_progress = True
        try:
            print("\n🛑 Shutdown signal received, cleaning up...")
            _shutdown_event.set()
            
            # Give cleanup some time to complete
            time.sleep(2)
            
            print("✅ Cleanup completed, exiting...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error during shutdown: {e}")
            sys.exit(1)

# Auto-activate virtual environment if not already active
def ensure_virtual_environment():
    """Ensure virtual environment is activated and all dependencies are available."""
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # Already in virtual environment
        return True
    
    # Find project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir
    
    # Look for virtual environment
    venv_paths = [
        project_root / "venv",
        project_root / ".venv", 
        project_root / "env",
        project_root / ".env"
    ]
    
    venv_path = None
    for path in venv_paths:
        if path.exists() and (path / "Scripts" / "python.exe").exists():
            venv_path = path
            break
    
    if venv_path:
        # Activate virtual environment by modifying PATH and VIRTUAL_ENV
        venv_scripts = str(venv_path / "Scripts")
        venv_python = str(venv_path / "Scripts" / "python.exe")
        
        # Update environment variables
        os.environ["VIRTUAL_ENV"] = str(venv_path)
        os.environ["PATH"] = f"{venv_scripts};{os.environ.get('PATH', '')}"
        
        # Update sys.path to use venv packages
        site_packages = venv_path / "Lib" / "site-packages"
        if site_packages.exists():
            sys.path.insert(0, str(site_packages))
        
        print(f"🚀 Auto-activated virtual environment: {venv_path}")
        return True
    else:
        print("⚠️ No virtual environment found. Please create one with:")
        print("   python -m venv venv")
        print("   venv\\Scripts\\activate")
        print("   pip install -r requirements.txt")
        return False

# Ensure virtual environment is activated before importing dependencies
if not ensure_virtual_environment():
    sys.exit(1)

# Install signal handlers
signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)

# Conditional imports for logging
try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

# Import AVAI components to check availability
try:
    from app.agent.browser import BrowserAgent
    from app.agent.code import CodeAgent
    from app.agent.avai_core import Avai
    from app.config import Config as AVAIConfig
    from app.llm import create_llm
    from app.memory import Memory
    from app.schema import AgentState, Message
    AVAI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"AVAI components not fully available: {e}")
    AVAI_AVAILABLE = False

# Import the actual functionality
try:
    from app.agent_router import route_agent
    from app.agent_wrappers import create_agent
    from app.config import Config, load_config
    from app.main_utils import (check_and_process_todo, display_startup_info,
                                initialize_system, process_prompt)
except ImportError as e:
    logger.error(f"Failed to import core modules: {e}")
    logger.error("Please ensure all dependencies are installed:")
    logger.error("pip install -r requirements.txt")
    sys.exit(1)


async def main():
    """Main entry point with full functionality."""
    parser = argparse.ArgumentParser(description="AVAI (Avishek's Very Awesome Intelligence) Agent - Complete System")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--prompt", type=str, help="Input prompt")
    parser.add_argument(
        "--no-wait", action="store_true", help="Exit immediately if no prompt"
    )
    parser.add_argument(
        "--agent", type=str, help="Specify agent (avai, code, browser, file, planner)"
    )
    parser.add_argument(
        "--api-type", type=str, choices=["local", "ollama"], help="Override API type"
    )
    parser.add_argument("--simple", action="store_true", help="Use simple agents only")
    parser.add_argument("--workspace", type=str, help="Workspace directory")
    parser.add_argument("--max-steps", type=int, help="Maximum agent steps")
    parser.add_argument("--no-healing", action="store_true", help="Skip AI healing analysis for faster startup")
    args = parser.parse_args()

    try:
        config, llm, memory = initialize_system(args)
        display_startup_info(config, args, AVAI_AVAILABLE)

        processed_cmd_prompt = False

        # Process command line prompt first if provided
        if args.prompt:
            logger.info(f"📝 Processing command line prompt: {args.prompt[:100]}...")
            await process_prompt(
                args.prompt, args, llm, config, memory, AVAI_AVAILABLE
            )
            processed_cmd_prompt = True
            if args.no_wait:
                return

        # Check for todo.md and auto-start if found (only if no command line prompt)
        if not args.prompt:
            auto_started = await check_and_process_todo(
                args, llm, config, memory, AVAI_AVAILABLE
            )

        # Interactive mode for additional prompts
        while not _shutdown_event.is_set():
            prompt = None
            if sys.stdin.isatty():
                try:
                    prompt = input("\n💬 Enter your prompt (or 'quit' to exit): ")
                    if prompt.lower() in ["quit", "exit", "bye", "q"]:
                        break
                except (EOFError, KeyboardInterrupt):
                    if args.no_wait:
                        break
                    continue
            else:
                if args.no_wait:
                    break
                time.sleep(5)
                continue

            if prompt:
                await process_prompt(
                    prompt, args, llm, config, memory, AVAI_AVAILABLE
                )

    except Exception as e:
        logger.error(f"An unhandled error occurred: {e}")
        logger.error(traceback.format_exc())
    finally:
        if "memory" in locals() and memory:
            memory.save_session()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user, cleaning up...")
        _shutdown_event.set()
        time.sleep(2)  # Give cleanup time to complete
        sys.exit(0)
