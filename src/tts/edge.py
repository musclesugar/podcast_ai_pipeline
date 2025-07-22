"""
Microsoft Edge TTS implementation.
"""
import asyncio
from pathlib import Path

from tts.base import TTSEngine

class EdgeTTS(TTSEngine):
    """Microsoft Edge TTS engine (free, cloud-based)."""
    
    def synthesize(self, text: str, voice: str, output_path: Path, speed_scale: float = 1.0) -> None:
        """Synthesize text using Microsoft Edge TTS."""
        try:
            import edge_tts
            
            # Clean the text of any SSML or markdown artifacts first
            cleaned_text = self.clean_text_for_tts(text)
            
            async def generate():
                communicate = edge_tts.Communicate(cleaned_text, voice)
                
                if speed_scale == 1.0:
                    # No speed adjustment needed - save directly as WAV-like format
                    await communicate.save(str(output_path))
                else:
                    # Save as MP3 first, then convert with speed adjustment
                    temp_mp3 = output_path.with_suffix('.mp3')
                    await communicate.save(str(temp_mp3))
                    
                    # Convert with speed adjustment
                    self._convert_with_speed_adjustment(temp_mp3, output_path, speed_scale)
                    
                    # Clean up temp file
                    if temp_mp3.exists():
                        temp_mp3.unlink()
            
            asyncio.run(generate())
            
        except ImportError:
            raise RuntimeError(
                "Edge TTS not installed. Install with: pip install edge-tts\n"
                "Edge TTS provides free, high-quality voices from Microsoft."
            )
        except Exception as e:
            raise RuntimeError(f"Edge TTS synthesis failed: {e}")
    
    def _convert_with_speed_adjustment(self, input_path: Path, output_path: Path, speed_scale: float) -> None:
        """Convert audio and adjust speed using simpler method."""
        try:
            from pydub import AudioSegment
            
            # Load the audio file (let pydub auto-detect format)
            audio = AudioSegment.from_file(str(input_path))
            
            # Apply speed adjustment if needed
            if speed_scale != 1.0:
                # Simple speed adjustment without complex processing
                # speed_scale > 1.0 means slower, so we need lower playback speed
                playback_speed = 1.0 / speed_scale
                
                # Use frame_rate manipulation instead of speedup for more stability
                # This changes both speed and pitch slightly but is more reliable
                new_sample_rate = int(audio.frame_rate * playback_speed)
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                audio = audio.set_frame_rate(22050)  # Normalize to standard rate
            
            # Export as simple WAV
            audio.export(str(output_path), format="wav")
            
        except Exception as e:
            print(f"⚠️ Speed adjustment failed ({e}), saving without adjustment...")
            # Fallback: simple conversion without speed change
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(str(input_path))
                audio.export(str(output_path), format="wav")
            except Exception as e2:
                raise RuntimeError(f"Audio conversion completely failed: {e2}")
    
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