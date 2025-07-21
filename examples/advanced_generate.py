#!/usr/bin/env python3
"""
Advanced podcast generation example with multiple speakers and natural conversation.
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
    """Generate an advanced podcast episode with multiple features."""
    # Validate configuration
    validate_config()
    
    # Advanced configuration - your exact command recreated
    prompt = (
        "Solving dynamic programming problems like fibonacci but more importantly, "
        "climbing stairs. Assume they're teaching for people that really struggle "
        "with the concept of breaking down the solution into an algorithm (logically "
        "understanding that a step can be 1 or 2 steps for every step) but struggling "
        "with how they equates to the formula for the solution, and the mindset "
        "required for future dynamic coding problems. Avoid mathematical formulas "
        "that would be awkward in conversational settings to say aloud. Include "
        "examples of the host breaking down the complicated explanation into simple terms."
    )
    
    minutes = 7
    speakers = {
        "HOST": "en-US-AndrewNeural",
        "GUEST": "en-US-AvaNeural", 
        "EXPERT": "en-US-EmmaNeural"
    }
    engines = {
        "HOST": "edge",
        "GUEST": "edge",
        "EXPERT": "edge"
    }
    
    # Advanced settings
    natural_style = True
    speed = 1.0
    
    # Create output directory
    output_dir = ensure_directory(Path("output/dp_tutorial_advanced"))
    
    print("🚀 Advanced Podcast Generation Example")
    print(f"📝 Topic: Dynamic Programming Tutorial")
    print(f"⏱️  Duration: {minutes} minutes")
    print(f"👥 Speakers: {len(speakers)} speakers ({', '.join(speakers.keys())})")
    print(f"🎭 Style: {'Natural conversation' if natural_style else 'Professional'}")
    print(f"⚡ Speed: {speed}x")
    
    # Generate script with natural conversation style
    print("\n🤖 Generating natural conversation script...")
    script_generator = ScriptGenerator()
    script = script_generator.generate_script(
        prompt, 
        minutes, 
        list(speakers.keys()), 
        natural_style=natural_style
    )
    
    # Save script
    script_path = output_dir / "script.txt"
    script_path.write_text(script, encoding="utf-8")
    print(f"✅ Script saved to {script_path}")
    
    # Preview the script first
    print("\n📋 Script preview (first 500 characters):")
    print("=" * 60)
    print(script[:500] + "..." if len(script) > 500 else script)
    print("=" * 60)
    
    # Generate audio with speed control
    print(f"\n🎙️ Generating audio at {speed}x speed...")
    audio_processor = AudioProcessor()
    audio_path = output_dir / "podcast_advanced.wav"
    
    audio_processor.process_script_to_audio(
        script, 
        speakers, 
        engines, 
        audio_path, 
        minutes, 
        speed
    )
    
    # Save configuration for reference
    config_info = {
        "prompt": prompt,
        "minutes": minutes,
        "speakers": speakers,
        "engines": engines,
        "natural_style": natural_style,
        "speed": speed,
        "generated_files": {
            "script": "script.txt",
            "audio": "podcast_advanced.wav"
        }
    }
    
    import json
    config_path = output_dir / "generation_config.json"
    with open(config_path, 'w') as f:
        json.dump(config_info, f, indent=2)
    
    print(f"\n🎉 Advanced example complete!")
    print(f"📁 Output: {output_dir}")
    print(f"📄 Files generated:")
    print(f"   • script.txt - The generated dialogue")
    print(f"   • podcast_advanced.wav - The final audio")
    print(f"   • generation_config.json - Configuration used")

if __name__ == "__main__":
    main()