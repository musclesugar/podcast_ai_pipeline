#!/usr/bin/env python3
"""
Basic podcast generation example.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.settings import validate_config
from core.script_generator import ScriptGenerator
from core.audio_processor import AudioProcessor
from utils.file_utils import ensure_directory

def main():
    """Generate a basic podcast episode."""
    # Validate configuration
    validate_config()
    
    # Configuration
    prompt = "Introduction to Suspension Bridges for absolute beginners"
    minutes = 10
    speakers = {
        "HOST": "en-US-AndrewNeural",
        "GUEST": "en-US-AvaNeural"
    }
    engines = {
        "HOST": "edge",
        "GUEST": "edge"
    }
    
    # Create output directory
    output_dir = ensure_directory(Path("output/basic_example"))
    
    print("🚀 Basic Podcast Generation Example")
    print(f"📝 Topic: {prompt}")
    print(f"⏱️  Duration: {minutes} minutes")
    print(f"👥 Speakers: {list(speakers.keys())}")
    
    # Generate script
    print("\n🤖 Generating script...")
    script_generator = ScriptGenerator()
    script = script_generator.generate_script(prompt, minutes, list(speakers.keys()))
    
    # Save script
    script_path = output_dir / "script.txt"
    script_path.write_text(script, encoding="utf-8")
    print(f"✅ Script saved to {script_path}")
    
    # Generate audio
    print("\n🎙️ Generating audio...")
    audio_processor = AudioProcessor()
    audio_path = output_dir / "podcast.wav"
    
    audio_processor.process_script_to_audio(script, speakers, engines, audio_path, minutes)
    
    print(f"\n🎉 Basic example complete!")
    print(f"📁 Output: {output_dir}")

if __name__ == "__main__":
    main()