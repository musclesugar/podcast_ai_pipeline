# Podcast AI Pipeline - Development Makefile

.PHONY: help install install-dev install-extra install-tts compile-deps clean test lint format check

help:  ## Show this help message
	@echo "Podcast AI Pipeline - Development Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $1, $2}'

install:  ## Install core dependencies only
	pip install -r requirements.txt

install-extra:  ## Install with extra features (Edge TTS, no PyTorch conflicts)
	pip install -r requirements-extra.txt

install-tts:  ## Install with ALL TTS engines including Coqui (may have PyTorch conflicts)
	pip install -r requirements-tts.txt

install-dev:  ## Install development dependencies (safe, no PyTorch)
	pip install -r requirements-dev.txt

install-dev-tts:  ## Install development dependencies WITH TTS (may have conflicts)
	pip install -r requirements-tts-dev.txt

compile-deps:  ## Compile requirements files from .in files
	pip-compile requirements.in
	pip-compile requirements-extra.in
	pip-compile requirements-tts.in
	pip-compile requirements-dev.in
	pip-compile requirements-tts-dev.in

upgrade-deps:  ## Upgrade all dependencies and recompile
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-extra.in
	pip-compile --upgrade requirements-tts.in
	pip-compile --upgrade requirements-dev.in
	pip-compile --upgrade requirements-tts-dev.in

test:  ## Run tests
	python test_imports.py
	@echo "✅ Import tests passed!"

test-voice-list:  ## Test voice listing (no API calls)
	python podcast_ai_pipeline.py generate --list-voices

lint:  ## Run linting
	flake8 src/ podcast_ai_pipeline.py
	mypy src/ podcast_ai_pipeline.py

format:  ## Format code
	black src/ podcast_ai_pipeline.py examples/ *.py
	isort src/ podcast_ai_pipeline.py examples/ *.py

check:  ## Run all checks (test + lint + format check)
	@echo "🔍 Running format check..."
	black --check src/ podcast_ai_pipeline.py examples/ *.py
	isort --check-only src/ podcast_ai_pipeline.py examples/ *.py
	@echo "🔍 Running linting..."
	flake8 src/ podcast_ai_pipeline.py
	@echo "🔍 Running tests..."
	python test_imports.py
	@echo "✅ All checks passed!"

clean:  ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf *.egg-info/
	rm -rf dist/
	rm -rf build/
	@echo "🧹 Cleaned Python cache files"

clean-output:  ## Clean all generated content (output directory)
	@echo "🧹 Cleaning output directory..."
	rm -rf output/
	@echo "✅ Output directory cleaned"

clean-all:  ## Clean everything (cache + output)
	$(MAKE) clean
	$(MAKE) clean-output
	@echo "✅ Full cleanup complete"

setup-dev:  ## Complete development setup (safe, no PyTorch conflicts)
	@echo "🚀 Setting up development environment (safe mode)..."
	pip install pip-tools
	$(MAKE) compile-deps
	$(MAKE) install-dev
	@echo "📝 Don't forget to create your .env file:"
	@echo "   cp .env.example .env"
	@echo "   # Edit .env and add your OPENAI_API_KEY"
	@echo "✅ Development setup complete!"
	@echo "💡 Your setup includes Edge TTS (no PyTorch conflicts)"
	@echo "💡 For Coqui TTS: make install-tts"

setup-dev-full:  ## Complete development setup WITH all TTS engines
	@echo "🚀 Setting up development environment with ALL TTS engines..."
	pip install pip-tools
	$(MAKE) compile-deps
	$(MAKE) install-dev-tts
	@echo "📝 Don't forget to create your .env file:"
	@echo "   cp .env.example .env"
	@echo "   # Edit .env and add your OPENAI_API_KEY"
	@echo "✅ Full development setup complete!"

example-basic:  ## Run basic example
	python examples/basic_generate.py

example-advanced:  ## Run advanced example (your DP tutorial)
	python examples/advanced_generate.py

example-system-design:  ## Run system design interview example (Netflix)
	python examples/system_design_interview.py