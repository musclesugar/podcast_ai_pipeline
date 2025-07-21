#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
"""
import sys
from pathlib import Path

# Add src to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))


def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing module imports...")

    try:
        # Test config imports
        print("  📁 Testing config modules...")
        from config.settings import WPM_NATURAL, validate_config
        from config.voices import PIPER_VOICES, get_voice_info

        print("    ✅ Config modules imported successfully")

        # Test core imports
        print("  🧠 Testing core modules...")
        from core.audio_processor import AudioProcessor
        from core.script_generator import ScriptGenerator
        from core.script_parser import ScriptParser

        print("    ✅ Core modules imported successfully")

        # Test TTS imports
        print("  🎙️ Testing TTS modules...")
        from tts.base import TTSEngine
        from tts.edge import EdgeTTS
        from tts.factory import TTSFactory
        from tts.piper import PiperTTS

        print("    ✅ TTS modules imported successfully")

        # Test transcription imports
        print("  📝 Testing transcription modules...")
        from transcription.whisper import WhisperTranscriber

        print("    ✅ Transcription modules imported successfully")

        # Test utility imports
        print("  🔧 Testing utility modules...")
        from utils.file_utils import ensure_directory, parse_json_arg
        from utils.progress import ProgressTracker

        print("    ✅ Utility modules imported successfully")

        print(
            "\n🎉 All imports successful! The modular structure is working correctly."
        )

        # Test basic functionality
        print("\n🔍 Testing basic functionality...")

        # Test voice info
        voice_info = get_voice_info()
        print(f"    ✅ Voice info loaded ({len(voice_info)} characters)")

        # Test TTS factory
        factory = TTSFactory()
        available_engines = factory.get_available_engines()
        print(f"    ✅ TTS factory working, found {len(available_engines)} engines")

        # Test script generator initialization
        generator = ScriptGenerator()
        print("    ✅ Script generator initialized")

        return True

    except Exception as e:
        print(f"    ❌ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ All tests passed! You can now run the main script.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        sys.exit(1)
