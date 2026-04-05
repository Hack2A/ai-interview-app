"""Feature 4: Learning Roadmap Builder with detailed hierarchical Mermaid Flowchart.

Generates a deeply structured learning roadmap for any career topic, with
in-memory caching and a large tree-style Mermaid flowchart for frontend rendering.
The output mirrors comprehensive roadmaps (like roadmap.sh) with many branches,
sub-topics, and sub-sub-topics.
"""
import json
import logging
import re

from src.career.json_utils import career_llm_call, safe_llm_json

logger = logging.getLogger("RoadmapBuilder")

# In-memory cache keyed by normalized topic
_roadmap_cache: dict[str, dict] = {}


def _normalize_topic(topic: str) -> str:
    """Normalize topic for cache key: lowercase, strip, collapse whitespace."""
    return " ".join(topic.lower().strip().split())


def _safe_id(text: str, prefix: str = "N") -> str:
    """Generate a safe Mermaid node ID from text."""
    clean = re.sub(r"[^a-zA-Z0-9]", "", text)[:20]
    return f"{prefix}_{clean}" if clean else f"{prefix}_x"


def _escape_label(text: str) -> str:
    """Escape special characters for Mermaid labels."""
    return text.replace('"', "'").replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")")


def _generate_mermaid(roadmap: dict) -> str:
    """Convert a hierarchical roadmap JSON into a large tree-style Mermaid flowchart.

    Produces a detailed, branching diagram similar to roadmap.sh style:
    - Root topic at top
    - Main branches for each category/phase
    - Sub-branches for each topic
    - Leaf nodes for sub-topics
    - Color coded by priority/depth

    Color coding:
      - 🟧 orange  = Root / Title
      - 🟩 green   = Must Learn (core/foundation)
      - 🟨 yellow  = Should Learn (intermediate)
      - ⬜ gray    = Nice to Know (advanced/optional)
      - 🟦 blue    = Practical (projects/tools)
      - 🟪 purple  = Career milestone
    """
    lines = [
        "flowchart TD",
        "",
        "  %% Style definitions",
        "  classDef rootNode fill:#f97316,stroke:#ea580c,color:#fff,stroke-width:3px,font-size:16px",
        "  classDef coreNode fill:#22c55e,stroke:#16a34a,color:#fff,stroke-width:2px",
        "  classDef midNode fill:#eab308,stroke:#ca8a04,color:#fff,stroke-width:2px",
        "  classDef advNode fill:#6b7280,stroke:#4b5563,color:#fff,stroke-width:1px",
        "  classDef practicalNode fill:#3b82f6,stroke:#2563eb,color:#fff,stroke-width:2px",
        "  classDef careerNode fill:#a855f7,stroke:#7c3aed,color:#fff,stroke-width:2px",
        "  classDef prereqNode fill:#1e293b,stroke:#334155,color:#94a3b8,stroke-width:1px",
        "",
    ]

    topic = _escape_label(roadmap.get("topic", "Roadmap"))
    node_ids = set()  # Track used IDs to avoid duplicates

    def unique_id(base: str) -> str:
        """Ensure unique node ID."""
        candidate = base
        counter = 1
        while candidate in node_ids:
            candidate = f"{base}{counter}"
            counter += 1
        node_ids.add(candidate)
        return candidate

    # ── Root node ──
    root_id = unique_id("ROOT")
    lines.append(f'  {root_id}["{topic}"]')
    lines.append(f"  class {root_id} rootNode")
    lines.append("")

    # ── Prerequisites section ──
    prereqs = roadmap.get("prerequisites", [])
    if prereqs:
        prereq_hdr = unique_id("PREREQ")
        lines.append(f'  {prereq_hdr}["Prerequisites"]')
        lines.append(f"  class {prereq_hdr} prereqNode")
        lines.append(f"  {root_id} --> {prereq_hdr}")
        for k, pr in enumerate(prereqs):
            pr_label = _escape_label(str(pr))
            pr_id = unique_id(f"pr{k}")
            lines.append(f'  {pr_id}["{pr_label}"]')
            lines.append(f"  class {pr_id} prereqNode")
            lines.append(f"  {prereq_hdr} --> {pr_id}")
        lines.append("")

    # ── Main sections (vertical chain) ──
    sections = roadmap.get("sections", [])
    prev_section = root_id  # Chain: root → S0 → S1 → S2 ...

    for i, section in enumerate(sections):
        phase_name = _escape_label(section.get("phase", f"Phase {i + 1}"))
        duration = section.get("duration_weeks", "?")

        # Section header node
        sec_id = unique_id(f"S{i}")
        lines.append(f'  {sec_id}["{phase_name}<br/>⏱️ {duration} weeks"]')

        # Color code: first 40% = core (green), next 30% = mid (yellow), rest = advanced (gray)
        if i < len(sections) * 0.4:
            lines.append(f"  class {sec_id} coreNode")
        elif i < len(sections) * 0.7:
            lines.append(f"  class {sec_id} midNode")
        else:
            lines.append(f"  class {sec_id} advNode")

        # Connect to previous section (vertical chain)
        lines.append(f"  {prev_section} --> {sec_id}")
        prev_section = sec_id

        # ── Topics as sub-branches ──
        topics = section.get("topics", [])
        for j, topic_item in enumerate(topics):
            if isinstance(topic_item, dict):
                # Rich topic with sub-topics
                t_name = _escape_label(topic_item.get("name", f"Topic {j + 1}"))
                t_id = unique_id(f"S{i}T{j}")
                lines.append(f'  {t_id}["{t_name}"]')

                if i < len(sections) * 0.4:
                    lines.append(f"  class {t_id} coreNode")
                elif i < len(sections) * 0.7:
                    lines.append(f"  class {t_id} midNode")
                else:
                    lines.append(f"  class {t_id} advNode")

                lines.append(f"  {sec_id} --> {t_id}")

                # Sub-topics as leaf nodes
                sub_topics = topic_item.get("sub_topics", [])
                for m, st in enumerate(sub_topics):
                    st_label = _escape_label(str(st))
                    st_id = unique_id(f"S{i}T{j}st{m}")
                    lines.append(f'  {st_id}["{st_label}"]')
                    lines.append(f"  class {st_id} advNode")
                    lines.append(f"  {t_id} --> {st_id}")
            else:
                # Simple string topic
                t_name = _escape_label(str(topic_item))
                t_id = unique_id(f"S{i}T{j}")
                lines.append(f'  {t_id}["{t_name}"]')

                if i < len(sections) * 0.4:
                    lines.append(f"  class {t_id} coreNode")
                elif i < len(sections) * 0.7:
                    lines.append(f"  class {t_id} midNode")
                else:
                    lines.append(f"  class {t_id} advNode")

                lines.append(f"  {sec_id} --> {t_id}")

        # ── Projects as practical sub-nodes ──
        projects = section.get("projects", [])
        for j, proj in enumerate(projects):
            proj_label = _escape_label(str(proj))[:60]
            proj_id = unique_id(f"S{i}Pr{j}")
            lines.append(f'  {proj_id}("{proj_label}")')
            lines.append(f"  class {proj_id} practicalNode")
            lines.append(f"  {sec_id} -.-> {proj_id}")

        # ── Milestones as diamond nodes ──
        milestones = section.get("milestones", [])
        for j, ms in enumerate(milestones[:2]):
            ms_label = _escape_label(str(ms))[:50]
            ms_id = unique_id(f"S{i}M{j}")
            lines.append(f'  {ms_id}{{{{{ms_label}}}}}')
            lines.append(f"  class {ms_id} careerNode")
            lines.append(f"  {sec_id} -.-> {ms_id}")

        lines.append("")

    # ── Certifications branch ──
    certs = roadmap.get("certifications", [])
    if certs:
        cert_hdr = unique_id("CERTS")
        lines.append(f'  {cert_hdr}["🎓 Certifications"]')
        lines.append(f"  class {cert_hdr} careerNode")
        lines.append(f"  {prev_section} --> {cert_hdr}")
        for k, cert in enumerate(certs):
            if isinstance(cert, dict):
                c_name = _escape_label(cert.get("name", f"Cert {k + 1}"))
                c_prov = _escape_label(cert.get("provider", ""))
                c_label = f"{c_name}<br/>{c_prov}" if c_prov else c_name
            else:
                c_label = _escape_label(str(cert))
            c_id = unique_id(f"C{k}")
            lines.append(f'  {c_id}["{c_label}"]')
            lines.append(f"  class {c_id} careerNode")
            lines.append(f"  {cert_hdr} --> {c_id}")
        lines.append("")

    # ── Career Progression branch ──
    career = roadmap.get("career_progression", [])
    if career:
        career_hdr = unique_id("CAREER")
        lines.append(f'  {career_hdr}["💼 Career Path"]')
        lines.append(f"  class {career_hdr} careerNode")
        lines.append(f"  {prev_section} --> {career_hdr}")
        prev_career = career_hdr
        for k, role in enumerate(career):
            if isinstance(role, dict):
                r_title = _escape_label(role.get("role", f"Role {k + 1}"))
                r_exp = role.get("experience_needed", "")
                r_sal = role.get("salary_range", "")
                parts = [r_title]
                if r_exp:
                    parts.append(f"📅 {_escape_label(str(r_exp))}")
                if r_sal:
                    parts.append(f"💰 {_escape_label(str(r_sal))}")
                r_label = "<br/>".join(parts)
            else:
                r_label = _escape_label(str(role))
            r_id = unique_id(f"CR{k}")
            lines.append(f'  {r_id}["{r_label}"]')
            lines.append(f"  class {r_id} careerNode")
            lines.append(f"  {prev_career} --> {r_id}")
            prev_career = r_id
        lines.append("")

    # ── Legend ──
    lines.extend([
        "  %% Legend",
        '  L1["🟩 Core / Must Learn"]',
        "  class L1 coreNode",
        '  L2["🟨 Should Learn"]',
        "  class L2 midNode",
        '  L3["⬜ Advanced / Optional"]',
        "  class L3 advNode",
        '  L4["🟦 Practical / Projects"]',
        "  class L4 practicalNode",
        '  L5["🟪 Career / Certs"]',
        "  class L5 careerNode",
    ])

    return "\n".join(lines)


def build_roadmap(llm, topic: str, context: str = "") -> dict:
    """Generate a detailed, hierarchical learning roadmap for a career topic via LLM.

    The prompt requests a deeply structured roadmap with 6-10 sections, each containing
    rich topic objects with sub-topics, multiple projects, milestones, and resources.
    This mirrors comprehensive roadmaps like roadmap.sh.

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

    prompt = f"""You are a world-class career learning architect. Create an EXTREMELY DETAILED and COMPREHENSIVE learning roadmap for mastering this topic from absolute beginner to expert level.

TOPIC: {topic}
{context_line}

IMPORTANT: Make this roadmap as DETAILED and LARGE as possible. Include:
- 6 to 10 major sections/phases covering the FULL learning journey
- Each section must have 4 to 8 topics, and each topic must have 2 to 5 sub_topics
- Each section must have 2 to 4 hands-on projects
- Each section must have 1 to 3 milestones
- Include prerequisites the learner should know first
- Include 3 to 6 relevant certifications
- Include 4 to 6 career progression roles from entry to senior

Respond ONLY with valid JSON:
{{
  "topic": "{topic}",
  "prerequisites": ["prereq1", "prereq2", "prereq3"],
  "sections": [
    {{
      "phase": "<Phase name, e.g. Mathematical Foundations>",
      "duration_weeks": <number>,
      "topics": [
        {{
          "name": "<topic name, e.g. Linear Algebra>",
          "sub_topics": ["sub1", "sub2", "sub3"]
        }}
      ],
      "projects": ["project1", "project2"],
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
        text = career_llm_call(llm, prompt, max_tokens=4000, temperature=0.4)
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
