"""
Base interface for TTS engines.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class TTSEngine(ABC):
    """Abstract base class for text-to-speech engines."""

    @abstractmethod
    def synthesize(
        self, text: str, voice: str, output_path: Path, speed_scale: float = 1.0
    ) -> None:
        """
        Synthesize text to speech.

        Args:
            text: The text to synthesize
            voice: Voice identifier for the engine
            output_path: Path where the audio file should be saved
            speed_scale: Speed multiplier (1.0 = normal, >1.0 = slower, <1.0 = faster)
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the TTS engine is available/installed."""
        pass

    @abstractmethod
    def get_engine_name(self) -> str:
        """Get the name of the TTS engine."""
        pass

    def validate_voice(self, voice: str) -> bool:
        """Validate if a voice is supported by this engine."""
        return True  # Default implementation - override in subclasses

    def get_supported_voices(self) -> Optional[list]:
        """Get list of supported voices for this engine."""
        return None  # Default implementation - override in subclasses
