"""Shared JSON extraction utilities for career LLM modules.

Uses brace-counting to correctly handle deeply nested JSON from LLM
responses.  When the LLM output is truncated (common with low max_tokens),
the repair helpers attempt to close open braces/brackets so parsing can
still succeed with a partial but valid result.
"""
import json
import logging
import re

logger = logging.getLogger("JSONUtils")


# ── Shared LLM call helper ──────────────────────────────────────
# Llama 3 Instruct models need create_chat_completion() with the
# proper chat template.  Every career module was using raw
# create_completion() which the instruct model ignores → empty text.

def career_llm_call(llm, prompt: str, *,
                    max_tokens: int = 1500,
                    temperature: float = 0.3) -> str:
    """Call the LLM using chat completion format and return the raw text.

    Converts a single prompt string into a system+user message pair
    for Llama 3 Instruct chat template.

    Returns:
        The raw text from the LLM response (may be empty on failure).
    """
    response = llm.create_chat_completion(
        messages=[
            {"role": "system",
             "content": "You are a helpful career assistant. Always respond ONLY with valid JSON. No explanations, no markdown, no extra text — just the JSON object or array."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    text = response["choices"][0]["message"]["content"] or ""
    logger.debug(f"career_llm_call raw output ({len(text)} chars): {text[:200]}...")
    return text.strip()


def _find_balanced(text: str, open_char: str, close_char: str) -> str | None:
    """Find the first balanced block delimited by open_char/close_char.

    Uses a simple brace-counting approach that handles arbitrary nesting depth,
    unlike the single-level regex previously used.
    """
    start = text.find(open_char)
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i in range(start, len(text)):
        ch = text[i]

        if escape_next:
            escape_next = False
            continue

        if ch == "\\":
            escape_next = True
            continue

        if ch == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if ch == open_char:
            depth += 1
        elif ch == close_char:
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


def _repair_truncated_json(text: str) -> str | None:
    """Attempt to repair truncated JSON by closing open braces/brackets.

    When LLM output is cut off mid-JSON, this tries to produce a valid
    (partial) JSON string by:
    1. Finding the first { or [
    2. Tracking open braces/brackets
    3. Closing any unclosed string literals
    4. Closing open containers in reverse order
    """
    # Find start of JSON
    obj_start = text.find("{")
    arr_start = text.find("[")

    if obj_start == -1 and arr_start == -1:
        return None

    if obj_start == -1:
        start = arr_start
    elif arr_start == -1:
        start = obj_start
    else:
        start = min(obj_start, arr_start)

    fragment = text[start:]

    # Track open containers
    stack = []
    in_string = False
    escape_next = False
    last_good = len(fragment)  # end position

    for i, ch in enumerate(fragment):
        if escape_next:
            escape_next = False
            continue

        if ch == "\\":
            escape_next = True
            continue

        if ch == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if ch in ("{", "["):
            stack.append(ch)
        elif ch == "}" and stack and stack[-1] == "{":
            stack.pop()
            last_good = i + 1
        elif ch == "]" and stack and stack[-1] == "[":
            stack.pop()
            last_good = i + 1

    if not stack:
        # Already balanced — shouldn't reach here but fallback
        return fragment[:last_good] if last_good < len(fragment) else fragment

    # Try to close the truncated JSON
    repaired = fragment.rstrip()

    # If we're in the middle of a string, close it
    # Count unescaped quotes
    quote_count = 0
    esc = False
    for ch in repaired:
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            quote_count += 1
    if quote_count % 2 != 0:
        repaired += '"'

    # Remove trailing comma (invalid JSON)
    repaired = repaired.rstrip()
    if repaired.endswith(","):
        repaired = repaired[:-1]

    # Close open containers in reverse order
    for opener in reversed(stack):
        if opener == "{":
            repaired += "}"
        elif opener == "[":
            repaired += "]"

    return repaired


def extract_json_object(text: str) -> dict | None:
    """Extract the first valid JSON object {...} from raw LLM text."""
    # Try balanced extraction first
    raw = _find_balanced(text, "{", "}")
    if raw is not None:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning(f"JSON object decode failed: {exc}")

    # Fallback: try to repair truncated JSON
    logger.info("Attempting truncated JSON repair for object...")
    repaired = _repair_truncated_json(text)
    if repaired is not None:
        try:
            result = json.loads(repaired)
            if isinstance(result, dict):
                logger.info("Truncated JSON repair succeeded (object)")
                return result
        except json.JSONDecodeError:
            logger.warning("Truncated JSON repair failed for object")

    return None


def extract_json_array(text: str) -> list | None:
    """Extract the first valid JSON array [...] from raw LLM text."""
    raw = _find_balanced(text, "[", "]")
    if raw is not None:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning(f"JSON array decode failed: {exc}")

    # Fallback: try to repair truncated JSON
    logger.info("Attempting truncated JSON repair for array...")
    repaired = _repair_truncated_json(text)
    if repaired is not None:
        try:
            result = json.loads(repaired)
            if isinstance(result, list):
                logger.info("Truncated JSON repair succeeded (array)")
                return result
        except json.JSONDecodeError:
            logger.warning("Truncated JSON repair failed for array")

    return None


def safe_llm_json(text: str, expect: str = "object"):
    """Extract JSON from LLM output, returning the expected type or None.

    Args:
        text: Raw LLM completion text.
        expect: "object" for dict, "array" for list.

    Returns:
        Parsed dict/list on success, None on failure.
    """
    if not text or not text.strip():
        logger.warning("safe_llm_json received empty text")
        return None

    if expect == "array":
        return extract_json_array(text)
    return extract_json_object(text)
