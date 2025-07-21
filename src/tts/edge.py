"""
Microsoft Edge TTS implementation.
"""

import asyncio
from pathlib import Path

from tts.base import TTSEngine


class EdgeTTS(TTSEngine):
    """Microsoft Edge TTS engine (free, cloud-based)."""

    def synthesize(
        self, text: str, voice: str, output_path: Path, speed_scale: float = 1.0
    ) -> None:
        """Synthesize text using Microsoft Edge TTS."""
        try:
            import edge_tts

            async def generate():
                # Apply speed control through SSML if not normal speed
                if speed_scale != 1.0:
                    # Convert speed_scale to percentage (Edge TTS uses rate)
                    rate_percent = int((speed_scale - 1.0) * 100)
                    if rate_percent != 0:
                        rate_str = f"{rate_percent:+d}%"
                        text_with_rate = f'<prosody rate="{rate_str}">{text}</prosody>'
                    else:
                        text_with_rate = text
                else:
                    text_with_rate = text

                communicate = edge_tts.Communicate(text_with_rate, voice)
                await communicate.save(str(output_path))

            asyncio.run(generate())

        except ImportError:
            raise RuntimeError(
                "Edge TTS not installed. Install with: pip install edge-tts\n"
                "Edge TTS provides free, high-quality voices from Microsoft."
            )
        except Exception as e:
            raise RuntimeError(f"Edge TTS synthesis failed: {e}")

    def is_available(self) -> bool:
        """Check if Edge TTS is available."""
        try:
            import edge_tts

            return True
        except ImportError:
            return False

    def get_engine_name(self) -> str:
        """Get engine name."""
        return "edge"

    def validate_voice(self, voice: str) -> bool:
        """Validate Edge TTS voice format."""
        # Edge TTS voices typically follow pattern: en-US-VoiceNeural
        return "Neural" in voice and "-" in voice
