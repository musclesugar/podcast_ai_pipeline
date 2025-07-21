"""
Piper TTS implementation with auto-downloading.
"""

import subprocess
from pathlib import Path

import requests
from tqdm import tqdm

from config.settings import DOWNLOAD_CHUNK_SIZE, PIPER_BASE_URL, PIPER_DATA_DIR
from config.voices import parse_voice_name, suggest_voice_alternatives
from tts.base import TTSEngine


class PiperTTS(TTSEngine):
    """Piper TTS engine with automatic voice downloading."""

    from typing import Optional

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or PIPER_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(
        self, text: str, voice: str, output_path: Path, speed_scale: float = 1.0
    ) -> None:
        """Synthesize text using Piper TTS."""
        # Ensure voice is available
        model_path = self._ensure_voice_available(voice)

        try:
            # Build piper command with speed control
            cmd = [
                "piper",
                "--model",
                model_path,
                "--output_file",
                str(output_path),
                "--text",
                text,
            ]

            # Add length scale for speed control (>1.0 = slower, <1.0 = faster)
            if speed_scale != 1.0:
                cmd.extend(["--length_scale", str(speed_scale)])

            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Piper synthesis failed for voice '{voice}': {e.stderr}")
            alternatives = suggest_voice_alternatives(voice)
            print("\n💡 Try these alternative voices:")
            for alt in alternatives:
                alt_info = parse_voice_name(alt)
                print(f"   • {alt} ({alt_info['gender']} {alt_info['quality']})")
            raise

    def is_available(self) -> bool:
        """Check if Piper is available."""
        try:
            subprocess.run(["piper", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_engine_name(self) -> str:
        """Get engine name."""
        return "piper"

    def _ensure_voice_available(self, voice_name: str) -> str:
        """Ensure voice is available, downloading if necessary."""
        onnx_file = self.data_dir / f"{voice_name}.onnx"
        json_file = self.data_dir / f"{voice_name}.onnx.json"

        # Check if voice files already exist
        if onnx_file.exists() and json_file.exists():
            return str(onnx_file)

        # Download if needed
        return self._download_voice(voice_name)

    def _download_voice(self, voice_name: str) -> str:
        """Download Piper voice model if it doesn't exist."""
        print(f"📥 Downloading Piper voice: {voice_name}")
        voice_info = parse_voice_name(voice_name)
        print(
            f"   👤 {voice_info['gender'].title()} voice, {voice_info['quality']} quality"
        )

        onnx_file = self.data_dir / f"{voice_name}.onnx"
        json_file = self.data_dir / f"{voice_name}.onnx.json"

        try:
            # Parse voice name to build download path
            if voice_name.startswith("en_US-"):
                lang_path = "en/en_US"
                voice_parts = voice_name.replace("en_US-", "").rsplit("-", 1)
                if len(voice_parts) == 2:
                    voice_id, quality = voice_parts
                else:
                    voice_id = voice_parts[0]
                    quality = "medium"  # default
            elif voice_name.startswith("en_GB-"):
                lang_path = "en/en_GB"
                voice_parts = voice_name.replace("en_GB-", "").rsplit("-", 1)
                if len(voice_parts) == 2:
                    voice_id, quality = voice_parts
                else:
                    voice_id = voice_parts[0]
                    quality = "medium"
            else:
                raise ValueError(f"Unsupported voice format: {voice_name}")

            # Build download URLs
            voice_path = f"{lang_path}/{voice_id}/{quality}"
            onnx_url = f"{PIPER_BASE_URL}/{voice_path}/{voice_name}.onnx"
            json_url = f"{PIPER_BASE_URL}/{voice_path}/{voice_name}.onnx.json"

            # Download with progress
            with tqdm(desc="Downloading voice files", total=2) as pbar:
                # Download ONNX model
                pbar.set_description("Downloading model file")
                self._download_file(onnx_url, onnx_file)
                pbar.update(1)

                # Download JSON config
                pbar.set_description("Downloading config file")
                self._download_file(json_url, json_file)
                pbar.update(1)

            print(f"   ✅ Voice {voice_name} downloaded successfully")
            print(f"   📁 Saved to: {onnx_file}")
            return str(onnx_file)

        except Exception as e:
            print(f"   ❌ Failed to download {voice_name}: {e}")
            print(f"   💡 Manual download: https://huggingface.co/rhasspy/piper-voices")
            print("   💡 Popular alternatives you can try:")
            for voice in [
                "en_US-lessac-medium",
                "en_US-ryan-medium",
                "en_US-amy-medium",
            ]:
                if voice != voice_name:
                    print(
                        f'      --speakers \'{{"HOST":"{voice}", "GUEST":"{voice}"}}\''
                    )
            raise

    def _download_file(self, url: str, output_path: Path) -> None:
        """Download a file with error handling."""
        resp = requests.get(url, stream=True)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
