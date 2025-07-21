"""
TTS engine factory for creating and managing different TTS engines.
"""

import subprocess
from typing import Dict, Type

from tts.base import TTSEngine
from tts.coqui import CoquiTTS
from tts.edge import EdgeTTS
from tts.openai import OpenAITTS
from tts.piper import PiperTTS


class TTSFactory:
    """Factory for creating TTS engine instances."""

    _engines: Dict[str, Type[TTSEngine]] = {
        "piper": PiperTTS,
        "edge": EdgeTTS,
        "openai": OpenAITTS,
        "coqui": CoquiTTS,
    }

    @classmethod
    def create_engine(cls, engine_name: str) -> TTSEngine:
        """Create a TTS engine instance."""
        if engine_name not in cls._engines:
            # Try legacy engines for backwards compatibility
            return cls._create_legacy_engine(engine_name)

        engine_class = cls._engines[engine_name]
        return engine_class()

    @classmethod
    def get_available_engines(cls) -> Dict[str, bool]:
        """Get availability status of all engines."""
        availability = {}

        # Check main engines
        for name, engine_class in cls._engines.items():
            try:
                engine = engine_class()
                availability[name] = engine.is_available()
            except Exception:
                availability[name] = False

        # Check legacy engines
        legacy_engines = ["say", "sapi", "espeak", "fish", "bark"]
        for name in legacy_engines:
            availability[name] = cls._check_legacy_engine(name)

        return availability

    @classmethod
    def _create_legacy_engine(cls, engine_name: str) -> TTSEngine:
        """Create legacy engine wrappers."""
        if engine_name == "say":
            return MacOSSayEngine()
        elif engine_name == "sapi":
            return WindowsSAPIEngine()
        elif engine_name == "espeak":
            return ESpeakEngine()
        elif engine_name == "fish":
            return FishSpeechEngine()
        elif engine_name == "bark":
            return BarkEngine()
        else:
            raise ValueError(f"Unknown TTS engine: {engine_name}")

    @classmethod
    def _check_legacy_engine(cls, engine_name: str) -> bool:
        """Check if a legacy engine is available."""
        try:
            if engine_name == "say":
                subprocess.run(["say", "--version"], check=True, capture_output=True)
                return True
            elif engine_name == "sapi":
                # Check if we're on Windows
                import platform

                return platform.system() == "Windows"
            elif engine_name == "espeak":
                subprocess.run(
                    ["espeak-ng", "--version"], check=True, capture_output=True
                )
                return True
            elif engine_name == "fish":
                # Would need to check if Fish Speech server is running
                return False  # Default to False for now
            elif engine_name == "bark":
                try:
                    import bark

                    return True
                except ImportError:
                    return False
        except:
            return False


# Legacy engine wrappers for backwards compatibility
class LegacyTTSEngine(TTSEngine):
    """Base class for legacy engine wrappers."""

    def is_available(self) -> bool:
        return True

    def validate_voice(self, voice: str) -> bool:
        return True


class MacOSSayEngine(LegacyTTSEngine):
    """macOS say command wrapper."""

    def synthesize(self, text: str, voice: str, output_path, speed_scale: float = 1.0):
        cmd = ["say", "-v", voice, "-o", str(output_path), text]
        if speed_scale != 1.0:
            # Convert speed_scale to words per minute (default ~200 wpm)
            rate = int(200 / speed_scale)
            cmd.extend(["-r", str(rate)])
        subprocess.run(cmd, check=True)

    def get_engine_name(self) -> str:
        return "say"


class WindowsSAPIEngine(LegacyTTSEngine):
    """Windows SAPI wrapper."""

    def synthesize(self, text: str, voice: str, output_path, speed_scale: float = 1.0):
        rate_attr = ""
        if speed_scale != 1.0:
            # SAPI rate: -10 to 10, where 0 is normal
            sapi_rate = max(-10, min(10, int((1.0 - speed_scale) * 10)))
            rate_attr = f"$speak.Rate={sapi_rate};"

        ps = (
            f"[void](Add-Type –AssemblyName System.speech);"
            f"$speak=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
            f'$speak.SelectVoice("{voice}");{rate_attr}'
            f'$speak.SetOutputToWaveFile("{output_path}");'
            f'$speak.Speak("{text}");'
        )
        subprocess.run(["powershell", "-Command", ps], check=True)

    def get_engine_name(self) -> str:
        return "sapi"


class ESpeakEngine(LegacyTTSEngine):
    """eSpeak-ng wrapper."""

    def synthesize(self, text: str, voice: str, output_path, speed_scale: float = 1.0):
        cmd = ["espeak-ng", "-v", voice, "-w", str(output_path), text]
        if speed_scale != 1.0:
            # eSpeak speed in words per minute
            speed_wpm = int(175 / speed_scale)  # Default ~175 wpm
            cmd.extend(["-s", str(speed_wpm)])
        subprocess.run(cmd, check=True)

    def get_engine_name(self) -> str:
        return "espeak"


class FishSpeechEngine(LegacyTTSEngine):
    """Fish Speech server wrapper."""

    def synthesize(self, text: str, voice: str, output_path, speed_scale: float = 1.0):
        import requests

        if speed_scale != 1.0:
            print(
                f"⚠️  Fish Speech doesn't support speed control. Speed scale {speed_scale} ignored."
            )

        resp = requests.post(
            "http://localhost:8000/tts", data={"text": text, "speaker": voice}
        )
        resp.raise_for_status()
        output_path.write_bytes(resp.content)

    def get_engine_name(self) -> str:
        return "fish"


class BarkEngine(LegacyTTSEngine):
    """Bark TTS wrapper."""

    def synthesize(self, text: str, voice: str, output_path, speed_scale: float = 1.0):
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models
            from scipy.io.wavfile import write as write_wav

            if speed_scale != 1.0:
                print(
                    f"⚠️  Bark doesn't support speed control. Speed scale {speed_scale} ignored."
                )

            # Preload models
            preload_models()

            # Generate audio
            audio_array = generate_audio(text, history_prompt=voice)

            # Save to file
            write_wav(str(output_path), SAMPLE_RATE, audio_array)

        except ImportError:
            raise RuntimeError(
                "Bark not installed. Install with: pip install git+https://github.com/suno-ai/bark.git"
            )

    def get_engine_name(self) -> str:
        return "bark"
