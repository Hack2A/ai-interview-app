"""Feature 4: Learning Roadmap Builder.

Generates a structured learning roadmap for any career topic, with in-memory caching.
"""
import json
import logging
import re

logger = logging.getLogger("RoadmapBuilder")

# In-memory cache keyed by normalized topic
_roadmap_cache: dict[str, dict] = {}


def _normalize_topic(topic: str) -> str:
    """Normalize topic for cache key: lowercase, strip, collapse whitespace."""
    return " ".join(topic.lower().strip().split())


def build_roadmap(llm, topic: str, context: str = "") -> dict:
    """Generate a learning roadmap for a career topic via LLM.

    Uses an in-memory cache to avoid redundant LLM calls for the same topic.

    Args:
        llm: A llama_cpp.Llama model instance.
        topic: The career/skill topic to build a roadmap for.
        context: Optional context (e.g., current skill level, time constraints).

    Returns:
        dict with sections, certifications, career_progression, estimated_months.
    """
    cache_key = _normalize_topic(topic)
    if cache_key in _roadmap_cache:
        logger.info(f"Roadmap cache hit for: {cache_key}")
        return _roadmap_cache[cache_key]

    context_line = f"\nAdditional context: {context}" if context else ""

    prompt = f"""You are a career learning architect. Create a detailed learning roadmap for mastering this topic.

TOPIC: {topic}
{context_line}

Respond ONLY with valid JSON:
{{
  "topic": "{topic}",
  "sections": [
    {{
      "phase": "<Phase name, e.g. Foundation>",
      "duration_weeks": <number>,
      "topics": ["topic1", "topic2"],
      "projects": ["hands-on project idea"],
      "milestones": ["what you should be able to do"]
    }}
  ],
  "certifications": [
    {{
      "name": "<certification name>",
      "provider": "<provider>",
      "difficulty": "<beginner|intermediate|advanced>",
      "estimated_cost": "<free|$X>"
    }}
  ],
  "career_progression": [
    {{
      "role": "<job title>",
      "experience_needed": "<X years>",
      "salary_range": "<$X-$Y>"
    }}
  ],
  "estimated_months": <total number>
}}"""

    try:
        response = llm.create_completion(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.4,
            stop=["</s>", "USER:", "ASSISTANT:"],
        )
        text = response["choices"][0]["text"].strip()
        match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if match:
            result = json.loads(match.group())
            _roadmap_cache[cache_key] = result
            return result
    except Exception as e:
        logger.error(f"Roadmap generation failed: {e}")

    return {"error": "Failed to generate roadmap"}


def clear_roadmap_cache() -> None:
    """Clear the in-memory roadmap cache."""
    _roadmap_cache.clear()
