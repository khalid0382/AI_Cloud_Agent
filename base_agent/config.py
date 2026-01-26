import os
import vertexai
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Cloud Project configuration
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# VertexAI init
vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)

# Model configuration
MODEL_NAME = "gemini-2.5-pro"

# Base directories
BASE_DIR = Path(__file__).parent.parent
