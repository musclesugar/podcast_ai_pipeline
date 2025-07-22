#!/usr/bin/env python3
"""
System design interview example - Netflix design with structured approach.
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
    """Generate a system design interview podcast about designing Netflix."""
    # Validate configuration
    validate_config()
    
    # Netflix system design interview configuration
    prompt = """
    System design interview: Design Netflix streaming platform.
    
    This should be a realistic technical interview where the interviewer asks the candidate to design Netflix from scratch. Cover:
    
    1. Requirements gathering (functional and non-functional requirements)
    2. Capacity estimation (users, storage, bandwidth)
    3. High-level system design 
    4. Database design (user data, content metadata, viewing history)
    5. API design (user management, content discovery, streaming)
    6. Scalability considerations (CDN, load balancing, caching)
    7. Deep dive topics (video encoding, recommendation system, analytics)
    8. Addressing concerns (fault tolerance, consistency, monitoring)
    
    The interviewer should guide the conversation, ask clarifying questions, and probe deeper into specific areas. The candidate should think out loud, ask questions, and explain their reasoning. Make it feel like a real senior engineer interview with natural back-and-forth discussion.
    """
    
    minutes = 25  # Longer interview format
    speakers = {
        "INTERVIEWER": "en-US-AndrewNeural",
        "CANDIDATE": "en-US-AvaNeural"
    }
    engines = {
        "INTERVIEWER": "edge",
        "CANDIDATE": "edge"
    }
    
    # Advanced settings for interview content
    natural_style = True  # More realistic conversation
    speed = 1.0  # Normal speed. Received issues with generated audio reading out parameter settings.
    
    # Create output directory
    output_dir = ensure_directory(Path("output/netflix_system_design"))
    
    print("🚀 Netflix System Design Interview Example")
    print(f"📝 Topic: System Design Interview - Netflix")
    print(f"⏱️  Duration: {minutes} minutes")
    print(f"👥 Speakers: {len(speakers)} speakers ({', '.join(speakers.keys())})")
    print(f"🎭 Style: {'Natural interview' if natural_style else 'Professional'}")
    print(f"⚡ Speed: {speed}x")
    print(f"🧠 Will use structured outline-first approach for complex content")
    
    # Generate script with structured approach
    print("\n🤖 Generating structured interview script...")
    script_generator = ScriptGenerator()
    script = script_generator.generate_script(
        prompt, 
        minutes, 
        list(speakers.keys()), 
        natural_style=natural_style,
        output_dir=output_dir  # Pass output directory for outline saving
    )
    
    # Save script
    script_path = output_dir / "interview_script.txt"
    script_path.write_text(script, encoding="utf-8")
    print(f"✅ Script saved to {script_path}")
    
    # Preview the script
    print("\n📋 Script preview (first 800 characters):")
    print("=" * 80)
    print(script[:800] + "..." if len(script) > 800 else script)
    print("=" * 80)
    
    # Generate audio
    print(f"\n🎙️ Generating interview audio at {speed}x speed...")
    audio_processor = AudioProcessor()
    audio_path = output_dir / "netflix_system_design_interview.wav"
    
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
        "interview_type": "Netflix System Design",
        "prompt": prompt,
        "minutes": minutes,
        "speakers": speakers,
        "engines": engines,
        "natural_style": natural_style,
        "speed": speed,
        "approach": "structured_outline_first",
        "generated_files": {
            "script": "interview_script.txt",
            "audio": "netflix_system_design_interview.wav"
        }
    }
    
    import json
    config_path = output_dir / "interview_config.json"
    with open(config_path, 'w') as f:
        json.dump(config_info, f, indent=2)
    
    print(f"\n🎉 Netflix system design interview complete!")
    print(f"📁 Output: {output_dir}")
    print(f"📄 Files generated:")
    print(f"   • interview_script.txt - The structured interview dialogue")
    print(f"   • netflix_system_design_interview.wav - The final audio")
    print(f"   • content_outline.json - Structured outline data")
    print(f"   • content_outline.txt - Human-readable outline")
    print(f"   • interview_config.json - Interview configuration")
    print(f"\n💡 The outline shows how the AI structured this complex topic into logical sections!")
    print(f"📋 Check content_outline.txt to see the planning that went into this interview.")

if __name__ == "__main__":
    main()