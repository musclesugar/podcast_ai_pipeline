#!/usr/bin/env python3
"""
Podcast AI Pipeline v2.1 - Main CLI Entry Point
================================================
A modular tool for generating and transcribing podcasts with AI.
"""
import argparse
import sys
import os
from pathlib import Path

# Add src to Python path for absolute imports
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Now we can use absolute imports
from config.settings import validate_config, DEFAULT_OUTPUT_DIR
from config.voices import get_voice_info
from core.script_generator import ScriptGenerator
from core.audio_processor import AudioProcessor
from transcription.whisper import WhisperTranscriber
from utils.file_utils import ensure_directory, parse_json_arg
from tts.factory import TTSFactory

def main():
    """Main CLI entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Handle voice listing
    if hasattr(args, 'list_voices') and args.list_voices:
        print(get_voice_info())
        return 0
    
    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        return 1
    
    print(f"🚀 Podcast AI Pipeline v2.1 - Mode: {args.mode}")
    print(f"📁 Output directory: {args.output}")
    
    # Ensure output directory exists
    output_dir = ensure_directory(Path(args.output))
    
    try:
        if args.mode == "generate":
            return handle_generate_mode(args, output_dir)
        elif args.mode == "transcribe":
            return handle_transcribe_mode(args, output_dir)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

def create_argument_parser():
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate or transcribe podcasts with local TTS and speed control."
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # Generate subcommand
    generate_parser = subparsers.add_parser("generate", help="Generate a scripted episode")
    generate_parser.add_argument("--prompt", required=True, help="Topic prompt for GPT")
    generate_parser.add_argument("--minutes", type=int, default=8, help="Target length in minutes (approx.)")
    generate_parser.add_argument("--speakers", required=True, help="JSON mapping of SPEAKER→voice_model")
    generate_parser.add_argument("--engines", default="{}", help="JSON mapping of SPEAKER→engine (piper, edge, openai, etc.)")
    generate_parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="Destination folder")
    generate_parser.add_argument("--preview-only", action="store_true", help="Generate and preview script without audio synthesis")
    generate_parser.add_argument("--natural", action="store_true", help="Generate natural conversational style with pauses, fillers, interruptions")
    generate_parser.add_argument("--speed", type=float, default=1.0, help="Speaking speed multiplier (1.0=normal, 1.2=20%% slower, 0.8=20%% faster)")
    generate_parser.add_argument("--list-voices", action="store_true", help="Show available voices and exit")
    generate_parser.add_argument("--model", default="gpt-4o-mini", help="GPT model to use for script generation")

    # Transcribe subcommand
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe an existing audio source")
    transcribe_parser.add_argument("--source", required=True, help="Path or URL to audio/video")
    transcribe_parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="Destination folder")
    transcribe_parser.add_argument("--model", default="whisper-1", help="Whisper model to use")
    transcribe_parser.add_argument("--list-voices", action="store_true", help="Show available voices and exit")

    return parser

def handle_generate_mode(args, output_dir: Path) -> int:
    """Handle the generate mode."""
    # Parse speaker configurations
    try:
        speaker_map = parse_json_arg(args.speakers, "speakers")
        engine_map = parse_json_arg(args.engines, "engines")
    except ValueError as e:
        print(f"❌ {e}")
        return 1
    
    # Validate TTS engines
    if not validate_tts_engines(engine_map, speaker_map):
        return 1
    
    # Create timestamped subdirectory for this generation
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_name = "_".join(args.prompt.split()[:3]).lower()  # First 3 words of prompt
    session_dir = output_dir / f"{timestamp}_{topic_name}"
    ensure_directory(session_dir)
    
    print(f"📁 Session directory: {session_dir}")
    
    # Generate script
    print("🤖 Generating podcast script...")
    script_generator = ScriptGenerator(model=args.model)
    script = script_generator.generate_script(
        args.prompt, 
        args.minutes, 
        list(speaker_map.keys()), 
        natural_style=args.natural
    )
    
    # Save script
    script_path = session_dir / "podcast_transcript.txt"
    script_path.write_text(script, encoding="utf-8")
    print(f"✅ Script saved to {script_path}")
    
    # Save generation metadata
    metadata = {
        "timestamp": timestamp,
        "prompt": args.prompt,
        "minutes": args.minutes,
        "speakers": speaker_map,
        "engines": engine_map,
        "natural_style": args.natural,
        "speed": args.speed,
        "model": args.model,
        "files": {
            "script": "podcast_transcript.txt",
            "audio": "podcast_audio.wav" if not args.preview_only else None
        }
    }
    
    import json
    metadata_path = session_dir / "generation_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Preview mode - just validate and show script
    if args.preview_only:
        from core.script_parser import ScriptParser
        parser = ScriptParser()
        parser.validate_and_preview_script(script, list(speaker_map.keys()))
        print(f"\n📋 Preview complete. Files saved to {session_dir}")
        print(f"   📝 Script: {script_path}")
        print(f"   📄 Metadata: {metadata_path}")
        return 0
    
    # Generate audio
    print("🎙️ Starting audio generation...")
    audio_processor = AudioProcessor()
    audio_path = session_dir / "podcast_audio.wav"
    
    audio_processor.process_script_to_audio(
        script, 
        speaker_map, 
        engine_map, 
        audio_path, 
        args.minutes, 
        args.speed
    )
    
    print(f"\n🎉 Episode generation complete!")
    print(f"📁 Files saved to: {session_dir}")
    print(f"   📝 Script: podcast_transcript.txt")
    print(f"   🎵 Audio: podcast_audio.wav")
    print(f"   📄 Metadata: generation_metadata.json")
    
    return 0

def handle_transcribe_mode(args, output_dir: Path) -> int:
    """Handle the transcribe mode."""
    # Create timestamped subdirectory for this transcription
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_name = Path(args.source).stem if not str(args.source).startswith("http") else "url_audio"
    session_dir = output_dir / f"{timestamp}_transcribe_{source_name}"
    ensure_directory(session_dir)
    
    print(f"📁 Session directory: {session_dir}")
    
    transcriber = WhisperTranscriber(model=args.model)
    transcript_path = transcriber.transcribe_audio(args.source, session_dir)
    
    # Save transcription metadata
    metadata = {
        "timestamp": timestamp,
        "source": str(args.source),
        "model": args.model,
        "files": {
            "transcript": transcript_path.name
        }
    }
    
    import json
    metadata_path = session_dir / "transcription_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"🎉 Transcription complete!")
    print(f"📁 Files saved to: {session_dir}")
    print(f"   📝 Transcript: {transcript_path.name}")
    print(f"   📄 Metadata: transcription_metadata.json")
    
    return 0

def validate_tts_engines(engine_map, speaker_map):
    """Validate that all specified TTS engines are available."""
    factory = TTSFactory()
    available_engines = factory.get_available_engines()
    
    # Check each speaker's engine
    for speaker, engine in engine_map.items():
        if speaker not in speaker_map:
            print(f"❌ Engine specified for unknown speaker '{speaker}'")
            return False
        
        if engine not in available_engines:
            print(f"❌ Unknown TTS engine '{engine}' for speaker '{speaker}'")
            return False
        
        if not available_engines[engine]:
            print(f"❌ TTS engine '{engine}' is not available. Please install required dependencies.")
            suggest_engine_installation(engine)
            return False
    
    return True

def suggest_engine_installation(engine: str):
    """Suggest installation commands for unavailable engines."""
    suggestions = {
        "edge": "pip install edge-tts",
        "coqui": "pip install TTS",
        "openai": "Ensure OPENAI_API_KEY is set in your .env file",
        "piper": "Install Piper TTS: https://github.com/rhasspy/piper",
        "bark": "pip install git+https://github.com/suno-ai/bark.git"
    }
    
    if engine in suggestions:
        print(f"💡 To install {engine}: {suggestions[engine]}")

if __name__ == "__main__":
    exit(main())