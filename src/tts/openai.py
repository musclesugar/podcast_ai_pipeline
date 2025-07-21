"""
OpenAI TTS implementation.
"""

from pathlib import Path
import openai

from config.voices import OPENAI_VOICES
from tts.base import TTSEngine


class OpenAITTS(TTSEngine):
    """OpenAI TTS engine (paid, premium quality)."""

    def synthesize(
        self, text: str, voice: str, output_path: Path, speed_scale: float = 1.0
    ) -> None:
        """Synthesize text using OpenAI TTS."""
        try:
            if speed_scale != 1.0:
                print(
                    f"⚠️  OpenAI TTS doesn't support speed control. Speed scale {speed_scale} ignored."
                )

            client = openai.OpenAI() # type: ignore

            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
            )

            response.stream_to_file(str(output_path))

        except Exception as e:
            raise RuntimeError(f"OpenAI TTS failed: {e}")

    def is_available(self) -> bool:
        """Check if OpenAI TTS is available."""
        try:
            client = openai.OpenAI() # type: ignore
            return bool(client.api_key)
        except Exception:
            return False

    def get_engine_name(self) -> str:
        """Get engine name."""
        return "openai"

    def validate_voice(self, voice: str) -> bool:
        """Validate OpenAI TTS voice."""
        return voice.lower() in OPENAI_VOICES

    def get_supported_voices(self) -> list:
        """Get list of supported OpenAI voices."""
        return list(OPENAI_VOICES.keys())
