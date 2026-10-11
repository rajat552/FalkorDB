from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# FalkorDB Database Configuration
FALKORDB_HOST = os.environ.get("FALKORDB_HOST", "127.0.0.1")
FALKORDB_PORT = int(os.environ.get("FALKORDB_PORT", "6379"))
FALKORDB_PASSWORD = os.environ.get("FALKORDB_PASSWORD", None)
FALKORDB_GRAPH = os.environ.get("FALKORDB_GRAPH", "company_brain")

# LLM Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "auto")  # 'openai', 'gemini', 'mock', 'auto'
DEFAULT_OPENAI_MODEL = os.environ.get("DEFAULT_OPENAI_MODEL", "gpt-4o")
DEFAULT_GEMINI_MODEL = os.environ.get("DEFAULT_GEMINI_MODEL", "gemini-1.5-flash-001")

# Document & Ingestion Configuration
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
ENTERPRISE_DATA_DIR = BASE_DIR / "data" / "enterprise"
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", "10"))
ALLOWED_EXTENSIONS = {".md", ".txt", ".pdf", ".json"}
CHUNK_SIZE_CHARS = int(os.environ.get("CHUNK_SIZE_CHARS", "800"))
CHUNK_OVERLAP_CHARS = int(os.environ.get("CHUNK_OVERLAP_CHARS", "150"))

# Server Configuration
SERVER_HOST = os.environ.get("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8000"))
