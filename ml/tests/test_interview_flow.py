"""Unit tests for SessionState and PromptManager — no heavy deps needed."""
import importlib.util
import os
import sys

ML_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, ML_DIR)

def _load_module(name, filepath):
    """Import a single .py file without triggering __init__.py cascades."""
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# Load SessionState (no external deps)
ss_mod = _load_module(
    'src.core.session_state',
    os.path.join(ML_DIR, 'src', 'core', 'session_state.py'),
)
SessionState = ss_mod.SessionState

# Load PromptManager (only needs `re`)
pm_mod = _load_module(
    'src.brain.prompt_manager',
    os.path.join(ML_DIR, 'src', 'brain', 'prompt_manager.py'),
)
PromptManager = pm_mod.PromptManager

# ── SessionState tests ───────────────────────────────────────────
s = SessionState()
assert s.interview_mode == "generic"
assert s.interview_type == "technical"
print("1. PASS: defaults")

s2 = SessionState(difficulty="Hard", interview_mode="curated", interview_type="behavioral")
assert s2.interview_mode == "curated"
assert s2.interview_type == "behavioral"
assert s2.difficulty == "Hard"
print("2. PASS: explicit values")

# Validation is via update_*() methods, not constructor
assert s.update_mode("bogus") == False  # rejects invalid
assert s.interview_mode == "generic"    # stays unchanged
assert s.update_mode("curated") == True
assert s.interview_mode == "curated"
print("3. PASS: update_mode validation")

assert s.update_interview_type("xyz") == False
assert s.interview_type == "technical"
assert s.update_interview_type("hr") == True
assert s.interview_type == "hr"
print("4. PASS: update_interview_type validation")

d = s2.to_dict()
assert d["interview_mode"] == "curated"
assert d["interview_type"] == "behavioral"
assert "elapsed_seconds" in d
print("5. PASS: to_dict")

# ── PromptManager tests ─────────────────────────────────────────
personas = {}
for itype in ["technical", "behavioral", "hr", "combined"]:
    pm = PromptManager(resume_text="Built a data pipeline in Python", interview_type=itype)
    assert pm.interview_type == itype
    personas[itype] = pm.system_persona
    opening = pm.get_opening_prompt("Medium")
    assert len(opening) > 20
    print(f"6. PASS: {itype} persona ({len(pm.system_persona)} chars)")

assert personas["technical"] != personas["behavioral"]
assert personas["hr"] != personas["combined"]
print("7. PASS: all 4 personas are distinct")

pm_hr = PromptManager(interview_type="hr")
opening_hr = pm_hr.get_opening_prompt()
assert "career" in opening_hr.lower() or "motivation" in opening_hr.lower()
print("8. PASS: HR opening prompt contents")

pm_beh = PromptManager(resume_text="Led a team of 5 engineers", interview_type="behavioral")
opening_beh = pm_beh.get_opening_prompt()
assert "star" in opening_beh.lower() or "behavioral" in opening_beh.lower()
print("9. PASS: behavioral opening with resume")

print("\n=== ALL TESTS PASSED ===")
