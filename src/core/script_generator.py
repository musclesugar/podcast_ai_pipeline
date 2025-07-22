"""
GPT-powered script generation with intelligent approach selection.
"""
import openai
from typing import List
from tqdm import tqdm

from config.settings import (
    WPM_NATURAL, WPM_PROFESSIONAL, TTS_MULTIPLIER, MAX_WORDS_PER_BATCH,
    DEFAULT_TEMPERATURE_NATURAL, DEFAULT_TEMPERATURE_PROFESSIONAL
)


class ScriptGenerator:
    """Handles AI-powered podcast script generation with intelligent approach selection."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
    
    def generate_script(self, prompt: str, minutes: int, speakers: List[str], natural_style: bool = False, output_dir = None) -> str:
        """Generate podcast script with intelligent approach selection."""
        target_words = self._estimate_words(minutes, natural_style)
        
        print("🤖 Generating podcast script with GPT...")
        style_desc = "natural conversational" if natural_style else "professional"
        print(f"🎯 Target: {minutes} minutes = ~{target_words} words ({style_desc} style)")
        
        # Use LLM to determine if content would benefit from structured approach
        use_structured = self._should_use_structured_approach(prompt, minutes)
        
        if use_structured:
            print("🧠 Using structured outline-first approach for complex content...")
            from core.structured_script_generator import StructuredScriptGenerator
            structured_generator = StructuredScriptGenerator(self.model)
            script, outline = structured_generator.generate_structured_script(prompt, minutes, speakers, natural_style, output_dir)
            return script
        
        # Use existing approach for simpler content
        print("⚡ Using streamlined approach for straightforward content...")
        if target_words <= MAX_WORDS_PER_BATCH:
            return self._generate_single_script(prompt, minutes, speakers, natural_style, target_words)
        else:
            return self._generate_batched_script(prompt, minutes, speakers, natural_style, target_words)
    
    def _should_use_structured_approach(self, prompt: str, minutes: int) -> bool:
        """Use LLM to intelligently determine if content needs structured approach."""
        
        # Always use structured for very long content
        if minutes >= 20:
            return True
        
        # Use lightweight LLM call to analyze content complexity
        analysis_prompt = f"""Analyze this podcast topic and determine if it would benefit from a structured, outline-first approach:

Topic: "{prompt}"
Duration: {minutes} minutes

A structured approach is better for content that:
- Has multiple logical sections or phases
- Requires building understanding progressively 
- Involves complex technical concepts
- Is educational or instructional in nature
- Has natural breakpoints or chapters
- Involves interviews, tutorials, or deep dives

A simple approach is better for:
- Casual conversations or discussions
- Simple Q&A format
- Single-concept explanations
- Short, focused topics
- Natural flowing dialogue

Respond with only "STRUCTURED" or "SIMPLE" and a brief 1-sentence reason."""

        try:
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",  # Use fastest model for this analysis
                messages=[
                    {"role": "system", "content": "You are a content strategist. Analyze if podcast content needs structured or simple generation approach."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,  # Low temperature for consistent analysis
                max_tokens=50,    # Keep response short
            )
            
            response = resp.choices[0].message.content.strip().upper()
            
            # Parse response
            if "STRUCTURED" in response:
                print(f"🧠 LLM Analysis: Using structured approach - {response.split('STRUCTURED')[1].strip()}")
                return True
            else:
                print(f"⚡ LLM Analysis: Using simple approach - {response.split('SIMPLE')[1].strip() if 'SIMPLE' in response else 'straightforward content'}")
                return False
                
        except Exception as e:
            print(f"⚠️ Analysis failed ({e}), falling back to duration-based logic")
            # Fallback: use structured for longer content
            return minutes >= 15
    
    def _estimate_words(self, minutes: int, natural_style: bool = False) -> int:
        """Estimate target words needed for desired duration, accounting for TTS speed."""
        base_wpm = WPM_NATURAL if natural_style else WPM_PROFESSIONAL
        # TTS systems speak faster than humans, so we need more words
        target_words = int(minutes * base_wpm * TTS_MULTIPLIER)
        return target_words
    
    def _generate_single_script(self, prompt: str, minutes: int, speakers: List[str], 
                               natural_style: bool, target_words: int) -> str:
        """Generate a single script without batching."""
        system_prompt = self._build_system_prompt(target_words, speakers, natural_style)
        user_prompt = self._build_user_prompt(prompt, target_words, minutes, speakers)
        
        temperature = DEFAULT_TEMPERATURE_NATURAL if natural_style else DEFAULT_TEMPERATURE_PROFESSIONAL
        
        with tqdm(total=1, desc=f"GPT Script") as pbar:
            resp = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
            )
            pbar.update(1)
        
        return resp.choices[0].message.content.strip()
    
    def _generate_batched_script(self, prompt: str, minutes: int, speakers: List[str], 
                                natural_style: bool, target_words: int) -> str:
        """Generate script in batches for longer content and stitch them together."""
        num_batches = max(2, (target_words + MAX_WORDS_PER_BATCH - 1) // MAX_WORDS_PER_BATCH)
        words_per_batch = target_words // num_batches
        
        print(f"📦 Using {num_batches} batches of ~{words_per_batch} words each")
        
        # Define sections for the batches
        sections = [
            "introduction and problem setup",
            "core concept explanation with examples", 
            "detailed algorithm walkthrough",
            "common mistakes and mindset shifts",
            "advanced techniques and conclusion"
        ]
        
        # Ensure we have enough sections
        while len(sections) < num_batches:
            sections.append(f"detailed discussion part {len(sections) - 3}")
        
        all_scripts = []
        temperature = DEFAULT_TEMPERATURE_NATURAL if natural_style else DEFAULT_TEMPERATURE_PROFESSIONAL
        
        with tqdm(total=num_batches, desc="GPT Batches") as pbar:
            for i in range(num_batches):
                is_first = i == 0
                is_last = i == num_batches - 1
                section = sections[i] if i < len(sections) else f"section {i + 1}"
                
                batch_system = self._create_batch_system_prompt(
                    words_per_batch, speakers, natural_style, is_first, is_last, section
                )
                
                batch_user = self._create_batch_user_prompt(
                    prompt, words_per_batch, speakers, is_first, is_last, section, i + 1, num_batches
                )
                
                resp = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": batch_system}, 
                        {"role": "user", "content": batch_user}
                    ],
                    temperature=temperature,
                )
                
                batch_script = resp.choices[0].message.content.strip()
                all_scripts.append(batch_script)
                pbar.update(1)
        
        # Stitch scripts together
        return self._stitch_script_batches(all_scripts, speakers)
    
    def _build_system_prompt(self, target_words: int, speakers: List[str], natural_style: bool) -> str:
        """Build the system prompt for script generation."""
        base_system = (
            "You are a professional podcast script writer. Write engaging dialogue between the specified speakers."
            f" The script should be approximately {target_words} words total - this is CRITICAL for proper timing."
            f" TARGET: {target_words} words. You MUST write enough content to reach this word count."
            " FORMAT REQUIREMENTS:"
            " - Each line should start with SPEAKER_NAME: followed by their dialogue"
            " - Use ONLY the exact speaker names provided (case-sensitive)"
            " - Each speaker line should be on its own line"
            " - NEVER include prefixes like 'text:', 'voice:', 'says:', 'speaks:', 'dialogue:', or 'response:' before the actual speech"
            " - Do not include ANY metadata, tags, labels, stage directions, sound effects, timestamps, code blocks, bullet points, or markdown formatting"
            " - Keep all content as pure spoken dialogue only - what the speakers would actually say out loud"
            " - No explanatory text or descriptions - only the words that would be spoken"
            " - Format example: 'HOST: Welcome to the show!' NOT 'HOST: text: Welcome to the show!'"
            " - Include natural transitions and back-and-forth conversation"
            " - Write substantial, detailed responses - avoid short exchanges"
            " - Each speaker should have multiple longer paragraphs of dialogue to reach the word count"
            " - Include thorough explanations, examples, and detailed discussions"
        )
        
        if natural_style:
            natural_additions = (
                " NATURAL CONVERSATION STYLE (use sparingly - TTS voices handle this differently):"
                " - Add occasional thinking pauses with '...' (not every sentence)"
                " - Include some self-correction: 'Actually, let me put it this way...', 'What I mean is...'"
                " - Show moments of realization: 'Oh! That makes sense now', 'Aha, I see what you mean'"
                " - Use natural transitions: 'So here's the thing...', 'Now, the key point is...'"
                " - Add enthusiasm and genuine reactions: 'That's fascinating!', 'Exactly!'"
                " - AVOID 'um', 'uh', 'like' - these sound awkward in TTS"
                " - Focus on natural phrasing and conversational flow instead of verbal fillers"
                " - Make it sound like thoughtful, engaging conversation rather than robotic exchange"
            )
            return base_system + natural_additions
        else:
            return base_system + " - Keep dialogue conversational but clear and professional"
    
    def _build_user_prompt(self, prompt: str, target_words: int, minutes: int, speakers: List[str]) -> str:
        """Build the user prompt for script generation."""
        return (
            f"Topic: {prompt}\n"
            f"CRITICAL REQUIREMENT: Target length: {minutes} minutes = EXACTLY {target_words} words\n"
            f"Speakers: {', '.join(speakers)}\n\n"
            "Write an engaging podcast script using the exact speaker names provided. "
            f"THE SCRIPT MUST CONTAIN APPROXIMATELY {target_words} WORDS TO ACHIEVE {minutes} MINUTES OF AUDIO. "
            f"This is not a suggestion - it's a requirement. Write {target_words} words of dialogue. "
            "Write substantial, detailed responses with thorough explanations and examples. "
            "Each speaker should have multiple long turns speaking to build up the word count. "
            "Make it educational but conversational, with natural back-and-forth dialogue that covers the topic comprehensively. "
            "Include detailed examples, step-by-step explanations, and extensive discussion to reach the target word count. "
            "Give the speakers names and titles where relevant. The host should be intelligent but represent the viewer who isn't familiar with the topic. "
            "The host should introduce the guest and the expert if included, and as a part of their introductions, who they are and why they're there. "
            "If the host has a specific question for a specific speaker, he should ask them directly. And he should frequently be asking clarifying questions as hosts typically do. "
        )
    
    def _create_batch_system_prompt(self, words_per_batch: int, speakers: List[str], natural_style: bool, 
                                   is_first: bool, is_last: bool, section: str) -> str:
        """Create system prompt for a batch."""
        base = (
            "You are a professional podcast script writer creating a segment of a longer podcast."
            f" This segment should be approximately {words_per_batch} words and focus on: {section}."
            " FORMAT REQUIREMENTS:"
            " - Each line should start with SPEAKER_NAME: followed by their dialogue"
            f" - Use ONLY these exact speaker names: {', '.join(speakers)}"
            " - Each speaker line should be on its own line"
            " - NEVER include prefixes like 'text:', 'voice:', 'says:', 'speaks:' before the actual speech"
            " - NEVER include markdown blocks like ```text or standalone words like 'text', 'voice', 'dialogue'"
            " - Keep all content as pure spoken dialogue only"
            " - Format example: 'HOST: Welcome to the show!' NOT 'HOST: text: Welcome to the show!' NOT 'HOST: ```text Welcome to the show!'"
        )
        
        if is_first:
            base += " - This is the OPENING segment, so include introductions and topic setup"
        elif is_last:
            base += " - This is the CLOSING segment, so include summary and conclusions"
        else:
            base += " - This is a MIDDLE segment, so continue the conversation naturally from previous discussion"
        
        if natural_style:
            base += (
                " NATURAL STYLE: Include pauses with '...', "
                "interruptions, self-corrections, and genuine reactions."
            )
        
        return base
    
    def _create_batch_user_prompt(self, prompt: str, words_per_batch: int, speakers: List[str], 
                                 is_first: bool, is_last: bool, section: str, batch_num: int, total_batches: int) -> str:
        """Create user prompt for a batch."""
        return (
            f"Topic: {prompt}\n"
            f"Segment: {section} (Part {batch_num} of {total_batches})\n"
            f"Target: {words_per_batch} words for this segment\n"
            f"Speakers: {', '.join(speakers)}\n\n"
            f"Write a {words_per_batch}-word podcast segment focusing on {section}. "
            f"{'Start with introductions and topic setup. ' if is_first else ''}"
            f"{'End with conclusions and wrap-up. ' if is_last else ''}"
            "Write substantial, detailed dialogue with thorough explanations and examples."
        )
    
    def _stitch_script_batches(self, scripts: List[str], speakers: List[str]) -> str:
        """Intelligently stitch script batches together with smooth transitions."""
        if not scripts:
            return ""
        
        if len(scripts) == 1:
            return scripts[0]
        
        # Simple concatenation for now - could add transition logic later
        stitched = scripts[0]
        for script in scripts[1:]:
            # Add a small transition buffer
            stitched += "\n" + script
        
        return stitched