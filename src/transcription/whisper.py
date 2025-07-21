"""
OpenAI Whisper transcription implementation.
"""

import subprocess
from pathlib import Path
from typing import Union

import openai
from tqdm import tqdm


class WhisperTranscriber:
    """Handles audio transcription using OpenAI Whisper."""

    def __init__(self, model: str = "whisper-1"):
        self.model = model

    def transcribe_audio(self, source: Union[Path, str], output_dir: Path) -> Path:
        """Download (if URL), transcribe with OpenAI Whisper; return transcript path."""
        print("🎧 Starting transcription process...")

        # Handle URL downloads
        if str(source).startswith("http"):
            audio_path = self._download_audio_from_url(str(source), output_dir)
        else:
            audio_path = Path(source)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Transcribe the audio
        transcript_text = self._transcribe_file(audio_path)

        # Save transcript
        transcript_path = output_dir / "podcast_transcript.txt"
        transcript_path.write_text(transcript_text, encoding="utf-8")
        print(f"✅ Transcript saved to {transcript_path}")

        return transcript_path

    def _download_audio_from_url(self, url: str, output_dir: Path) -> Path:
        """Download audio from URL using yt-dlp."""
        print("📥 Downloading audio from URL...")

        try:
            # Use yt-dlp to download the best audio format
            local_file = output_dir / "downloaded_audio.%(ext)s"
            with tqdm(desc="Downloading") as pbar:
                cmd = ["yt-dlp", "-f", "bestaudio", "-o", str(local_file), str(url)]
                subprocess.run(cmd, check=True, capture_output=True)
                pbar.update(1)

            # Find the actual downloaded file (yt-dlp determines extension)
            downloaded_files = list(output_dir.glob("downloaded_audio.*"))
            if not downloaded_files:
                raise RuntimeError("No audio file was downloaded")

            return downloaded_files[0]

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to download audio from URL: {e}")
        except FileNotFoundError:
            raise RuntimeError(
                "yt-dlp not found. Install with: pip install yt-dlp\n"
                "yt-dlp is required for downloading audio from URLs."
            )

    def _transcribe_file(self, audio_path: Path) -> str:
        """Transcribe audio file using OpenAI Whisper."""
        print(f"🎤 Transcribing audio with {self.model}...")

        try:
            with tqdm(desc="Transcription") as pbar:
                with open(audio_path, "rb") as audio_file:
                    response = openai.audio.transcriptions.create(
                        model=self.model, file=audio_file, response_format="text"
                    )
                pbar.update(1)

            return response

        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")

    def transcribe_with_timestamps(self, audio_path: Path) -> dict:
        """Transcribe with detailed timestamps and speaker detection."""
        print(f"🎤 Transcribing with timestamps using {self.model}...")

        try:
            with open(audio_path, "rb") as audio_file:
                response = openai.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word", "segment"],
                )

            return response

        except Exception as e:
            raise RuntimeError(f"Detailed transcription failed: {e}")
