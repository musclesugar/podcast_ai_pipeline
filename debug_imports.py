#!/usr/bin/env python3
"""
Debug script to find the exact source of import issues.
"""
import sys
from pathlib import Path

# Add src to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))


def check_file_for_relative_imports(file_path):
    """Check a Python file for relative imports."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        lines = content.split("\n")
        relative_imports = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith("from ..") or line.startswith("from ."):
                relative_imports.append((line_num, line))

        return relative_imports
    except Exception as e:
        return [f"Error reading file: {e}"]


def scan_all_python_files():
    """Scan all Python files in src/ for relative imports."""
    print("🔍 Scanning for relative imports...")

    src_path = Path("src")
    if not src_path.exists():
        print("❌ src/ directory not found!")
        return

    python_files = list(src_path.rglob("*.py"))
    print(f"📁 Found {len(python_files)} Python files")

    issues_found = False

    for py_file in python_files:
        relative_imports = check_file_for_relative_imports(py_file)

        if relative_imports:
            issues_found = True
            print(f"\n❌ {py_file}:")
            for line_num, line in relative_imports:
                print(f"   Line {line_num}: {line}")

    if not issues_found:
        print("\n✅ No relative imports found!")

    return not issues_found


def test_individual_imports():
    """Test imports one by one to identify the problem."""
    print("\n🧪 Testing individual imports...")

    modules_to_test = [
        ("config.settings", "Settings module"),
        ("config.voices", "Voices module"),
        ("core.script_parser", "Script parser"),
        ("core.script_generator", "Script generator"),
        ("core.audio_processor", "Audio processor"),
        ("tts.base", "TTS base"),
        ("tts.piper", "Piper TTS"),
        ("tts.edge", "Edge TTS"),
        ("tts.factory", "TTS factory"),
        ("transcription.whisper", "Whisper transcription"),
        ("utils.file_utils", "File utils"),
        ("utils.progress", "Progress utils"),
    ]

    for module_name, description in modules_to_test:
        try:
            print(f"  📦 Testing {description}...")
            __import__(module_name)
            print(f"    ✅ {module_name} imported successfully")
        except Exception as e:
            print(f"    ❌ {module_name} failed: {e}")
            if "relative import" in str(e):
                print(f"       🔍 This is the problematic file!")


def main():
    """Main debugging function."""
    print("🐛 Import Debug Tool")
    print("=" * 50)

    # First, scan for relative imports
    clean = scan_all_python_files()

    if clean:
        print("\n🧪 All files look clean, testing imports...")
        test_individual_imports()
    else:
        print("\n💡 Fix the relative imports shown above and try again.")
        print("\nQuick fix guide:")
        print("• Change 'from ..config import' to 'from config import'")
        print("• Change 'from .base import' to 'from tts.base import'")
        print("• etc.")


if __name__ == "__main__":
    main()
