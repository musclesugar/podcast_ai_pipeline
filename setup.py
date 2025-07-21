#!/usr/bin/env python3
"""
Setup script for Podcast AI Pipeline.
"""
from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = (
    readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
)

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="podcast-ai-pipeline",
    version="2.1.0",
    description="A modular tool for generating and transcribing podcasts with AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Podcast AI Pipeline Team",
    author_email="your-email@example.com",
    url="https://github.com/yourusername/podcast-ai-pipeline",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["podcast_ai_pipeline"],
    install_requires=[
        req
        for req in requirements
        if not any(opt in req for opt in ["edge-tts", "TTS", "yt-dlp"])
    ],
    extras_require={
        "edge": ["edge-tts>=6.1.0"],
        "coqui": ["TTS>=0.22.0"],
        "transcribe": ["yt-dlp>=2023.1.6"],
        "all": ["edge-tts>=6.1.0", "TTS>=0.22.0", "yt-dlp>=2023.1.6"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "flake8>=5.0.0"],
    },
    entry_points={
        "console_scripts": [
            "podcast-ai=podcast_ai_pipeline:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Content Creators",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    keywords="podcast, ai, tts, speech-synthesis, audio-generation, openai, whisper",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/podcast-ai-pipeline/issues",
        "Source": "https://github.com/yourusername/podcast-ai-pipeline",
        "Documentation": "https://github.com/yourusername/podcast-ai-pipeline#readme",
    },
)
