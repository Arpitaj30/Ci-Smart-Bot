"""
AI CI/CD Fix Bot - Automatically analyzes and fixes CI/CD pipeline failures
across multiple GitHub repositories using GitHub App integration.
"""

__version__ = "1.0.0"
__author__ = "CI Bot Team"

from .app import app

__all__ = ["app"]
