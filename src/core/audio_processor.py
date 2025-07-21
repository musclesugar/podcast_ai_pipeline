"""
Audio processing and assembly for podcast generation.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from pydub import AudioSegment
from tqdm import tqdm

from config.settings import OUTPUT_FORMAT, PIPER_DATA_DIR
from core.script_parser import ScriptParser
from tts.factory import TTSFactory


class AudioProcessor:
    """Handles audio synthesis and assembly."""

    def __init__(self):
        self.script_parser = ScriptParser()
        self.tts_factory = TTSFactory()

    def process_script_to_audio(
        self,
        script: str,
        speaker_voices: Dict[str, str],
        speaker_engines: Dict[str, str],
        output_path: Path,
        target_minutes: Optional[int] = None,
        speed_scale: float = 1.0,
    ) -> None:
        """Process script and generate final audio file."""
        print("\n🎙️  Processing audio synthesis...")

        # Validate and parse the script
        expected_speakers = list(speaker_voices.keys())
        dialogue_lines = self.script_parser.validate_and_preview_script(
            script, expected_speakers
        )

        # Pre-download all required Piper voices to avoid repeated messages
        self._predownload_piper_voices(speaker_voices, speaker_engines)

        # Generate audio clips
        audio_clips = self._generate_audio_clips(
            dialogue_lines, speaker_voices, speaker_engines, speed_scale
        )

        # Combine audio clips
        final_audio = self._combine_audio_clips(audio_clips)

        # Export final audio
        self._export_audio(final_audio, output_path, target_minutes)

    def _predownload_piper_voices(
        self, speaker_voices: Dict[str, str], speaker_engines: Dict[str, str]
    ) -> None:
        """Pre-download all required Piper voices to avoid repeated messages."""
        piper_voices_to_download = set()

        for speaker, voice in speaker_voices.items():
            engine = speaker_engines.get(speaker, "piper")
            if engine == "piper":
                onnx_file = PIPER_DATA_DIR / f"{voice}.onnx"
                if not onnx_file.exists():
                    piper_voices_to_download.add(voice)

        # Download all missing voices upfront
        if piper_voices_to_download:
            print(
                f"\n📥 Pre-downloading {len(piper_voices_to_download)} Piper voices..."
            )
            piper_engine = self.tts_factory.create_engine("piper")
            for voice in piper_voices_to_download:
                # Use synthesize to trigger voice download if needed
                temp_path = PIPER_DATA_DIR / f"temp_{voice}.wav"
                try:
                    piper_engine.synthesize("test", voice, temp_path)
                    if temp_path.exists():
                        temp_path.unlink()
                except Exception:
                    pass  # Voice will be downloaded during actual synthesis

    def _generate_audio_clips(
        self,
        dialogue_lines: List[Tuple[str, str]],
        speaker_voices: Dict[str, str],
        speaker_engines: Dict[str, str],
        speed_scale: float,
    ) -> List[AudioSegment]:
        """Generate audio clips for each dialogue line."""
        tempdir = Path(tempfile.mkdtemp())
        clips: List[AudioSegment] = []

        try:
            print(f"\n🔊 Synthesizing {len(dialogue_lines)} dialogue lines...")
            if speed_scale != 1.0:
                speed_desc = f"slower" if speed_scale > 1.0 else f"faster"
                print(
                    f"🎛️  Speed: {speed_scale}x ({int((speed_scale-1)*100):+d}% {speed_desc})"
                )

            # Use a single progress bar that stays on one line
            with tqdm(
                total=len(dialogue_lines),
                desc="TTS Synthesis",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
            ) as pbar:

                for idx, (speaker, text) in enumerate(dialogue_lines):
                    voice = speaker_voices.get(speaker)
                    engine_name = speaker_engines.get(speaker, "piper")

                    if not voice:
                        raise ValueError(f"No voice specified for speaker '{speaker}'")

                    # Update progress description to show current speaker
                    pbar.set_description(f"TTS: {speaker}")

                    # Generate audio for this line
                    wav_file = tempdir / f"{idx:04d}_{speaker}.{OUTPUT_FORMAT}"
                    engine = self.tts_factory.create_engine(engine_name)
                    engine.synthesize(text, voice, wav_file, speed_scale=speed_scale)

                    # Load and add to clips
                    clips.append(AudioSegment.from_file(wav_file))
                    pbar.update(1)

            if not clips:
                raise RuntimeError("No audio clips were generated successfully.")

            return clips

        finally:
            # Cleanup temp directory
            shutil.rmtree(tempdir)

    def _combine_audio_clips(self, clips: List[AudioSegment]) -> AudioSegment:
        """Combine individual audio clips into a single audio file."""
        print("\n🎵 Combining audio segments...")
        with tqdm(
            total=len(clips),
            desc="Audio Assembly",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
        ) as pbar:
            combined = clips[0]
            pbar.update(1)

            for seg in clips[1:]:
                combined += seg
                pbar.update(1)

        return combined

    def _export_audio(
        self, audio: AudioSegment, output_path: Path, target_minutes: Optional[int] = None
    ) -> None:
        """Export the final audio file."""
        print(f"\n💾 Exporting final audio to {output_path}...")
        audio.export(output_path, format=OUTPUT_FORMAT)

        duration_minutes = len(audio) / 1000 / 60
        print(f"✅ Audio generation complete! Duration: {duration_minutes:.1f} minutes")

        if target_minutes:
            self._show_duration_feedback(duration_minutes, target_minutes)

    def _show_duration_feedback(
        self, actual_minutes: float, target_minutes: Optional[int]
    ) -> None:
        """Show feedback about the generated audio duration."""
        if target_minutes is None:
            return
        if (
            actual_minutes < target_minutes * 0.8
        ):  # If significantly shorter than target
            print(f"⚠️  Audio is shorter than target ({target_minutes} min). Consider:")
            print(f"   • Using --natural flag for slower, more conversational pace")
            print(f"   • The script may need more content - try regenerating")
        elif actual_minutes > target_minutes * 1.2:  # If significantly longer
            print(
                f"📈 Audio is longer than target ({target_minutes} min) - great for detailed content!"
            )
        else:
            print(f"🎯 Duration close to target ({target_minutes} min) - excellent!")
