"""
Dynamic structured script generation with LLM-powered outline creation for any topic.
"""
import json
import openai
from typing import List, Dict, Any
from tqdm import tqdm

from config.settings import (
    WPM_NATURAL, WPM_PROFESSIONAL, TTS_MULTIPLIER, 
    DEFAULT_TEMPERATURE_NATURAL, DEFAULT_TEMPERATURE_PROFESSIONAL
)

class StructuredScriptGenerator:
    """Handles structured podcast script generation with dynamic outline creation for any topic."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
    
    def generate_structured_script(self, prompt: str, minutes: int, speakers: List[str], 
                                 natural_style: bool = False, output_dir = None) -> tuple[str, Dict[str, Any]]:
        """Generate script using dynamic structured outline-first approach for any topic."""
        target_words = self._estimate_words(minutes, natural_style)
        
        print("🧠 Generating structured podcast script...")
        style_desc = "natural conversational" if natural_style else "professional"
        print(f"🎯 Target: {minutes} minutes = ~{target_words} words ({style_desc} style)")
        
        # Step 1: Generate topic-aware outline
        print("📋 Step 1: Creating dynamic content outline...")
        outline = self._generate_dynamic_outline(prompt, minutes, speakers, natural_style)
        
        # Save outline if output directory provided
        if output_dir:
            self._save_outline(outline, output_dir, prompt)
        
        # Step 2: Generate dynamic introduction
        print("🎭 Step 2: Creating topic-specific introduction...")
        introduction = self._generate_dynamic_introduction(prompt, speakers, outline, natural_style)
        
        # Step 3: Generate script sections based on outline
        print("✍️ Step 3: Writing detailed sections...")
        sections = self._generate_sections_from_outline(outline, speakers, natural_style, target_words - len(introduction.split()))
        
        # Step 4: Stitch everything together with smart transitions
        print("🔗 Step 4: Adding intelligent transitions and final polish...")
        final_script = self._stitch_with_introduction(introduction, sections, speakers, natural_style, prompt)
        
        return final_script, outline
    
    def _generate_dynamic_introduction(self, prompt: str, speakers: List[str], outline: Dict[str, Any], natural_style: bool) -> str:
        """Generate a topic-specific introduction for the podcast."""
        
        # Get section titles for preview
        sections = outline.get('sections', [])
        section_titles = [s.get('title', '') for s in sections[:4]]  # First 4 sections
        
        intro_prompt = f"""Create a natural, engaging podcast introduction for this topic:

TOPIC: {prompt}
SPEAKERS: {', '.join(speakers)} (typically first is host, others are guests/experts)
UPCOMING SECTIONS: {', '.join(section_titles)}

Create a natural introduction (100-150 words) that:
1. Has the host welcome listeners and introduce the topic
2. Briefly introduces any guests/experts and their credentials 
3. Gives listeners a preview of what they'll learn
4. Sets the right tone for the content type (interview, tutorial, discussion, etc.)
5. Creates excitement and engagement

Format as dialogue with speaker names. Make it sound natural and conversational.
The host should set context and the guest should add credibility or perspective."""

        try:
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Create engaging, natural podcast introductions that set the right tone and context."},
                    {"role": "user", "content": intro_prompt}
                ],
                temperature=0.7,
                max_tokens=200,
            )
            
            introduction = resp.choices[0].message.content.strip()
            
            # Clean up any unwanted formatting
            introduction = self._clean_section_script(introduction, True)  # True = allow intro language
            
            return introduction
            
        except Exception as e:
            print(f"⚠️ Could not generate dynamic introduction: {e}")
            # Fallback introduction
            host = speakers[0] if speakers else "HOST"
            guest = speakers[1] if len(speakers) > 1 else "GUEST"
            
            return f"""{host}: Welcome to today's podcast! I'm excited to dive deep into an important topic with our expert guest.

{guest}: Thanks for having me! Looking forward to sharing some insights on this fascinating subject.

{host}: Perfect! Today we're going to explore this topic in detail, covering everything from the fundamentals to advanced applications. Let's get started!"""
    
    def _stitch_with_introduction(self, introduction: str, sections: List[Dict[str, str]], 
                                speakers: List[str], natural_style: bool, prompt: str) -> str:
        """Stitch introduction with sections using intelligent transitions."""
        if not sections:
            return introduction
        
        script_parts = [introduction]
        
        # Add transition from intro to first section
        if sections:
            intro_transition = self._generate_intro_to_content_transition(
                introduction, sections[0], speakers, prompt
            )
            if intro_transition:
                script_parts.append(intro_transition)
        
        # Add all sections with transitions
        for i, section in enumerate(sections):
            # Clean up section script
            cleaned_script = self._clean_section_script(section['script'], False)  # False = no intro language
            script_parts.append(cleaned_script)
            
            # Add transition to next section (except for last section)
            if i < len(sections) - 1:
                transition = self._generate_intelligent_transition(
                    section, sections[i + 1], speakers, natural_style, prompt
                )
                if transition:
                    script_parts.append(transition)
        
        return '\n\n'.join(script_parts)
    
    def _generate_intro_to_content_transition(self, introduction: str, first_section: Dict[str, str], 
                                            speakers: List[str], prompt: str) -> str:
        """Generate transition from introduction to the first content section."""
        
        host = speakers[0] if speakers else "HOST"
        first_section_title = first_section.get('title', 'our discussion')
        first_section_info = first_section.get('section_info', {})
        
        # Create contextual transition based on content type
        prompt_lower = prompt.lower()
        
        if 'interview' in prompt_lower or 'design' in prompt_lower:
            return f"{host}: Alright, let's dive right in. I'd like to start with {first_section_title.lower()}. What's your approach here?"
        elif 'tutorial' in prompt_lower or 'guide' in prompt_lower:
            return f"{host}: Let's begin with the fundamentals. First, we need to understand {first_section_title.lower()}."
        else:
            return f"{host}: So let's start our exploration with {first_section_title.lower()}. What should our listeners know first?"
    
    def _save_outline(self, outline: Dict[str, Any], output_dir, prompt: str) -> None:
        """Save the generated outline to the output directory."""
        import json
        from pathlib import Path
        
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Create a readable outline file
            outline_content = {
                "topic": prompt,
                "generation_method": "dynamic_structured_approach",
                "total_sections": len(outline.get('sections', [])),
                "sections": []
            }
            
            for i, section in enumerate(outline.get('sections', []), 1):
                outline_content["sections"].append({
                    "section_number": i,
                    "title": section.get('title', f'Section {i}'),
                    "duration_minutes": section.get('duration_minutes', 0),
                    "objective": section.get('objective', ''),
                    "talking_points": section.get('talking_points', []),
                    "speaker_dynamics": section.get('speaker_dynamics', '')
                })
            
            # Save as JSON
            json_path = output_path / "content_outline.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(outline_content, f, indent=2, ensure_ascii=False)
            
            # Also save as readable text
            txt_path = output_path / "content_outline.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"PODCAST CONTENT OUTLINE\n")
                f.write(f"{'=' * 50}\n\n")
                f.write(f"Topic: {prompt}\n")
                f.write(f"Generation Method: Dynamic Structured Approach\n")
                f.write(f"Total Sections: {len(outline.get('sections', []))}\n\n")
                
                for i, section in enumerate(outline.get('sections', []), 1):
                    f.write(f"SECTION {i}: {section.get('title', f'Section {i}')}\n")
                    f.write(f"Duration: {section.get('duration_minutes', 0)} minutes\n")
                    f.write(f"Objective: {section.get('objective', '')}\n")
                    f.write(f"Speaker Dynamics: {section.get('speaker_dynamics', '')}\n")
                    f.write(f"Talking Points:\n")
                    for point in section.get('talking_points', []):
                        f.write(f"  • {point}\n")
                    f.write(f"\n{'-' * 40}\n\n")
            
            print(f"📄 Outline saved to:")
            print(f"   • {json_path} (structured data)")
            print(f"   • {txt_path} (human readable)")
            
        except Exception as e:
            print(f"⚠️ Could not save outline: {e}")
            # Don't fail the whole generation if outline saving fails
    
    def _estimate_words(self, minutes: int, natural_style: bool = False) -> int:
        """Estimate target words needed for desired duration."""
        base_wpm = WPM_NATURAL if natural_style else WPM_PROFESSIONAL
        target_words = int(minutes * base_wpm * TTS_MULTIPLIER)
        return target_words
    
    def _generate_dynamic_outline(self, prompt: str, minutes: int, speakers: List[str], natural_style: bool) -> Dict[str, Any]:
        """Generate a topic-aware content outline using direct LLM generation."""
        
        # Create a very explicit outline generation prompt
        outline_prompt = f"""Create a detailed podcast outline for this topic. Be very specific and structured.

TOPIC: {prompt}
SPEAKERS: {', '.join(speakers)}
DURATION: {minutes} minutes

Generate 5-7 logical sections that cover this topic comprehensively. For each section:

1. Give it a clear, descriptive title (what will be discussed)
2. Assign realistic duration (sections should total {minutes} minutes)
3. Define specific objective (what should be accomplished)
4. List 3-4 concrete talking points (actual content to discuss)
5. Describe how speakers should interact

Return ONLY a valid JSON structure like this:
{{
  "sections": [
    {{
      "title": "Clear descriptive title",
      "duration_minutes": 4,
      "objective": "Specific goal for this section",
      "talking_points": [
        "First specific point to discuss",
        "Second technical detail to cover", 
        "Third concept to explain"
      ],
      "speaker_dynamics": "How speakers interact in this section"
    }}
  ]
}}

Make each section focus on different aspects of the topic with specific, actionable talking points."""

        with tqdm(total=1, desc="Generating structured outline") as pbar:
            resp = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a content strategist. Create structured, logical podcast outlines in valid JSON format. Focus on specific, actionable content for each section."},
                    {"role": "user", "content": outline_prompt}
                ],
                temperature=0.5,  # Lower temperature for more structured output
            )
            pbar.update(1)
        
        outline_text = resp.choices[0].message.content.strip()
        
        # Try to parse JSON first
        try:
            # Clean up the response to get just the JSON
            json_start = outline_text.find('{')
            json_end = outline_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_text = outline_text[json_start:json_end]
                outline = json.loads(json_text)
                
                # Validate the structure
                if 'sections' in outline and outline['sections']:
                    # Normalize durations
                    total_duration = sum(s.get('duration_minutes', 0) for s in outline['sections'])
                    if total_duration > 0:
                        for section in outline['sections']:
                            section['duration_minutes'] = max(1, int((section.get('duration_minutes', 1) / total_duration) * minutes))
                    
                    print(f"✅ Created structured outline with {len(outline['sections'])} sections")
                    return outline
        except (json.JSONDecodeError, KeyError):
            pass
        
        # If JSON parsing fails, create intelligent fallback
        print("⚠️ JSON parsing failed, creating intelligent fallback outline...")
        return self._create_topic_specific_fallback(prompt, minutes)
    
    def _create_topic_specific_fallback(self, prompt: str, minutes: int) -> Dict[str, Any]:
        """Create topic-specific fallback outline using LLM analysis."""
        
        # Analyze the topic to create appropriate sections
        analysis_prompt = f"""Analyze this topic and create 5-6 logical section titles for a {minutes}-minute discussion:

TOPIC: {prompt}

Create sections that:
1. Flow logically from introduction to conclusion
2. Cover different aspects of the topic
3. Build understanding progressively
4. Are appropriate for the subject matter

Return just a numbered list of clear section titles, nothing else."""

        try:
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Create logical section titles for any topic."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.4,
                max_tokens=200,
            )
            
            section_titles = []
            for line in resp.choices[0].message.content.strip().split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up the title
                    title = line.lstrip('1234567890.-•').strip()
                    if len(title) > 5:  # Valid title
                        section_titles.append(title)
            
            # Create structured sections from titles
            if section_titles:
                base_duration = max(2, minutes // len(section_titles))
                sections = []
                
                for i, title in enumerate(section_titles):
                    # Generate talking points for each section
                    talking_points = self._generate_talking_points_for_section(title, prompt)
                    
                    sections.append({
                        'title': title,
                        'duration_minutes': base_duration,
                        'objective': f'Thoroughly explore {title.lower()} with practical examples and insights',
                        'talking_points': talking_points,
                        'speaker_dynamics': 'Interactive discussion with questions and detailed explanations'
                    })
                
                return {'sections': sections}
                
        except Exception:
            pass
        
        # Ultimate fallback - create generic but functional sections
        return self._create_universal_fallback_sections(prompt, minutes)
    
    def _generate_talking_points_for_section(self, section_title: str, original_prompt: str) -> List[str]:
        """Generate specific talking points for a section."""
        
        points_prompt = f"""For this podcast section, generate 3-4 specific talking points:

SECTION: {section_title}
OVERALL TOPIC: {original_prompt}

Create concrete, actionable talking points that:
- Are specific to this section
- Provide real value and insights
- Can be discussed with examples
- Build understanding of the topic

Return just a simple list of talking points, one per line."""

        try:
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate specific, actionable talking points for podcast sections."},
                    {"role": "user", "content": points_prompt}
                ],
                temperature=0.6,
                max_tokens=150,
            )
            
            points = []
            for line in resp.choices[0].message.content.strip().split('\n'):
                line = line.strip().lstrip('-•*').strip()
                if len(line) > 10:  # Valid talking point
                    points.append(line)
            
            return points if points else [
                f"Key concepts and principles of {section_title.lower()}",
                f"Practical applications and real-world examples",
                f"Common challenges and how to address them"
            ]
            
        except Exception:
            return [
                f"Core concepts of {section_title.lower()}",
                f"Practical examples and applications", 
                f"Key insights and takeaways"
            ]
    
    def _create_universal_fallback_sections(self, prompt: str, minutes: int) -> Dict[str, Any]:
        """Create universal fallback sections that work for any topic."""
        base_duration = max(2, minutes // 5)
        
        # Determine topic type to customize sections
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['design', 'system', 'architecture', 'build']):
            # Technical/Design topic
            return {
                'sections': [
                    {
                        'title': 'Problem Definition and Requirements',
                        'duration_minutes': base_duration,
                        'objective': 'Clearly define the problem scope and key requirements',
                        'talking_points': [
                            'Problem statement and context',
                            'Functional requirements identification', 
                            'Non-functional requirements and constraints',
                            'Success criteria definition'
                        ],
                        'speaker_dynamics': 'Interviewer guides requirements gathering, candidate asks clarifying questions'
                    },
                    {
                        'title': 'High-Level Approach and Strategy',
                        'duration_minutes': base_duration,
                        'objective': 'Outline the overall approach and key design decisions',
                        'talking_points': [
                            'Overall architecture and approach',
                            'Key components and their interactions',
                            'Technology choices and trade-offs',
                            'Design principles and patterns'
                        ],
                        'speaker_dynamics': 'Candidate explains approach, interviewer challenges decisions'
                    },
                    {
                        'title': 'Detailed Design and Implementation',
                        'duration_minutes': base_duration,
                        'objective': 'Deep dive into specific design aspects and implementation details',
                        'talking_points': [
                            'Detailed component design',
                            'Data structures and algorithms',
                            'Implementation considerations',
                            'Integration patterns'
                        ],
                        'speaker_dynamics': 'Interactive discussion with technical details and examples'
                    },
                    {
                        'title': 'Scaling and Performance Considerations',
                        'duration_minutes': base_duration,
                        'objective': 'Address scalability, performance, and operational concerns',
                        'talking_points': [
                            'Scalability bottlenecks and solutions',
                            'Performance optimization strategies',
                            'Monitoring and observability',
                            'Operational considerations'
                        ],
                        'speaker_dynamics': 'Candidate proposes solutions, interviewer explores edge cases'
                    },
                    {
                        'title': 'Edge Cases and Future Considerations',
                        'duration_minutes': base_duration,
                        'objective': 'Discuss edge cases, failure scenarios, and future improvements',
                        'talking_points': [
                            'Edge cases and failure scenarios',
                            'Error handling and recovery',
                            'Future enhancements and extensibility',
                            'Lessons learned and best practices'
                        ],
                        'speaker_dynamics': 'Final discussion covering remaining concerns and wrap-up'
                    }
                ]
            }
        else:
            # General topic structure
            return {
                'sections': [
                    {
                        'title': 'Introduction and Context',
                        'duration_minutes': base_duration,
                        'objective': 'Introduce the topic and provide necessary context',
                        'talking_points': [
                            'Topic introduction and importance',
                            'Historical context or background',
                            'Current state and relevance',
                            'What listeners will learn'
                        ],
                        'speaker_dynamics': 'Host introduces topic, expert provides overview and context'
                    },
                    {
                        'title': 'Core Concepts and Principles',
                        'duration_minutes': base_duration,
                        'objective': 'Explain the fundamental concepts and principles',
                        'talking_points': [
                            'Key definitions and terminology',
                            'Fundamental principles and concepts',
                            'How different elements relate to each other',
                            'Common misconceptions to address'
                        ],
                        'speaker_dynamics': 'Expert explains concepts, host asks clarifying questions'
                    },
                    {
                        'title': 'Practical Applications and Examples',
                        'duration_minutes': base_duration,
                        'objective': 'Demonstrate practical applications with real-world examples',
                        'talking_points': [
                            'Real-world applications and use cases',
                            'Step-by-step examples or case studies',
                            'Best practices and proven approaches',
                            'Common pitfalls and how to avoid them'
                        ],
                        'speaker_dynamics': 'Interactive discussion with detailed examples and scenarios'
                    },
                    {
                        'title': 'Advanced Topics and Insights',
                        'duration_minutes': base_duration,
                        'objective': 'Explore advanced aspects and provide deeper insights',
                        'talking_points': [
                            'Advanced techniques and strategies',
                            'Industry trends and future directions',
                            'Expert insights and personal experiences',
                            'Cutting-edge developments'
                        ],
                        'speaker_dynamics': 'Expert shares advanced insights, host explores implications'
                    },
                    {
                        'title': 'Key Takeaways and Action Items',
                        'duration_minutes': base_duration,
                        'objective': 'Summarize key insights and provide actionable takeaways',
                        'talking_points': [
                            'Most important lessons learned',
                            'Actionable steps listeners can take',
                            'Resources for further learning',
                            'Final thoughts and recommendations'
                        ],
                        'speaker_dynamics': 'Collaborative summary with practical advice for listeners'
                    }
                ]
            }
    
    def _analyze_topic_structure(self, prompt: str, minutes: int) -> str:
        """Analyze the topic to understand its natural structure and flow."""
        analysis_prompt = f"""Analyze this podcast topic to understand its natural structure:

TOPIC: "{prompt}"
DURATION: {minutes} minutes

Provide a brief analysis covering:
1. Content type (interview, tutorial, discussion, debate, etc.)
2. Natural progression (how should concepts build on each other?)
3. Key themes or phases that should be covered
4. Appropriate depth level for the given duration
5. Best speaker dynamics for this content

Keep the analysis concise but insightful - focus on structural insights that will help create a logical outline."""

        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a content analysis expert. Analyze topics to understand their natural structure and flow."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3,
            max_tokens=200,
        )
        
        return resp.choices[0].message.content.strip()
    
    def _parse_dynamic_outline(self, outline_text: str, total_minutes: int, original_prompt: str) -> Dict[str, Any]:
        """Parse outline text into structured format with intelligent fallbacks."""
        lines = outline_text.split('\n')
        sections = []
        current_section = None
        
        # Look for section patterns dynamically
        section_patterns = ['##', '**', 'Section', 'Part', 'Phase', 'Step', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.']
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this looks like a section header
            is_section_header = any(pattern in line for pattern in section_patterns) and len(line) < 120
            
            if is_section_header:
                # Save previous section
                if current_section and current_section.get('talking_points'):
                    sections.append(current_section)
                
                # Start new section
                title = self._clean_section_title(line)
                current_section = {
                    'title': title,
                    'duration_minutes': max(2, total_minutes // 6),  # Default duration
                    'objective': f'Cover {title.lower()} comprehensively',
                    'talking_points': [],
                    'speaker_dynamics': 'Interactive discussion with detailed explanations'
                }
            elif current_section and line:
                # Parse different types of content
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    # This is a talking point
                    point = line.lstrip('-•*').strip()
                    if len(point) > 15:  # Filter out very short points
                        current_section['talking_points'].append(point)
                elif 'objective:' in line.lower():
                    objective = line.split(':', 1)[1].strip()
                    current_section['objective'] = objective
                elif 'duration:' in line.lower() or 'minutes:' in line.lower():
                    # Try to extract duration
                    import re
                    duration_match = re.search(r'(\d+)', line)
                    if duration_match:
                        current_section['duration_minutes'] = int(duration_match.group(1))
                elif len(current_section['talking_points']) == 0 and len(line) > 20:
                    # Use as objective if no talking points yet
                    current_section['objective'] = line
        
        # Add the last section
        if current_section and current_section.get('talking_points'):
            sections.append(current_section)
        
        # If no good sections found, create intelligent fallback
        if not sections:
            sections = self._create_intelligent_fallback_sections(original_prompt, total_minutes)
        
        # Adjust durations to sum to total_minutes
        self._normalize_section_durations(sections, total_minutes)
        
        return {'sections': sections, 'original_prompt': original_prompt}
    
    def _clean_section_title(self, title: str) -> str:
        """Clean up section title by removing formatting."""
        # Remove common formatting
        title = title.replace('#', '').replace('**', '').replace('Section', '').replace('Part', '').strip()
        title = title.lstrip('12345678.').strip()
        title = title.replace(':', '').strip()
        return title if title else "Discussion Section"
    
    def _create_intelligent_fallback_sections(self, prompt: str, total_minutes: int) -> List[Dict[str, Any]]:
        """Create intelligent fallback sections when parsing fails."""
        # Use LLM to create basic sections when parsing fails
        fallback_prompt = f"""The topic is: "{prompt}"

Create 4-6 logical sections for a {total_minutes}-minute discussion. For each section, provide:
- A clear title
- 2-3 key talking points

Make the sections flow logically and build understanding progressively."""

        try:
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Create logical sections for any topic."},
                    {"role": "user", "content": fallback_prompt}
                ],
                temperature=0.5,
                max_tokens=300,
            )
            
            # Parse the response into sections
            fallback_text = resp.choices[0].message.content.strip()
            base_duration = max(2, total_minutes // 5)
            
            sections = []
            for i, line in enumerate(fallback_text.split('\n')):
                if line.strip() and (i % 3 == 0):  # Rough heuristic
                    sections.append({
                        'title': self._clean_section_title(line),
                        'duration_minutes': base_duration,
                        'objective': f'Discuss {line.lower()}',
                        'talking_points': ['Main concepts and examples', 'Practical applications', 'Key insights'],
                        'speaker_dynamics': 'Collaborative discussion'
                    })
            
            if sections:
                return sections[:6]  # Limit to 6 sections max
                
        except Exception:
            pass
        
        # Ultimate fallback - generic sections
        base_duration = max(2, total_minutes // 4)
        return [
            {
                'title': 'Introduction and Context',
                'duration_minutes': base_duration,
                'objective': 'Set up the topic and provide context',
                'talking_points': ['Topic introduction', 'Why this matters', 'What we\'ll cover'],
                'speaker_dynamics': 'Host introduces, guest provides perspective'
            },
            {
                'title': 'Core Concepts',
                'duration_minutes': base_duration,
                'objective': 'Explain the main concepts and ideas',
                'talking_points': ['Key definitions', 'Core principles', 'Important examples'],
                'speaker_dynamics': 'Interactive explanation and discussion'
            },
            {
                'title': 'Deep Dive and Applications',
                'duration_minutes': base_duration,
                'objective': 'Explore applications and real-world examples',
                'talking_points': ['Practical applications', 'Case studies', 'Best practices'],
                'speaker_dynamics': 'Detailed discussion with examples'
            },
            {
                'title': 'Insights and Takeaways',
                'duration_minutes': base_duration,
                'objective': 'Summarize key insights and actionable takeaways',
                'talking_points': ['Key lessons learned', 'Actionable advice', 'Future considerations'],
                'speaker_dynamics': 'Synthesis and practical guidance'
            }
        ]
    
    def _normalize_section_durations(self, sections: List[Dict[str, Any]], total_minutes: int) -> None:
        """Adjust section durations to sum to total minutes."""
        if not sections:
            return
            
        total_estimated = sum(s['duration_minutes'] for s in sections)
        if total_estimated > 0:
            for section in sections:
                section['duration_minutes'] = max(1, int((section['duration_minutes'] / total_estimated) * total_minutes))
    
    def _generate_sections_from_outline(self, outline: Dict[str, Any], speakers: List[str], 
                                      natural_style: bool, total_target_words: int) -> List[Dict[str, str]]:
        """Generate detailed script sections based on the dynamic outline with progressive context."""
        sections = outline.get('sections', [])
        if not sections:
            return []
        
        generated_sections = []
        total_duration = sum(section.get('duration_minutes', 1) for section in sections)
        original_prompt = outline.get('original_prompt', '')
        
        # Keep track of context from previous sections
        conversation_context = []
        
        with tqdm(total=len(sections), desc="Writing sections") as pbar:
            for i, section in enumerate(sections):
                # Calculate word target for this section
                section_duration = section.get('duration_minutes', 1)
                section_words = int((section_duration / total_duration) * total_target_words)
                
                # Build context from previous sections
                section_context = self._build_progressive_context(sections, i, conversation_context)
                
                section_script = self._generate_context_aware_section_script(
                    section, speakers, natural_style, section_words, i == 0, i == len(sections) - 1, 
                    original_prompt, section_context
                )
                
                generated_section = {
                    'title': section.get('title', f'Section {i+1}'),
                    'script': section_script,
                    'transition_hint': section.get('transition_hint', ''),
                    'section_info': section  # Keep section info for intelligent transitions
                }
                
                generated_sections.append(generated_section)
                
                # Add this section's context for future sections
                conversation_context.append({
                    'title': section.get('title', f'Section {i+1}'),
                    'objective': section.get('objective', ''),
                    'talking_points': section.get('talking_points', []),
                    'key_decisions': self._extract_key_decisions(section_script)
                })
                
                pbar.update(1)
        
        return generated_sections
    
    def _build_progressive_context(self, all_sections: List[Dict[str, Any]], current_index: int, 
                                 conversation_context: List[Dict[str, Any]]) -> str:
        """Build context about what has been discussed in previous sections."""
        if current_index == 0:
            return "This is the opening section of the conversation."
        
        context_parts = ["This conversation has already covered:"]
        
        # Add context from previous sections
        for i, prev_context in enumerate(conversation_context):
            section_num = i + 1
            context_parts.append(f"Section {section_num} ({prev_context['title']}): {prev_context['objective']}")
            
            # Add key talking points from previous sections
            if prev_context['talking_points']:
                key_points = prev_context['talking_points'][:2]  # First 2 points
                for point in key_points:
                    context_parts.append(f"  - {point}")
        
        # Add what's coming next
        remaining_sections = all_sections[current_index + 1:]
        if remaining_sections:
            context_parts.append("\nUpcoming sections will cover:")
            for section in remaining_sections[:2]:  # Next 2 sections
                context_parts.append(f"  - {section.get('title', 'Next topic')}")
        
        return "\n".join(context_parts)
    
    def _extract_key_decisions(self, section_script: str) -> List[str]:
        """Extract key design decisions or concepts from a section script."""
        # Simple extraction - could be enhanced with more sophisticated NLP
        key_decisions = []
        
        # Look for common decision patterns in technical discussions
        decision_patterns = [
            "we'll use", "we decided", "the approach is", "we chose", 
            "the design uses", "we implement", "the strategy is"
        ]
        
        lines = section_script.split('\n')
        for line in lines:
            line_lower = line.lower()
            for pattern in decision_patterns:
                if pattern in line_lower and len(line) < 200:  # Not too long
                    # Extract the decision part
                    decision_start = line_lower.find(pattern)
                    if decision_start != -1:
                        decision = line[decision_start:decision_start + 100].strip()
                        key_decisions.append(decision)
                        break
        
        return key_decisions[:3]  # Limit to 3 key decisions per section
    
    def _generate_context_aware_section_script(self, section: Dict[str, Any], speakers: List[str], 
                                             natural_style: bool, target_words: int, is_first: bool, 
                                             is_last: bool, original_prompt: str, section_context: str) -> str:
        """Generate script for a specific section with full conversational context."""
        
        # Build context about position in conversation
        position_context = ""
        if is_first:
            position_context = "This is the opening section - include natural introductions and topic setup."
        elif is_last:
            position_context = "This is the closing section - include wrap-up and conclusions. Reference key points from earlier discussion."
        else:
            position_context = "This is a middle section of an ongoing conversation. Build naturally on previous discussion and reference earlier points where relevant."
        
        system_prompt = f"""You are a professional podcast script writer. Write dialogue for this specific section of an ongoing conversation.

ORIGINAL TOPIC: {original_prompt}

CONVERSATION CONTEXT:
{section_context}

CRITICAL CONTEXT:
{position_context}

SECTION DETAILS:
- Title: {section.get('title', 'Section')}
- Objective: {section.get('objective', 'Cover the topic')}
- Target words: {target_words}
- Speakers: {', '.join(speakers)}

DIALOGUE REQUIREMENTS:
- Each line starts with SPEAKER_NAME: followed by dialogue (no asterisks, markdown, or formatting)
- Use ONLY the exact speaker names provided
- Write approximately {target_words} words of dialogue
- Cover all talking points naturally in conversation
- {'Include natural conversation elements like pauses, reactions' if natural_style else 'Keep professional but conversational'}
- Stay focused on the original topic and this section's specific objective
- IMPORTANT: Reference and build upon concepts discussed in previous sections where relevant
- Make connections to earlier discussion to show progression and continuity

FORMAT REQUIREMENTS:
- Use clean format: "SPEAKER: dialogue text"
- Do NOT use markdown formatting like **SPEAKER:** or *SPEAKER:*
- Do NOT include any asterisks, bold formatting, or special characters around speaker names
- Keep it simple and clean for audio processing

CONTINUITY RULES:
- Reference previous sections naturally (e.g., "Building on the requirements we discussed...")
- Don't repeat information already covered - build upon it instead
- Show logical progression from previous decisions
- Use terminology and concepts established in earlier sections
- Make the conversation feel like one continuous, evolving discussion

ANTI-REPETITION RULES:
- Do NOT start with "Welcome back", "Today we're discussing", "Let's talk about"
- Do NOT re-introduce the topic or speakers unnecessarily
- Continue the conversation naturally as part of an ongoing discussion
- Jump straight into the section content while acknowledging previous work

TALKING POINTS TO COVER:
{chr(10).join('- ' + point for point in section.get('talking_points', []))}

SPEAKER DYNAMICS: {section.get('speaker_dynamics', 'Natural back-and-forth conversation')}

Write engaging dialogue that naturally covers these points while building on the previous discussion and maintaining conversational flow."""

        user_prompt = f"""Write {target_words} words of podcast dialogue for this section.

Section focus: {section.get('title', 'Section')}
Objective: {section.get('objective', 'Cover the content')}
Original topic: {original_prompt}

CONTEXT FROM PREVIOUS DISCUSSION:
{section_context}

Key points to cover naturally in conversation:
{chr(10).join('• ' + point for point in section.get('talking_points', []))}

IMPORTANT: This is {'the opening of the conversation' if is_first else 'a continuation of an ongoing conversation about: ' + original_prompt}. 

{'Start with natural introductions and topic setup.' if is_first else 'Build naturally on the previous discussion. Reference earlier points where relevant and show how this section connects to what was already covered.'}

Write substantial dialogue where speakers naturally discuss these points with examples and explanations while maintaining continuity with the overall conversation.

CRITICAL: Use clean format "SPEAKER: text" without any markdown formatting like **SPEAKER:** or *SPEAKER:*"""

        temperature = DEFAULT_TEMPERATURE_NATURAL if natural_style else DEFAULT_TEMPERATURE_PROFESSIONAL
        
        resp = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
        )
        
        generated_script = resp.choices[0].message.content.strip()
        
        # Clean up any markdown formatting that might have slipped through
        cleaned_script = self._clean_script_formatting(generated_script)
        
        return cleaned_script
    
    def _clean_script_formatting(self, script: str) -> str:
        """Clean up script formatting to ensure consistent speaker format."""
        import re
        
        lines = script.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Clean up speaker formatting - remove markdown bold/italic
            # Convert **SPEAKER:** or *SPEAKER:* to SPEAKER:
            line = re.sub(r'^\*+([A-Z][A-Z_\s]+?)\*+:', r'\1:', line)
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _generate_dynamic_section_script(self, section: Dict[str, Any], speakers: List[str], 
                                       natural_style: bool, target_words: int, is_first: bool, is_last: bool, original_prompt: str) -> str:
        """Generate script for a specific section with topic awareness."""
        
        # Build context about position in conversation
        position_context = ""
        if is_first:
            position_context = "This is the opening section - include natural introductions and topic setup."
        elif is_last:
            position_context = "This is the closing section - include wrap-up and conclusions."
        else:
            position_context = "This is a middle section of an ongoing conversation. Continue naturally from where the previous section left off."
        
        system_prompt = f"""You are a professional podcast script writer. Write dialogue for this specific section of an ongoing conversation.

ORIGINAL TOPIC: {original_prompt}

CRITICAL CONTEXT:
{position_context}

SECTION DETAILS:
- Title: {section.get('title', 'Section')}
- Objective: {section.get('objective', 'Cover the topic')}
- Target words: {target_words}
- Speakers: {', '.join(speakers)}

DIALOGUE REQUIREMENTS:
- Each line starts with SPEAKER_NAME: followed by dialogue
- Use ONLY the exact speaker names provided
- Write approximately {target_words} words of dialogue
- Cover all talking points naturally in conversation
- {'Include natural conversation elements like pauses, reactions' if natural_style else 'Keep professional but conversational'}
- Stay focused on the original topic and this section's specific objective
- Build on concepts from earlier in the conversation (if not the first section)

ANTI-REPETITION RULES:
- Do NOT start with "Welcome back", "Today we're discussing", "Let's talk about"
- Do NOT re-introduce the topic or speakers unnecessarily
- Continue the conversation naturally as part of an ongoing discussion
- Jump straight into the section content

TALKING POINTS TO COVER:
{chr(10).join('- ' + point for point in section.get('talking_points', []))}

SPEAKER DYNAMICS: {section.get('speaker_dynamics', 'Natural back-and-forth conversation')}

Write engaging dialogue that naturally covers these points while staying focused on the overall topic."""

        user_prompt = f"""Write {target_words} words of podcast dialogue for this section.

Section focus: {section.get('title', 'Section')}
Objective: {section.get('objective', 'Cover the content')}
Original topic: {original_prompt}

Key points to cover naturally in conversation:
{chr(10).join('• ' + point for point in section.get('talking_points', []))}

IMPORTANT: This is {'the opening of the conversation' if is_first else 'a continuation of an ongoing conversation about: ' + original_prompt}. 

Write substantial dialogue where speakers naturally discuss these points with examples and explanations while staying focused on the original topic."""

        temperature = DEFAULT_TEMPERATURE_NATURAL if natural_style else DEFAULT_TEMPERATURE_PROFESSIONAL
        
        resp = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
        )
        
        return resp.choices[0].message.content.strip()
    
    def _stitch_sections_intelligently(self, sections: List[Dict[str, str]], 
                                     speakers: List[str], natural_style: bool, original_prompt: str) -> str:
        """Stitch sections together with intelligent, topic-aware transitions."""
        if not sections:
            return ""
        
        final_script_parts = []
        
        for i, section in enumerate(sections):
            # Clean up section script
            cleaned_script = self._clean_section_script(section['script'], i == 0)
            final_script_parts.append(cleaned_script)
            
            # Add intelligent transition to next section (except for last section)
            if i < len(sections) - 1:
                transition = self._generate_intelligent_transition(
                    section, sections[i + 1], speakers, natural_style, original_prompt
                )
                if transition:
                    final_script_parts.append(transition)
        
        return '\n\n'.join(final_script_parts)
    
    def _generate_intelligent_transition(self, current_section: Dict[str, str], next_section: Dict[str, str], 
                                       speakers: List[str], natural_style: bool, original_prompt: str) -> str:
        """Generate intelligent transitions using LLM understanding of content flow."""
        
        current_title = current_section.get('title', '')
        next_title = next_section.get('title', '')
        current_info = current_section.get('section_info', {})
        next_info = next_section.get('section_info', {})
        
        # Use LLM to create contextually appropriate transition
        transition_prompt = f"""Create a natural transition between these two podcast sections:

ORIGINAL TOPIC: {original_prompt}
SPEAKERS: {', '.join(speakers)}

CURRENT SECTION: {current_title}
- Objective: {current_info.get('objective', 'Previous discussion')}

NEXT SECTION: {next_title}  
- Objective: {next_info.get('objective', 'Next discussion')}

Create a 1-2 sentence transition that:
- Naturally connects the current topic to the next
- Uses one of the speaker names: {', '.join(speakers)}
- Sounds conversational and logical
- Avoids generic phrases like "let's move on" or "next topic"
- Builds on what was just discussed

Format: SPEAKER_NAME: [transition dialogue]"""

        try:
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Create natural, contextual transitions between conversation sections."},
                    {"role": "user", "content": transition_prompt}
                ],
                temperature=0.7,
                max_tokens=80,
            )
            
            transition = resp.choices[0].message.content.strip()
            
            # Validate the transition has proper format
            if ':' in transition and any(speaker in transition for speaker in speakers):
                return transition
                
        except Exception:
            pass
        
        # Fallback to simple but contextual transition
        speaker = speakers[0] if speakers else "HOST"
        return f"{speaker}: That's really insightful. Building on that, let's explore {next_title.lower()}."
    
    def _clean_section_script(self, script: str, allow_intro_language: bool = False) -> str:
        """Clean up section script to remove unwanted introductory phrases."""
        if allow_intro_language:
            return script  # Keep introduction language for actual introductions
        
        lines = script.split('\n')
        cleaned_lines = []
        
        unwanted_phrases = [
            'welcome back', 'today we\'re', 'in this section', 'let\'s talk about',
            'hello listeners', 'welcome to', 'thanks for joining', 'good morning',
            'good afternoon', 'good evening', 'hello everyone', 'hi everyone',
            'welcome everyone', 'today\'s episode', 'in today\'s', 'this episode'
        ]
        
        for line in lines:
            line_lower = line.lower()
            
            # Skip lines that start with unwanted phrases
            skip_line = False
            for phrase in unwanted_phrases:
                if phrase in line_lower and ':' in line:
                    dialogue_part = line.split(':', 1)[1].strip().lower()
                    if dialogue_part.startswith(phrase):
                        skip_line = True
                        break
            
            if not skip_line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)