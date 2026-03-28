"""Verification tests for Career Module V2 — all non-LLM functionality."""
import sys
import os

# Ensure the ml directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_json_utils():
    from src.career.json_utils import safe_llm_json, extract_json_object, extract_json_array

    # Test 1: Simple object
    assert extract_json_object('{"a": 1}') == {"a": 1}
    print("  [✓] Test 1: simple object")

    # Test 2: Nested object (old regex would fail here)
    nested = '{"x": {"y": {"z": 1}}, "a": [1,2,3]}'
    r = extract_json_object(nested)
    assert r == {"x": {"y": {"z": 1}}, "a": [1, 2, 3]}
    print("  [✓] Test 2: nested object")

    # Test 3: Array extraction
    assert extract_json_array("[1, 2, 3]") == [1, 2, 3]
    print("  [✓] Test 3: simple array")

    # Test 4: Array with nested objects (Project Extractor failure case)
    arr_text = 'preamble\n[{"name": "proj1", "tech": ["py", "js"]}, {"name": "proj2", "tech": []}]\nepilogue'
    r = extract_json_array(arr_text)
    assert len(r) == 2
    assert r[0]["name"] == "proj1"
    assert r[0]["tech"] == ["py", "js"]
    print("  [✓] Test 4: array with nested objects (old bug case)")

    # Test 5: Deep nesting (Industry Calibrator failure case)
    deep = '{"industry": "faang", "bullets": [{"original": "did X", "rewritten": "achieved Y", "reasoning": "because Z"}], "keywords": ["a", "b"]}'
    r = extract_json_object(deep)
    assert r["industry"] == "faang"
    assert len(r["bullets"]) == 1
    print("  [✓] Test 5: deep nesting (old bug case)")

    # Test 6: safe_llm_json wrapper
    assert safe_llm_json('{"ok": true}', "object") == {"ok": True}
    assert safe_llm_json("[1,2]", "array") == [1, 2]
    assert safe_llm_json("garbage", "object") is None
    print("  [✓] Test 6: safe_llm_json wrapper")

    # Test 7: JSON with preamble text (typical LLM response)
    llm_response = "Sure! Here is the JSON:\n\n```json\n{\"score\": 85, \"items\": [{\"a\": 1}]}\n```"
    r = extract_json_object(llm_response)
    assert r is not None
    assert r["score"] == 85
    print("  [✓] Test 7: LLM response with preamble")


def test_project_manager():
    from src.career.project_manager import (
        add_project_manual, get_all_projects, clear_projects,
        generate_project_latex,
    )

    clear_projects()

    # Manual entry - success
    r = add_project_manual({"title": "My App", "description": "Does things"})
    assert "error" not in r
    assert r["name"] == "My App"
    assert r["source"] == "manual"
    assert len(get_all_projects()) == 1
    print("  [✓] Test 8: manual project entry")

    # Manual entry - missing fields
    r = add_project_manual({"title": "No desc"})
    assert "error" in r
    print("  [✓] Test 9: missing fields rejected")

    # LaTeX generation
    latex = generate_project_latex([{
        "name": "TestProject",
        "tech_stack": ["Python", "React"],
        "description": "A test project",
        "impact": "Improved speed by 50%",
        "dates": "2025",
        "github_link": "https://github.com/test/repo",
    }])
    assert "\\section{Projects}" in latex
    assert "TestProject" in latex
    assert "Python" in latex
    assert "GitHub" in latex
    print("  [✓] Test 10: LaTeX generation")

    clear_projects()


def test_jd_manager():
    from src.career.jd_manager import add_jd_from_text, list_jds, clear_jds

    clear_jds()
    r = add_jd_from_text(
        "We are looking for a Python developer with 3 years experience.",
        "Test JD",
    )
    assert "error" not in r
    assert r["label"] == "Test JD"
    jds = list_jds()
    assert len(jds) == 1
    assert jds[0]["word_count"] > 0
    print("  [✓] Test 11: JD text storage")

    # Empty text
    r = add_jd_from_text("", "Empty")
    assert "error" in r
    print("  [✓] Test 12: empty JD rejected")

    clear_jds()


def test_cover_letter_tones():
    from src.career.cover_letter import VALID_TONES

    expected = {
        "professional", "enthusiastic", "concise", "storytelling",
        "startup", "faang", "service_based", "product_based", "quant", "custom",
    }
    assert expected == VALID_TONES
    print(f"  [✓] Test 13: {len(VALID_TONES)} cover letter tones")


def test_roadmap_mermaid():
    from src.career.roadmap_builder import _generate_mermaid

    roadmap = {
        "sections": [
            {
                "phase": "Foundation",
                "duration_weeks": 4,
                "topics": ["Python Basics", "Data Structures"],
                "projects": ["Build a CLI tool"],
                "milestones": ["Can write Python scripts"],
            },
            {
                "phase": "Intermediate",
                "duration_weeks": 6,
                "topics": ["Web Frameworks", "APIs"],
                "projects": ["Build a REST API"],
                "milestones": ["Can build web services"],
            },
        ]
    }
    mermaid = _generate_mermaid(roadmap)
    assert "flowchart TD" in mermaid
    assert "Foundation" in mermaid
    assert "mustLearn" in mermaid
    assert "shouldLearn" in mermaid or "niceToKnow" in mermaid
    print("  [✓] Test 14: Mermaid flowchart generation")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  Career Module V2 — Verification Tests")
    print("=" * 50 + "\n")

    test_json_utils()
    test_project_manager()
    test_jd_manager()
    test_cover_letter_tones()
    test_roadmap_mermaid()

    print("\n" + "=" * 50)
    print("  ALL 14 TESTS PASSED ✓")
    print("=" * 50)
