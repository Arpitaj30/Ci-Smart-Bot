# from .llm_engine import ask_llm
# import logging

# logger = logging.getLogger(__name__)

# def analyze_error(context: str) -> tuple:
#     """Analyze CI error and generate fix patch"""
#     try:
#         analysis_prompt = f"""
# You are a senior DevOps engineer analyzing CI/CD failures.
# Provide a brief root cause analysis for this failure.

# Context: {context}
# """
        
#         fix_prompt = f"""
# You are an automated CI fixing agent.

# Rules:
# - Output ONLY a valid unified git diff
# - Do NOT include explanations
# - Start with: diff --git
# - Fix ONLY the error shown

# CI Logs:
# {context}
# """
        
#         analysis = ask_llm(analysis_prompt)
#         patch = ask_llm(fix_prompt)
        
#         return analysis, patch
#     except Exception as e:
#         logger.error(f"Error analyzing: {str(e)}")
#         return "Unable to analyze", ""
    

from .llm_engine import ask_llm
import logging

logger = logging.getLogger(__name__)


def analyze_error(logs: str) -> tuple:
    try:
        analysis_prompt = f"""
You are a senior DevOps engineer.
Explain the root cause of this CI failure in 2–3 sentences.

CI Logs:
{logs}
"""

        fix_prompt = f"""
You are an automated CI fixing agent.

Rules:
- Output ONLY a valid unified git diff
- Start with: diff --git
- Do NOT include explanations or markdown
- Fix ONLY the error shown
- Keep changes minimal

CI Logs:
{logs}
"""

        analysis = ask_llm(analysis_prompt)
        patch = ask_llm(fix_prompt)

        return analysis.strip(), patch.strip()

    except Exception:
        logger.error("Error analysis failed", exc_info=True)
        return "Analysis failed", ""