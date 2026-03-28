"""Feature 4: Learning Roadmap Builder with Mermaid Flowchart.

Generates a structured learning roadmap for any career topic, with in-memory
caching and Mermaid flowchart code for frontend rendering.
"""
import json
import logging

from src.career.json_utils import career_llm_call, safe_llm_json

logger = logging.getLogger("RoadmapBuilder")

# In-memory cache keyed by normalized topic
_roadmap_cache: dict[str, dict] = {}


def _normalize_topic(topic: str) -> str:
    """Normalize topic for cache key: lowercase, strip, collapse whitespace."""
    return " ".join(topic.lower().strip().split())


def _generate_mermaid(roadmap: dict) -> str:
    """Convert a roadmap JSON into Mermaid flowchart code with color-coded nodes.

    Color coding:
      - 🟩 green  = Must Learn (high priority)
      - 🟨 yellow = Should Learn (medium priority)
      - ⬜ gray   = Nice to Know (low priority)
      - 🟦 blue   = Already Known / Prerequisite
    """
    lines = [
        "flowchart TD",
        "",
        "  %% Style definitions",
        "  classDef mustLearn fill:#22c55e,stroke:#16a34a,color:#fff,stroke-width:2px",
        "  classDef shouldLearn fill:#eab308,stroke:#ca8a04,color:#fff,stroke-width:2px",
        "  classDef niceToKnow fill:#6b7280,stroke:#4b5563,color:#fff,stroke-width:1px",
        "  classDef alreadyKnown fill:#3b82f6,stroke:#2563eb,color:#fff,stroke-width:2px",
        "  classDef prerequisite fill:#1e293b,stroke:#334155,color:#94a3b8,stroke-width:1px",
        "",
    ]

    sections = roadmap.get("sections", [])
    if not sections:
        return ""

    prev_node = None

    for i, section in enumerate(sections):
        phase = section.get("phase", f"Phase {i + 1}")
        duration = section.get("duration_weeks", "?")
        topics = section.get("topics", [])
        milestones = section.get("milestones", [])
        projects = section.get("projects", [])

        # Sanitize node ID
        node_id = f"P{i}"
        # Escape special chars for Mermaid labels
        phase_safe = phase.replace('"', "'")

        # Build rich label
        label_parts = [
            f"<b>📌 {phase_safe}</b>",
            f"⏱️ {duration} weeks",
        ]
        if topics:
            topics_str = ", ".join(topics[:5])
            label_parts.append(f"📚 {topics_str}")
        if milestones:
            ms = milestones[0] if milestones else ""
            label_parts.append(f"🎯 {ms}")

        label = "<br/>".join(label_parts)
        lines.append(f'  {node_id}["{label}"]')

        # Determine style class based on position (first phases = must learn)
        if i < len(sections) * 0.4:
            lines.append(f"  class {node_id} mustLearn")
        elif i < len(sections) * 0.7:
            lines.append(f"  class {node_id} shouldLearn")
        else:
            lines.append(f"  class {node_id} niceToKnow")

        # Add project sub-nodes
        for j, proj in enumerate(projects[:2]):
            proj_id = f"P{i}_proj{j}"
            proj_safe = proj.replace('"', "'")[:60]
            lines.append(f'  {proj_id}("{proj_safe}")')
            lines.append(f"  {node_id} -.-> {proj_id}")
            lines.append(f"  class {proj_id} prerequisite")

        # Connect to previous phase
        if prev_node is not None:
            lines.append(f"  {prev_node} --> {node_id}")

        prev_node = node_id
        lines.append("")

    # Add legend
    lines.extend([
        "  %% Legend",
        '  L1["🟩 Must Learn"]',
        "  class L1 mustLearn",
        '  L2["🟨 Should Learn"]',
        "  class L2 shouldLearn",
        '  L3["⬜ Nice to Know"]',
        "  class L3 niceToKnow",
        '  L4["🟦 Already Known"]',
        "  class L4 alreadyKnown",
        '  L5["⬛ Prerequisite"]',
        "  class L5 prerequisite",
    ])

    return "\n".join(lines)


def build_roadmap(llm, topic: str, context: str = "") -> dict:
    """Generate a learning roadmap for a career topic via LLM.

    Uses an in-memory cache to avoid redundant LLM calls for the same topic.
    Returns both the structured JSON and Mermaid flowchart code.

    Args:
        llm: A llama_cpp.Llama model instance.
        topic: The career/skill topic to build a roadmap for.
        context: Optional context (e.g., current skill level, time constraints).

    Returns:
        dict with sections, certifications, career_progression,
        estimated_months, and mermaid_code.
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
      "milestones": ["what you should be able to do"],
      "resources": [
        {{
          "name": "<resource name>",
          "type": "<course|doc|tutorial|video|book>",
          "difficulty": "<beginner|intermediate|advanced>"
        }}
      ]
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
        text = career_llm_call(llm, prompt, max_tokens=2000, temperature=0.4)
        result = safe_llm_json(text, expect="object")
        if result is not None:
            # Generate Mermaid flowchart code
            result["mermaid_code"] = _generate_mermaid(result)
            _roadmap_cache[cache_key] = result
            return result
    except Exception as e:
        logger.error(f"Roadmap generation failed: {e}")

    return {"error": "Failed to generate roadmap"}


def clear_roadmap_cache() -> None:
    """Clear the in-memory roadmap cache."""
    _roadmap_cache.clear()
