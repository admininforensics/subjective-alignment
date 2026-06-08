"""LLM narrative generation: OpenAI API, local Ollama, or template fallback."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

PROVIDER_OPENAI = "openai"
PROVIDER_OLLAMA = "ollama"
PROVIDER_TEMPLATE = "template"


def _report_llm_provider() -> str:
    explicit = os.environ.get("REPORT_LLM_PROVIDER", "").strip().lower()
    if explicit in {PROVIDER_OPENAI, PROVIDER_OLLAMA, PROVIDER_TEMPLATE}:
        return explicit
    if os.environ.get("OPENAI_API_KEY"):
        return PROVIDER_OPENAI
    return PROVIDER_OLLAMA


def _call_openai(*, system_prompt: str, user_prompt: str) -> str | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "temperature": 0.4,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"].strip()
    except (urllib.error.URLError, KeyError, json.JSONDecodeError, TimeoutError) as exc:
        logger.warning("OpenAI request failed: %s", exc)
        return None


def _call_ollama(*, system_prompt: str, user_prompt: str) -> str | None:
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    model = os.environ.get("OLLAMA_MODEL", "mistral:latest")
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"temperature": 0.4},
    }
    request = urllib.request.Request(
        f"{base_url}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = body.get("message", {}).get("content", "").strip()
        return content or None
    except (urllib.error.URLError, KeyError, json.JSONDecodeError, TimeoutError) as exc:
        logger.warning("Ollama request failed: %s", exc)
        return None


def _call_llm(*, system_prompt: str, user_prompt: str) -> tuple[str | None, str]:
    provider = _report_llm_provider()

    if provider == PROVIDER_OPENAI:
        text = _call_openai(system_prompt=system_prompt, user_prompt=user_prompt)
        if text:
            return text, PROVIDER_OPENAI
        text = _call_ollama(system_prompt=system_prompt, user_prompt=user_prompt)
        if text:
            return text, PROVIDER_OLLAMA
        return None, PROVIDER_TEMPLATE

    if provider == PROVIDER_OLLAMA:
        text = _call_ollama(system_prompt=system_prompt, user_prompt=user_prompt)
        if text:
            return text, PROVIDER_OLLAMA
        return None, PROVIDER_TEMPLATE

    return None, PROVIDER_TEMPLATE


def _template_overall_snapshot(variables: dict) -> str:
    state = variables["overall_system_state"]
    primary = variables["primary_domain"]
    secondary = variables.get("secondary_domain")
    theme = variables["interaction_theme"]

    if state == "Stable":
        return (
            "Your assessment suggests a broadly balanced and well-aligned professional system. "
            "Although some areas of pressure and adaptation are present, these remain within "
            "manageable ranges and do not appear to be generating significant friction. "
            "Overall, your results indicate that your current role, environment, and personal "
            "drivers are working together relatively effectively."
        )

    secondary_clause = (
        f" and {secondary.lower()}" if secondary and secondary != primary else ""
    )
    if state == "Emerging Strain":
        return (
            f"Your results suggest a generally functional professional system, although emerging "
            f"areas of strain may warrant attention around {primary.lower()}{secondary_clause}. "
            f"{theme}. "
            "While these pressures are not currently severe, they may contribute to fatigue, "
            "frustration, or reduced engagement if maintained over extended periods."
        )

    if state == "Meaningful Strain":
        return (
            f"Your assessment indicates a meaningful level of strain within your current "
            f"professional system, with the strongest pressures emerging around "
            f"{primary.lower()}{secondary_clause}. "
            f"This suggests that {theme.lower()}. "
            "While other areas remain relatively stable, the concentration of pressure within "
            "these domains indicates a pattern that may become more difficult to sustain if "
            "left unaddressed."
        )

    return (
        f"Your assessment indicates significant misalignment within your current professional "
        f"system, with pronounced strain around {primary.lower()}{secondary_clause}. "
        f"{theme}. "
        "This pattern suggests that sustaining the current environment may require ongoing "
        "adaptation that is becoming increasingly costly in terms of energy, engagement, "
        "and personal fit."
    )


def _template_what_results_suggest(section5_context: dict) -> str:
    domains = section5_context.get("elevated_domains", [])
    if not domains:
        return (
            "Your results suggest a broadly stable professional system with no dominant pattern "
            "of strain at this time. "
            "This does not mean pressure is absent, but that the main dimensions of alignment "
            "appear to be functioning within manageable ranges. "
            "Continued attention to energy, fit, and influence will help maintain this balance."
        )

    primary = domains[0]
    secondary = domains[1] if len(domains) > 1 else None
    themes = ", ".join(primary.get("key_themes", [])[:3]) or "sustained adaptation"
    subdomains = ", ".join(primary.get("major_contributors", [])) or "your current environment"
    interaction = section5_context.get("interaction_themes", ["Several pressures are interacting"])[0]

    secondary_text = ""
    if secondary:
        secondary_text = (
            f" The combination with elevated {secondary['domain'].lower()} suggests that "
            f"{interaction.lower()}."
        )

    return (
        f"The pattern identified in your results appears to be driven less by capability or "
        f"commitment, and more by the relationship between your natural way of operating and "
        f"the environment in which you are working. Responses associated with elevated "
        f"{primary['domain'].lower()} point toward experiences within {subdomains}, including "
        f"themes such as {themes.lower()}.{secondary_text}\n\n"
        f"At the same time, the profile suggests that energy may be consumed not only by the "
        f"demands of the work itself, but also by the process of continually managing how you "
        f"present, communicate, or function within the environment. This can create a situation "
        f"where professional performance remains outwardly intact while the personal cost of "
        f"maintaining that performance gradually increases.\n\n"
        f"Taken together, these results suggest that the central challenge may not be one of "
        f"performance, motivation, or competence. Rather, it points toward a system in which "
        f"the ongoing effort required to fit, adapt, or sustain expectations may be consuming "
        f"resources that would otherwise be available for engagement, creativity, resilience, "
        f"and long-term growth."
    )


def generate_overall_snapshot(variables: dict) -> tuple[str, str]:
    system_prompt = (
        "You write professional alignment assessment summaries for working adults. "
        "Use plain, insightful language. Never diagnose. Never mention scores, numbers, or bullet points. "
        "Return exactly 3 sentences as a single paragraph with no numbering or labels."
    )
    user_prompt = (
        "Write Section 2 (Overall Alignment Snapshot) for a Subjective Alignment report.\n\n"
        f"Overall system state: {variables['overall_system_state']}\n"
        f"Primary domain: {variables['primary_domain']}\n"
        f"Secondary domain: {variables.get('secondary_domain') or 'None'}\n"
        f"Interaction theme: {variables['interaction_theme']}\n"
        f"Tone: {variables['tone']}\n\n"
        "First sentence: overall pattern. "
        "Second sentence: explain the source of strain. "
        "Third sentence: summarise likely consequence if unaddressed."
    )

    llm_text, provider = _call_llm(system_prompt=system_prompt, user_prompt=user_prompt)
    if llm_text:
        return llm_text, provider
    return _template_overall_snapshot(variables), PROVIDER_TEMPLATE


def generate_what_results_suggest(section5_context: dict) -> tuple[str, str]:
    system_prompt = (
        "You write reflective workplace alignment narratives for working adults. "
        "Ground every paragraph in the supplied themes only. "
        "Do not diagnose. Do not mention question numbers, raw scores, or bullet points. "
        "Write exactly 3 short paragraphs separated by a single blank line."
    )
    user_prompt = (
        "Write Section 5 (What Your Results Suggest) for a Subjective Alignment report.\n\n"
        f"Context JSON:\n{json.dumps(section5_context, indent=2)}\n\n"
        "Paragraph 1: Understanding the pattern — environmental vs personal factors.\n"
        "Paragraph 2: How the elevated domains interact and what that costs.\n"
        "Paragraph 3: What the central challenge likely is (fit, not capability)."
    )

    llm_text, provider = _call_llm(system_prompt=system_prompt, user_prompt=user_prompt)
    if llm_text:
        return llm_text, provider
    return _template_what_results_suggest(section5_context), PROVIDER_TEMPLATE
