"""The swappable authoring boundary.

An `Analyzer` turns SOP text into a canonical package dict that conforms to
contract.SCHEMA. Implementations are interchangeable behind one interface:

  * CachedAnalyzer   — reads the committed JSON. **Deterministic.** This is the
                       default the build uses; the LLM has already run, once.
  * LLMAnalyzer      — calls the Claude API to author the JSON. Non-deterministic
                       (the API no longer even exposes `temperature`). You run it
                       deliberately, review the diff, and commit the result.
  * (your own)       — a fine-tuned small model, a different provider, or a human
                       editing JSON — all fit the same Protocol.

Determinism is achieved by *freezing the Analyzer's output* (the committed JSON),
never by assuming the Analyzer itself is reproducible.
"""
from __future__ import annotations

import json
import os
from typing import Protocol

from . import contract


class Analyzer(Protocol):
    def analyze(self, sop_id: str, sop_text: str = "") -> dict:
        """Return a canonical package dict that validates against contract.SCHEMA."""
        ...


# --------------------------------------------------------------------------
# Deterministic: read the frozen, committed analysis
# --------------------------------------------------------------------------
class CachedAnalyzer:
    """Loads `<json_dir>/<sop_id>.json`. The canonical source of truth."""

    def __init__(self, json_dir: str):
        self.json_dir = json_dir

    def analyze(self, sop_id: str, sop_text: str = "") -> dict:
        path = os.path.join(self.json_dir, f"{sop_id}.json")
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        errors = contract.validate(d)
        if errors:
            raise ValueError(f"{sop_id}.json failed contract validation: {errors[:3]}")
        return d


# --------------------------------------------------------------------------
# Non-deterministic authoring: Claude API (sketch)
# --------------------------------------------------------------------------
SYSTEM = """You are a process-analysis engine for the FlowAgent platform.
Given the full text of a Standard Operating Procedure, produce a single JSON
object that decomposes it into a process model (phases, steps, swimlanes), a
fit-gap analysis against the named reference catalog, and an optimised SOP.
The JSON MUST conform exactly to the provided JSON Schema. Ground every gap and
score in the SOP text; do not invent systems or roles not implied by it.
Respond with ONLY the JSON object — no markdown, no code fences, no commentary."""


def _extract_json(text: str) -> dict:
    """Parse the model's reply as a JSON object, tolerating any stray prose by
    taking the outermost { ... } span."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("model did not return a JSON object")
    return json.loads(text[start:end + 1])


class LLMAnalyzer:
    """Authors the canonical JSON with the Claude API and validates it.

    NOTE ON DETERMINISM: current models (Opus 4.8 / 4.7) do not accept a
    `temperature` parameter at all — sampling determinism is not an available
    lever. Two runs may differ. That is expected: treat the output as a draft,
    review it, and commit it via CachedAnalyzer. Reproducibility comes from the
    committed file, not from this call.
    """

    def __init__(self, model: str = "claude-opus-4-8", max_tokens: int = 32000):
        import anthropic  # imported lazily so the package loads without the SDK
        self.client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
        self.model = model
        self.max_tokens = max_tokens

    def analyze(self, sop_id: str, sop_text: str) -> dict:
        # The canonical schema is too large to compile into a grammar via
        # output_config.format, so we give the model the schema in the prompt
        # and validate the returned JSON against the contract ourselves.
        # Stream because the package JSON is large (avoids HTTP timeouts).
        schema_text = json.dumps(contract.SCHEMA, indent=2)
        user = (
            f"SOP id: {sop_id}\n\n"
            "Produce the canonical JSON conforming exactly to this JSON Schema:\n\n"
            f"=== JSON SCHEMA ===\n{schema_text}\n\n"
            f"=== SOP TEXT ===\n{sop_text}"
        )
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM,
            messages=[{"role": "user", "content": user}],
        ) as stream:
            message = stream.get_final_message()

        if message.stop_reason == "refusal":
            raise RuntimeError(f"{sop_id}: request refused ({message.stop_details})")
        text = next(b.text for b in message.content if b.type == "text")
        d = _extract_json(text)

        errors = contract.validate(d)
        if errors:
            raise ValueError(f"{sop_id}: model output failed contract validation: {errors[:5]}")
        return d
