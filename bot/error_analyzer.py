from .llm_engine import ask_llm
import logging

logger = logging.getLogger(__name__)


def analyze_error(logs: str) -> tuple:
    """
    Analyze CI logs and return:
    - analysis: human-readable explanation
    - patch: unified git diff OR empty string if not applicable
    """
    try:
        # -------- Root cause analysis --------
        analysis_prompt = f"""
You are a senior DevOps engineer.

Explain the root cause of the following CI failure clearly and concisely
in 2–3 sentences. If it is a syntax or configuration error, explain what
is wrong and what needs to be fixed.

CI Logs:
{logs}
"""

        # -------- Patch generation --------
        fix_prompt = f"""
You are an automated CI fixing agent.

Rules:
- If a code fix is possible, output a VALID unified git diff
- Start with: diff --git
- Do NOT include explanations or markdown
- Fix ONLY the error shown
- Keep changes minimal
- If no safe automatic fix is possible, output an EMPTY STRING

CI Logs:
{logs}
"""

        analysis = ask_llm(analysis_prompt) or ""
        patch = ask_llm(fix_prompt) or ""

        analysis = analysis.strip()
        patch = patch.strip()

        # -------- Safety fallback --------
        if not analysis:
            analysis = (
                "The CI pipeline failed, but the root cause could not be "
                "clearly determined from the logs. Please review the error output."
            )

        # If patch is not a valid diff, discard it
        if patch and not patch.startswith("diff --git"):
            logger.warning("LLM returned non-diff patch, ignoring it")
            patch = ""

        return analysis, patch

    except Exception:
        logger.error("Error analysis failed", exc_info=True)
        return (
            "The CI pipeline failed, but the AI analyzer encountered an internal error.",
            "",
        )








# from .llm_engine import ask_llm
# import logging

# logger = logging.getLogger(__name__)


# def analyze_error(logs: str) -> tuple:
#     try:
#         analysis_prompt = f"""
# You are a senior DevOps engineer.
# Explain the root cause of this CI failure in 2–3 sentences.

# CI Logs:
# {logs}
# """

#         fix_prompt = f"""
# You are an automated CI fixing agent.

# Rules:
# - Output ONLY a valid unified git diff
# - Start with: diff --git
# - Do NOT include explanations or markdown
# - Fix ONLY the error shown
# - Keep changes minimal

# CI Logs:
# {logs}
# """

#         analysis = ask_llm(analysis_prompt)
#         patch = ask_llm(fix_prompt)

#         return analysis.strip(), patch.strip()

#     except Exception:
#         logger.error("Error analysis failed", exc_info=True)
#         return "Analysis failed", ""