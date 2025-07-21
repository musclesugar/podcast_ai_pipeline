"""
Coqui TTS implementation with voice cloning support.
"""

import logging
import os
from pathlib import Path

from tts.base import TTSEngine


class CoquiTTS(TTSEngine):
    """Coqui TTS engine (free, advanced neural TTS with voice cloning)."""

    def __init__(self):
        # Suppress verbose Coqui logging
        logging.getLogger("TTS").setLevel(logging.ERROR)
        logging.getLogger("trainer").setLevel(logging.ERROR)
        os.environ["TTS_LOG_LEVEL"] = "ERROR"

        # Fix PyTorch 2.6 compatibility
        self._setup_pytorch_compatibility()

    def synthesize(
        self, text: str, voice: str, output_path: Path, speed_scale: float = 1.0
    ) -> None:
        """Synthesize text using Coqui TTS."""
        try:
            from TTS.api import TTS

            # Handle different voice formats
            if "|" in voice:
                # Format: "model_name|speaker_name"
                model_name, speaker_name = voice.split("|", 1)
            elif voice.startswith("xtts"):
                # XTTS-v2 voice cloning format
                model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
                speaker_name = voice.replace("xtts_", "")
            else:
                model_name = voice
                speaker_name = None

            # Note: Coqui TTS doesn't support speed control directly
            if speed_scale != 1.0:
                print(
                    f"⚠️  Coqui TTS doesn't support speed control. Speed scale {speed_scale} ignored."
                )

            # Initialize TTS with the specified model
            tts = TTS(model_name=model_name)

            # Handle XTTS-v2 voice cloning
            if "xtts" in model_name.lower():
                # XTTS-v2 supports voice cloning from reference audio
                if speaker_name in ["aaron_dreschner", "ana_florence"]:
                    # These would need reference audio files, for now use default speakers
                    # In practice, you'd provide: speaker_wav="path/to/reference.wav"
                    tts.tts_to_file(
                        text=text, file_path=str(output_path), language="en"
                    )
                else:
                    tts.tts_to_file(
                        text=text, file_path=str(output_path), language="en"
                    )
            # Handle multi-speaker models
            elif speaker_name and hasattr(tts, "speakers") and tts.speakers:
                tts.tts_to_file(
                    text=text, file_path=str(output_path), speaker=speaker_name
                )
            elif hasattr(tts, "speakers") and tts.speakers:
                # Multi-speaker model, use first available speaker
                first_speaker = tts.speakers[0] if tts.speakers else None
                if first_speaker:
                    tts.tts_to_file(
                        text=text, file_path=str(output_path), speaker=first_speaker
                    )
                else:
                    tts.tts_to_file(text=text, file_path=str(output_path))
            else:
                # Single speaker model
                tts.tts_to_file(text=text, file_path=str(output_path))

        except ImportError:
            raise RuntimeError(
                "Coqui TTS not installed. Install with: pip install TTS\n"
                "Coqui TTS provides advanced neural voices with voice cloning capabilities."
            )
        except Exception as e:
            if "weights_only" in str(e) or "WeightsUnpickler" in str(e):
                raise RuntimeError(
                    f"PyTorch compatibility issue with Coqui TTS. Try: "
                    f"1) Downgrade PyTorch: pip install torch==2.0.1, or "
                    f'2) Use Edge TTS instead: --engines \'{{"HOST":"edge","GUEST":"edge"}}\''
                )
            else:
                raise RuntimeError(f"Coqui TTS error: {e}")

    def is_available(self) -> bool:
        """Check if Coqui TTS is available."""
        try:
            from TTS.api import TTS

            return True
        except ImportError:
            return False

    def get_engine_name(self) -> str:
        """Get engine name."""
        return "coqui"

    def _setup_pytorch_compatibility(self):
        """Setup PyTorch compatibility for newer versions."""
        try:
            import torch

            # Add safe globals for XTTS compatibility
            from TTS.tts.configs.xtts_config import XttsConfig
            from TTS.utils.audio.processor import AudioProcessor
            torch.serialization.add_safe_globals(
                [
                    (XttsConfig, "TTS.tts.configs.xtts_config.XttsConfig"),
                    (AudioProcessor, "TTS.utils.audio.processor.AudioProcessor"),
                ]
            )
        except:
            pass  # Fallback for older PyTorch versions
