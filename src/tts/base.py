"""
Base interface for TTS engines.
"""
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

class TTSEngine(ABC):
    """Abstract base class for text-to-speech engines."""
    
    @abstractmethod
    def synthesize(self, text: str, voice: str, output_path: Path, speed_scale: float = 1.0) -> None:
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
    
    def clean_text_for_tts(self, text: str) -> str:
        """Clean text of SSML artifacts, markdown, and other TTS-unfriendly content."""
        # Remove broken SSML tags that might be getting read aloud
        text = re.sub(r'\*\*\s*/?prosody[^*]*\*\*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\*\*\s*/?procity[^*]*\*\*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</?prosody[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</?speak[^>]*>', '', text, flags=re.IGNORECASE)
        
        # Remove markdown formatting that TTS might read
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
        text = re.sub(r'`([^`]+)`', r'\1', text)        # `code` -> code
        
        # Remove any remaining asterisks or markup
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'#+\s*', '', text)  # Remove markdown headers
        
        # Clean up multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text