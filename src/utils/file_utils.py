"""
File utilities for the podcast AI pipeline.
"""

import json
from pathlib import Path
from typing import Any, Dict


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Save data as JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: Path) -> Dict[str, Any]:
    """Load data from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_json_arg(json_string: str, arg_name: str) -> Dict[str, str]:
    """Parse JSON string argument with error handling."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing {arg_name} JSON: {e}")


def get_file_size_mb(filepath: Path) -> float:
    """Get file size in megabytes."""
    return filepath.stat().st_size / (1024 * 1024)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename.strip()


def get_audio_duration(filepath: Path) -> float:
    """Get audio duration in seconds using pydub."""
    try:
        from pydub import AudioSegment

        audio = AudioSegment.from_file(filepath)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except Exception as e:
        raise RuntimeError(f"Could not determine audio duration: {e}")


def validate_output_format(format_name: str) -> str:
    """Validate and normalize audio output format."""
    format_name = format_name.lower().strip(".")
    supported_formats = ["wav", "mp3", "ogg", "flac", "m4a"]

    if format_name not in supported_formats:
        raise ValueError(
            f"Unsupported format '{format_name}'. Supported: {supported_formats}"
        )

    return format_name
