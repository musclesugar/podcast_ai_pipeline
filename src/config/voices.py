"""
Voice database and management for various TTS engines.
"""

from typing import Any, Dict, List

# Comprehensive Piper voice database
PIPER_VOICES = {
    # Most Popular English Voices (by community usage)
    "popular": {
        "en_US-lessac-high": {
            "gender": "female",
            "quality": "high",
            "style": "clear, professional",
            "description": "Very popular female voice, excellent for podcasts",
        },
        "en_US-lessac-medium": {
            "gender": "female",
            "quality": "medium",
            "style": "clear, professional",
            "description": "Most used female voice, great balance of quality/speed",
        },
        "en_US-ryan-high": {
            "gender": "male",
            "quality": "high",
            "style": "warm, friendly",
            "description": "Popular male voice, natural sounding",
        },
        "en_US-amy-medium": {
            "gender": "female",
            "quality": "medium",
            "style": "pleasant, conversational",
            "description": "Friendly female voice, good for dialogue",
        },
        "en_US-joe-medium": {
            "gender": "male",
            "quality": "medium",
            "style": "casual, approachable",
            "description": "Relaxed male voice, podcast-friendly",
        },
        "en_US-danny-low": {
            "gender": "male",
            "quality": "low",
            "style": "energetic, youthful",
            "description": "Younger-sounding male voice",
        },
        "en_US-kathleen-low": {
            "gender": "female",
            "quality": "low",
            "style": "mature, authoritative",
            "description": "Professional female voice",
        },
    },
    # Female Voices by Quality
    "female": {
        "high": ["en_US-lessac-high", "en_US-libritts-high"],
        "medium": [
            "en_US-lessac-medium",
            "en_US-amy-medium",
            "en_US-libritts_r-medium",
            "en_US-arctic-medium",
            "en_US-kusal-medium",
        ],
        "low": ["en_US-amy-low", "en_US-lessac-low", "en_US-kathleen-low"],
    },
    # Male Voices by Quality
    "male": {
        "high": ["en_US-ryan-high"],
        "medium": ["en_US-ryan-medium", "en_US-joe-medium", "en_US-l2arctic-medium"],
        "low": ["en_US-ryan-low", "en_US-danny-low"],
    },
    # International English Variants
    "international": {
        "en_GB-alan-medium": {
            "gender": "male",
            "accent": "British",
            "style": "BBC-like, formal",
        },
        "en_GB-alba-medium": {
            "gender": "female",
            "accent": "British",
            "style": "posh, refined",
        },
        "en_GB-aru-medium": {
            "gender": "male",
            "accent": "British",
            "style": "modern British",
        },
        "en_GB-jenny_dioco-medium": {
            "gender": "female",
            "accent": "British",
            "style": "conversational",
        },
        "en_GB-northern_english_male-medium": {
            "gender": "male",
            "accent": "Northern British",
            "style": "regional character",
        },
    },
}

# Popular Edge TTS voices
EDGE_VOICES = {
    "popular_male": [
        "en-US-AndrewNeural",
        "en-US-BrianNeural",
        "en-US-ChristopherNeural",
        "en-US-EricNeural",
        "en-US-GuyNeural",
        "en-US-RogerNeural",
    ],
    "popular_female": [
        "en-US-AvaNeural",
        "en-US-EmmaNeural",
        "en-US-JennyNeural",
        "en-US-MichelleNeural",
        "en-US-MonicaNeural",
        "en-US-SaraNeural",
    ],
    "international": [
        "en-GB-RyanNeural",  # British Male
        "en-GB-SoniaNeural",  # British Female
        "en-AU-NatashaNeural",  # Australian Female
        "en-AU-WilliamNeural",  # Australian Male
        "en-CA-ClaraNeural",  # Canadian Female
        "en-CA-LiamNeural",  # Canadian Male
    ],
}

# OpenAI TTS voices
OPENAI_VOICES = {
    "alloy": {"gender": "neutral", "style": "balanced"},
    "echo": {"gender": "male", "style": "warm"},
    "fable": {"gender": "male", "style": "dramatic"},
    "onyx": {"gender": "male", "style": "deep"},
    "nova": {"gender": "female", "style": "bright"},
    "shimmer": {"gender": "female", "style": "soft"},
}


def parse_voice_name(voice_name: str) -> Dict[str, str]:
    """Parse a voice name to extract metadata."""
    parts = voice_name.split("-")
    if len(parts) >= 3:
        lang_region = parts[0]
        name = parts[1]
        quality = parts[2]

        # Determine gender from our database
        gender = "unknown"
        for voice_info in PIPER_VOICES["popular"].values():
            if voice_name in PIPER_VOICES["popular"]:
                gender = PIPER_VOICES["popular"][voice_name]["gender"]
                break

        # Check female/male lists
        if gender == "unknown":
            for qual_voices in PIPER_VOICES["female"].values():
                if voice_name in qual_voices:
                    gender = "female"
                    break
            for qual_voices in PIPER_VOICES["male"].values():
                if voice_name in qual_voices:
                    gender = "male"
                    break

        return {
            "language": lang_region,
            "name": name,
            "quality": quality,
            "gender": gender,
            "full_name": voice_name,
            "engine": "piper",
        }

    # Check if it's an Edge TTS voice
    if "Neural" in voice_name:
        return {
            "full_name": voice_name,
            "language": voice_name.split("-")[0],
            "name": voice_name.split("-")[1].replace("Neural", ""),
            "quality": "high",
            "gender": _get_edge_gender(voice_name),
            "engine": "edge",
        }

    # Check if it's an OpenAI voice
    if voice_name.lower() in OPENAI_VOICES:
        voice_info = OPENAI_VOICES[voice_name.lower()]
        return {
            "full_name": voice_name,
            "language": "en-US",
            "name": voice_name,
            "quality": "premium",
            "gender": voice_info["gender"],
            "engine": "openai",
        }

    return {
        "full_name": voice_name,
        "language": "unknown",
        "name": "unknown",
        "quality": "unknown",
        "gender": "unknown",
        "engine": "unknown",
    }


def _get_edge_gender(voice_name: str) -> str:
    """Determine gender for Edge TTS voice."""
    if any(
        voice_name in voices
        for voices in [EDGE_VOICES["popular_male"], EDGE_VOICES["international"]]
    ):
        if any(
            name in voice_name
            for name in [
                "Andrew",
                "Brian",
                "Christopher",
                "Eric",
                "Guy",
                "Roger",
                "Ryan",
                "William",
                "Liam",
            ]
        ):
            return "male"
    if any(
        voice_name in voices
        for voices in [EDGE_VOICES["popular_female"], EDGE_VOICES["international"]]
    ):
        if any(
            name in voice_name
            for name in [
                "Ava",
                "Emma",
                "Jenny",
                "Michelle",
                "Monica",
                "Sara",
                "Sonia",
                "Natasha",
                "Clara",
            ]
        ):
            return "female"
    return "unknown"


def suggest_voice_alternatives(failed_voice: str) -> List[str]:
    """Suggest alternative voices based on the failed voice."""
    voice_info = parse_voice_name(failed_voice)
    alternatives = []

    # Suggest same gender alternatives
    if voice_info["gender"] in ["male", "female"]:
        if voice_info["engine"] == "piper":
            gender_voices = PIPER_VOICES[voice_info["gender"]]
            for quality, voices in gender_voices.items():
                alternatives.extend(voices[:2])  # Top 2 per quality
        elif voice_info["engine"] == "edge":
            if voice_info["gender"] == "male":
                alternatives.extend(EDGE_VOICES["popular_male"][:3])
            else:
                alternatives.extend(EDGE_VOICES["popular_female"][:3])

    # Add popular alternatives from different engines
    alternatives.extend(
        [
            "en_US-lessac-medium",  # Piper
            "en_US-ryan-medium",  # Piper
            "en-US-AndrewNeural",  # Edge
            "en-US-AvaNeural",  # Edge
            "alloy",  # OpenAI
            "nova",  # OpenAI
        ]
    )

    # Remove duplicates and the failed voice
    alternatives = list(set(alternatives))
    if failed_voice in alternatives:
        alternatives.remove(failed_voice)

    return alternatives[:5]  # Return top 5 suggestions


def get_voice_info() -> str:
    """Return formatted voice information for documentation."""
    return """
🎙️  VOICE GUIDE
===============

📈 MOST POPULAR PIPER VOICES:
  • en_US-lessac-high (Female, High Quality) - Clear, professional. Best overall choice.
  • en_US-ryan-high (Male, High Quality) - Warm, friendly. Top male voice.
  • en_US-lessac-medium (Female, Medium) - Excellent balance of quality/speed.
  • en_US-amy-medium (Female, Medium) - Pleasant, conversational.
  • en_US-joe-medium (Male, Medium) - Casual, approachable.

🔊 EDGE TTS VOICES (Recommended):
  • en-US-AndrewNeural (Male) - Professional, clear
  • en-US-AvaNeural (Female) - Friendly, natural
  • en-US-EmmaNeural (Female) - Warm, engaging
  • en-US-BrianNeural (Male) - Casual, approachable
  • en-GB-RyanNeural (Male, British) - Professional accent

🎯 ENGINE COMPARISON:
  • Edge TTS: Free, excellent quality, no setup required
  • Piper: Free, good quality, local processing, auto-download
  • OpenAI: Paid ($0.015/1K chars), premium quality
  • Coqui: Free, advanced features, voice cloning

💡 SPEED CONTROL TIPS:
  • --speed 1.0 = Normal pace
  • --speed 1.2 = 20% slower (educational content)
  • --speed 0.8 = 20% faster (energetic style)

🆓 SETUP RECOMMENDATIONS:
  1. Try Edge TTS first (easiest, free, excellent quality)
  2. Use Piper for local processing
  3. Consider OpenAI TTS for premium productions
"""
