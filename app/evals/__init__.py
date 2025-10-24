"""
Evaluation module for QA Coach.

Provides LLM-as-a-judge capabilities for assessing suggestion quality.
"""

from app.evals.judge import evaluate_suggestion, JudgeResponse

__all__ = ["evaluate_suggestion", "JudgeResponse"]
