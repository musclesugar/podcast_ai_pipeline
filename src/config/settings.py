"""
Configuration settings and constants for the podcast AI pipeline.
"""
import os
from pathlib import Path
from typing import Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API Configuration
OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
DEFAULT_GPT_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
DEFAULT_WHISPER_MODEL: str = os.getenv('WHISPER_MODEL', 'whisper-1')

# Audio Configuration
OUTPUT_FORMAT: str = os.getenv('OUTPUT_FORMAT', 'wav')
DEFAULT_SAMPLE_RATE: int = 22050
DEFAULT_CHANNELS: int = 1

# Speech Configuration
WPM_NATURAL: int = int(os.getenv('DEFAULT_WPM_NATURAL', '110'))
WPM_PROFESSIONAL: int = int(os.getenv('DEFAULT_WPM_PROFESSIONAL', '130'))
TTS_MULTIPLIER: float = 2.5  # TTS systems speak faster than humans

# Script Generation
MAX_WORDS_PER_BATCH: int = int(os.getenv('MAX_BATCH_SIZE', '1800'))
DEFAULT_TEMPERATURE_NATURAL: float = 0.8
DEFAULT_TEMPERATURE_PROFESSIONAL: float = 0.7

# File Paths
PIPER_DATA_DIR: Path = Path(os.getenv('PIPER_DATA_DIR', Path.home() / '.local' / 'share' / 'piper'))
DEFAULT_OUTPUT_DIR: str = 'output'  # Changed to use output/ directory

# Voice Download Configuration
PIPER_BASE_URL: str = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
DOWNLOAD_CHUNK_SIZE: int = 8192

# Validation
def validate_config() -> None:
    """Validate required configuration settings."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables or .env file. "
            "Please set it in your .env file or export it manually."
        )

# Audio format validation
SUPPORTED_FORMATS = ['wav', 'mp3', 'ogg', 'flac']
if OUTPUT_FORMAT not in SUPPORTED_FORMATS:
    raise ValueError(f"Unsupported output format: {OUTPUT_FORMAT}. Supported: {SUPPORTED_FORMATS}")

# Ensure data directory exists
PIPER_DATA_DIR.mkdir(parents=True, exist_ok=True)