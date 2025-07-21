# 🎙️ Podcast AI Pipeline v2.1

A **self-contained** tool that can **generate** brand-new podcast episodes *or* **transcribe** existing audio files using AI. Create professional-quality conversational content with multiple speakers, natural dialogue, and flexible TTS options.

## ✨ Features

### 🤖 Content Generation
- **AI-powered script writing** with GPT models for engaging dialogue
- **Multi-speaker conversations** with distinct voices and personalities
- **Natural conversation flow** with pauses, interruptions, and realistic speech patterns
- **Intelligent batching** for long-form content (handles 30+ minute episodes)
- **Speed control** for educational content or accessibility needs

### 🎙️ Text-to-Speech Options
- **Microsoft Edge TTS** (free) - Extremely natural cloud voices (recommended)
- **Piper TTS** (free, local) - High-quality neural voices
- **Coqui TTS** (free, local) - Advanced neural models with voice cloning
- **OpenAI TTS** (paid) - Premium quality for professional productions
- **Auto-downloading** of voice models when needed

### 📝 Content Processing
- **Script validation** with preview before audio generation
- **Progress tracking** with visual feedback for all stages
- **Flexible audio formats** (WAV, MP3) with quality options
- **Transcription** of existing audio using OpenAI Whisper

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
git clone <repository-url>
cd podcast_ai_pipeline

# Set up development environment (handles PyTorch conflicts automatically)
make setup-dev-clean

# Or step-by-step:
pip install pip-tools
pip-compile requirements.in
pip-compile requirements-extra.in  
pip-compile requirements-dev.in
pip install -r requirements-dev.txt

# Set up your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Basic Usage

**Generate a 7-minute educational podcast:**
```bash
python podcast_ai_pipeline.py generate \
  --prompt "Dynamic programming for beginners - climbing stairs problem" \
  --minutes 7 \
  --speakers '{"HOST":"en-US-AndrewNeural","GUEST":"en-US-AvaNeural"}' \
  --engines '{"HOST":"edge","GUEST":"edge"}' \
  --natural \
  --output my_podcast
```

**Transcribe an existing audio file:**
```bash
python podcast_ai_pipeline.py transcribe \
  --source path/to/audio.mp3 \
  --output transcription_output
```

### 3. Voice Selection Help

```bash
# See available voices and recommendations
python podcast_ai_pipeline.py generate --list-voices
```

## 📖 Detailed Usage

### Generate Command Options

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--prompt` | Topic/content prompt for AI generation | `"Quantum computing basics"` |
| `--minutes` | Target duration in minutes | `12` |
| `--speakers` | JSON mapping of speaker names to voices | `'{"HOST":"en_US-lessac-high","GUEST":"en_US-ryan-medium"}'` |
| `--engines` | JSON mapping of speaker names to TTS engines | `'{"HOST":"piper","GUEST":"edge"}'` |
| `--natural` | Enable natural conversation style | (flag) |
| `--speed` | Speaking speed multiplier | `1.2` (20% slower) |
| `--preview-only` | Generate script without audio | (flag) |
| `--output` | Output directory name | `my_podcast` |

### TTS Engine Options

| Engine | Cost | Quality | Setup | Best For |
|--------|------|---------|-------|----------|
| `edge` | Free | Excellent | `pip install edge-tts` | Professional podcasts |
| `piper` | Free | Very Good | Auto-download | Local processing |
| `coqui` | Free | Excellent | `pip install TTS` | Voice cloning |
| `openai` | Paid | Premium | API key only | Commercial production |

### Popular Voice Combinations

**Professional News Style:**
```bash
--speakers '{"HOST":"en-US-AndrewNeural","GUEST":"en-US-EmmaNeural"}' \
--engines '{"HOST":"edge","GUEST":"edge"}'
```

**Casual Conversation:**
```bash
--speakers '{"HOST":"en_US-lessac-medium","GUEST":"en_US-ryan-medium"}' \
--engines '{"HOST":"piper","GUEST":"piper"}'
```

**Educational Content (3 speakers):**
```bash
--speakers '{"HOST":"en-US-AndrewNeural","EXPERT":"en-US-AvaNeural","STUDENT":"en-US-EmmaNeural"}' \
--engines '{"HOST":"edge","EXPERT":"edge","STUDENT":"edge"}'
```

## 💡 Advanced Examples

### Your Dynamic Programming Tutorial (Exact Command)
```bash
# The exact command you used - recreated and working with the modular structure
python podcast_ai_pipeline.py generate \
  --prompt "Solving dynamic programming problems like fibonacci but more importantly, climbing stairs. Assume they're teaching for people that really struggle with the concept of breaking down the solution into an algorithm (logically understanding that a step can be 1 or 2 steps for every step) but struggling with how they equates to the formula for the solution, and the mindset required for future dynamic coding problems. Avoid mathematical formulas that would be awkward in conversational settings to say aloud. Include examples of the host breaking down the complicated explanation into simple terms." \
  --minutes 7 \
  --speakers '{"HOST":"en-US-AndrewNeural","GUEST":"en-US-AvaNeural","EXPERT":"en-US-EmmaNeural"}' \
  --engines '{"HOST":"edge","GUEST":"edge","EXPERT":"edge"}' \
  --natural \
  --speed 1.0 \
  --output dp_tutorial_edge_final
```

### Educational Series
```bash
# Complex topic with slower pace for learning
python podcast_ai_pipeline.py generate \
  --prompt "Machine learning fundamentals: supervised vs unsupervised learning with real-world examples. The host should ask clarifying questions and the expert should use analogies to explain complex concepts." \
  --minutes 15 \
  --speakers '{"HOST":"en-US-AndrewNeural","EXPERT":"en-US-AvaNeural"}' \
  --engines '{"HOST":"edge","EXPERT":"edge"}' \
  --speed 1.3 \
  --natural \
  --output ml_fundamentals
```

### Interview Format
```bash
# Multi-speaker interview with natural conversation
python podcast_ai_pipeline.py generate \
  --prompt "Interview with a startup founder about building a SaaS business from zero to $1M ARR. Include specific challenges, solutions, and advice for aspiring entrepreneurs." \
  --minutes 20 \
  --speakers '{"HOST":"en-US-AndrewNeural","FOUNDER":"en_US-ryan-high","CO_HOST":"en-US-EmmaNeural"}' \
  --engines '{"HOST":"edge","FOUNDER":"piper","CO_HOST":"edge"}' \
  --natural \
  --output startup_interview
```

### Preview Before Generation
```bash
# Generate script first, review it, then create audio
python podcast_ai_pipeline.py generate \
  --prompt "Your topic here" \
  --minutes 10 \
  --speakers '{"HOST":"en-US-AndrewNeural","GUEST":"en-US-AvaNeural"}' \
  --engines '{"HOST":"edge","GUEST":"edge"}' \
  --preview-only \
  --output preview_test

# Review the script in preview_test/podcast_transcript.txt
# If satisfied, run again without --preview-only
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Voice Model Storage
- **Piper voices**: Downloaded to `~/.local/share/piper/`
- **Coqui models**: Cached in `~/.cache/tts/`
- **Edge TTS**: No local storage (cloud-based)

### Output Structure
```
output_directory/
├── podcast_transcript.txt    # Generated script
├── podcast_audio.wav         # Final audio file
└── (temp files cleaned up automatically)
```

## 📦 Dependency Management

This project uses `pip-tools` for clean dependency management:

### Installation Options
```bash
# Core dependencies only
pip install -r requirements.txt

# Full functionality (recommended)
make setup-dev-clean

# Manual setup
pip install pip-tools
make compile-deps
make install-dev
```

### Available Commands
```bash
make help                 # Show all available commands
make setup-dev           # Standard development setup
make setup-dev-clean     # Clean setup (fixes PyTorch conflicts)
make test               # Run import tests
make lint               # Run linting
make format             # Format code
make check              # Run all checks
make clean              # Clean up generated files
```

### Dependency Files
- `requirements.in` - Core dependencies
- `requirements-extra.in` - + TTS engines and optional features
- `requirements-dev.in` - + Development tools

## 🎛️ Performance Tips

### Speed Control
- `--speed 1.0`: Normal conversational pace
- `--speed 1.2-1.5`: Slower for educational content
- `--speed 0.8-0.9`: Faster for energetic content

### Quality vs Speed
- **Edge TTS**: Excellent quality, cloud processing (recommended)
- **Piper**: `high` quality = slower, `medium` = balanced, `low` = fastest
- **Coqui**: Local processing, customizable quality

### Long Content (30+ minutes)
The tool automatically handles long content with intelligent batching:
- Each batch generates ~1800 words
- Maintains conversation continuity
- Progress tracking across all batches

## 🐛 Troubleshooting

### Common Issues

**"No valid dialogue lines found"**
- The AI generated non-dialogue content
- Try running with `--preview-only` to inspect the script
- Adjust your prompt to be more specific about dialogue format

**TTS Voice Download Fails**
- Check internet connection
- Try alternative voices: `python podcast_ai_pipeline.py generate --list-voices`
- Use Edge TTS as fallback: `--engines '{"HOST":"edge","GUEST":"edge"}'`

**Audio Too Short/Long**
- Use `--natural` flag for slower, more detailed conversation
- Adjust `--minutes` parameter
- The tool aims for ~2.5x word count vs natural speech due to TTS speed

**OpenAI API Errors**
- Verify `OPENAI_API_KEY` in `.env` file
- Check API quota and billing
- Try `gpt-4o-mini` model for cost efficiency

**PyTorch/TTS Conflicts**
- Use `make setup-dev-clean` for clean installation
- Or skip Coqui TTS and use Edge TTS only: `make install && pip install edge-tts`

### Import Errors
```bash
# Test all imports
python test_imports.py

# Debug specific import issues
python debug_imports.py
```

### Edge TTS Voice Names
Popular Edge TTS voices for podcasts:
- `en-US-AndrewNeural` (Male, professional)
- `en-US-AvaNeural` (Female, friendly)
- `en-US-EmmaNeural` (Female, warm)
- `en-US-BrianNeural` (Male, casual)
- `en-GB-RyanNeural` (Male, British)

## 📦 Dependencies

Core requirements:
- `openai` - GPT script generation and Whisper transcription
- `pydub` - Audio processing and assembly
- `requests` - Voice model downloads
- `tqdm` - Progress tracking
- `python-dotenv` - Environment variable management

Optional TTS engines:
- `edge-tts` - Microsoft Edge TTS (recommended)
- `TTS` - Coqui TTS with voice cloning
- `yt-dlp` - URL audio downloads for transcription

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional TTS engine integrations
- Enhanced script generation prompts
- Audio post-processing effects
- Batch processing capabilities
- Web interface

## 📝 License

MIT License - See LICENSE file for details.

## 🔗 Related Projects

- [Piper TTS](https://github.com/rhasspy/piper) - Local neural text-to-speech
- [Coqui TTS](https://github.com/coqui-ai/TTS) - Advanced TTS with voice cloning
- [Edge TTS](https://github.com/rany2/edge-tts) - Microsoft Edge text-to-speech
- [OpenAI API](https://platform.openai.com/) - GPT and Whisper models

---