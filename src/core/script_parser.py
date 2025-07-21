"""
Script validation and parsing for dialogue extraction.
"""

import re
from typing import List, Tuple


class ScriptParser:
    """Handles script validation and dialogue line extraction."""

    def __init__(self):
        # More flexible regex patterns to try
        self.patterns = [
            r"^([A-Z][A-Z0-9_]*)\s*:\s*(.*)",  # HOST: or GUEST: (all caps)
            r"^([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*)",  # More flexible speaker names
            r"^\*?\*?([A-Z][A-Z0-9_]*)\*?\*?\s*:\s*(.*)",  # With optional markdown bold
        ]

        # Patterns to skip
        self.skip_patterns = [
            lambda line: line.startswith("```"),  # Code blocks
            lambda line: line.startswith("-"),  # Bullet points
            lambda line: line.startswith("*"),  # Markdown lists
            lambda line: line.startswith("#"),  # Headers
            lambda line: line.startswith("("),  # Parenthetical notes
            lambda line: line.startswith("["),  # Brackets
            lambda line: line.startswith("<"),  # XML/HTML tags
            lambda line: line.startswith("{"),  # JSON-like content
            lambda line: "def " in line,  # Function definitions
            lambda line: "return" in line,  # Code returns
            lambda line: line.startswith("text:"),  # Common GPT tag
            lambda line: line.startswith("speaker:"),  # Speaker metadata
            lambda line: line.startswith("voice:"),  # Voice metadata
            lambda line: "transcript:" in line.lower(),  # Transcript labels
            lambda line: "dialogue:" in line.lower(),  # Dialogue labels
            lambda line: line.strip() in ["```", "---", "===", "***"],  # Separators
            lambda line: line.startswith("Note:"),  # Notes
            lambda line: line.startswith("Example:"),  # Examples
            lambda line: "OUTPUT:" in line,  # Output labels
            lambda line: "INPUT:" in line,  # Input labels
            lambda line: len(line.strip()) < 3,  # Very short lines
            lambda line: line.isdigit(),  # Just numbers
            lambda line: line.startswith("//"),  # Comments
        ]

        # Text prefixes to remove from dialogue
        self.text_prefixes_to_remove = [
            "text:",
            "Text:",
            "TEXT:",
            "```text",
            "```Text",
            "```TEXT",
            "```",
            "text",
            "TEXT",
            "voice:",
            "Voice:",
            "VOICE:",
            "speaker:",
            "Speaker:",
            "SPEAKER:",
            "dialogue:",
            "Dialogue:",
            "DIALOGUE:",
            "says:",
            "Says:",
            "SAYS:",
            "speaks:",
            "Speaks:",
            "SPEAKS:",
            "output:",
            "Output:",
            "OUTPUT:",
            "response:",
            "Response:",
            "RESPONSE:",
        ]

    def validate_and_preview_script(
        self, script: str, expected_speakers: List[str]
    ) -> List[Tuple[str, str]]:
        """Validate script format and return parsed dialogue lines."""
        print("\n📋 Validating generated script...")

        dialogue_lines = []
        unmatched_lines = []

        for line_num, line in enumerate(script.splitlines(), 1):
            line = line.strip()
            if not line:
                continue

            # Skip obvious non-dialogue lines and common GPT artifacts
            if self._should_skip_line(line):
                unmatched_lines.append(f"Line {line_num}: {line}")
                continue

            # Try to match dialogue patterns
            matched = False
            for pattern in self.patterns:
                m = re.match(pattern, line)
                if m:
                    speaker, text = m.groups()
                    speaker = speaker.strip(
                        "*"
                    ).strip()  # Remove any markdown formatting

                    if speaker in expected_speakers:
                        # Clean up the dialogue text and remove common artifacts
                        text = self._clean_dialogue_text(text)

                        # Skip lines that are clearly not dialogue after cleaning
                        if self._is_valid_dialogue(text):
                            dialogue_lines.append((speaker, text))
                            matched = True
                            break

            if (
                not matched and line and len(line) > 5
            ):  # Only log substantial unmatched lines
                unmatched_lines.append(f"Line {line_num}: {line}")

        # Show preview
        self._show_preview(dialogue_lines, unmatched_lines)

        if not dialogue_lines:
            self._show_debug_info(script)
            raise RuntimeError(
                "No parseable dialogue lines found in generated script. Check the format."
            )

        return dialogue_lines

    def _should_skip_line(self, line: str) -> bool:
        """Check if a line should be skipped based on skip patterns."""
        return any(pattern(line) for pattern in self.skip_patterns)

    def _clean_dialogue_text(self, text: str) -> str:
        """Clean up dialogue text by removing common prefixes and artifacts."""
        text = text.strip()

        # Remove common prefixes that GPT sometimes adds
        for prefix in self.text_prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix) :].strip()
                break

        return text

    def _is_valid_dialogue(self, text: str) -> bool:
        """Check if cleaned text represents valid dialogue."""
        if not text:
            return False

        text_lower = text.lower()

        # Skip lines that are clearly not dialogue after cleaning
        invalid_content = [
            "text",
            "voice",
            "speaker",
            "dialogue",
            "says",
            "speaks",
            "...",
            "---",
            "***",
            "```",
        ]

        if text_lower in invalid_content or len(text) < 5:  # Skip very short responses
            return False

        return True

    def _show_preview(
        self, dialogue_lines: List[Tuple[str, str]], unmatched_lines: List[str]
    ):
        """Show preview of parsed dialogue and filtering results."""
        word_count = sum(len(text.split()) for _, text in dialogue_lines)
        print(f"✅ Found {len(dialogue_lines)} dialogue lines (~{word_count} words)")

        print(f"\n📝 Preview of parsed dialogue (first 3 lines):")
        for i, (speaker, text) in enumerate(dialogue_lines[:3]):
            preview_text = text[:80] + "..." if len(text) > 80 else text
            print(f"  {speaker}: {preview_text}")

        if len(dialogue_lines) > 3:
            print(f"  ... and {len(dialogue_lines) - 3} more lines")

        # Only show unmatched lines if there are many
        if len(unmatched_lines) > 5:
            print(
                f"\n⚠️  Filtered out {len(unmatched_lines)} non-dialogue lines (code, formatting, etc.)"
            )
        elif unmatched_lines:
            print(f"\n⚠️  Filtered out {len(unmatched_lines)} lines:")
            for line in unmatched_lines[:3]:
                print(f"  {line}")

    def _show_debug_info(self, script: str):
        """Show debug information when no dialogue lines are found."""
        print("\n❌ No valid dialogue lines found!")
        print("Raw script preview:")
        print("=" * 50)
        print(script[:500] + "..." if len(script) > 500 else script)
        print("=" * 50)
