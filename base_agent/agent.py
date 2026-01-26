"""Top level agent"""

import base64
import json
import logging
import os
from datetime import date
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools import load_artifacts

from google.genai import types

from .prompts import return_instructions_root

# --- Logging setup ----------------------------------------------------------

import google.cloud.logging

IS_RUNNING_IN_GCP = os.getenv("K_SERVICE") is not None

if IS_RUNNING_IN_GCP:
    # In Agent Engine / Cloud Run
    client = google.cloud.logging.Client()
    client.setup_logging()
    logging.basicConfig(level=logging.INFO)
    logging.info("Running in GCP. Configured Google Cloud Logging.")
else:
    # Local dev (adk web, etc.)
    logging.basicConfig(level=logging.INFO)
    logging.info("Running locally. Using basic console logging.")

logger = logging.getLogger(__name__)
logger.info("Libraries imported and logging configured.")

# --- Root Agent Definition ----------------------------------------------------

def get_root_agent() -> LlmAgent:
    tools = []
    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-pro"),
        name="base_root_agent",
        instruction=return_instructions_root(),
        tools=tools,  # type: ignore
        generate_content_config=types.GenerateContentConfig(temperature=0.01),
    )

    return agent


# Fetch the root agent
root_agent = get_root_agent()