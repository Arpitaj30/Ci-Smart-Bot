from .llm_engine import ask_llm
import logging

logger = logging.getLogger(__name__)

def analyze_error(context: str) -> tuple:
    """Analyze CI error and generate fix patch"""
    try:
        analysis_prompt = f"""
You are a senior DevOps engineer analyzing CI/CD failures.
Provide a brief root cause analysis for this failure.

Context: {context}
"""
        
        fix_prompt = f"""
Generate a minimal git diff patch to fix this CI failure.
Output only the valid diff.

Context: {context}
"""
        
        analysis = ask_llm(analysis_prompt)
        patch = ask_llm(fix_prompt)
        
        return analysis, patch
    except Exception as e:
        logger.error(f"Error analyzing: {str(e)}")
        return "Unable to analyze", ""