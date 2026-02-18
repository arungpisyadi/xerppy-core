"""LLM Factory for Xerppy AI Core.

This module provides a robust factory for creating LLM (Large Language Model) instances
from different providers with proper configuration and validation.
"""

import os

from crewai import LLM


class LLMFactory:
    """Factory class to create LLM instances from different providers."""

    @staticmethod
    def create_llm(provider: str, model: str) -> LLM:
        """Create an LLM instance based on the specified provider and model.

        Args:
            provider: The LLM provider (openai, gemini, or huggingface)
            model: The specific model to use

        Returns:
            LLM instance configured for the specified provider and model

        Raises:
            ValueError: If the provider is not supported or API key is missing
        """
        provider = provider.lower().strip()

        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            return LLM(model=model, api_key=api_key)

        elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required")
            return LLM(model=f"gemini/{model}", api_key=api_key)

        elif provider == "huggingface":
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                raise ValueError("HUGGINGFACE_API_KEY environment variable is required")
            return LLM(
                model=f"huggingface/{model}",
                base_url="https://api.inference.huggingface.co",
                api_key=api_key
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                "Supported providers: openai, gemini, huggingface"
            )
