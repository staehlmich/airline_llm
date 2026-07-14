"""
LLM initialization layer using LangChain's init_chat_model.

This module provides a thin wrapper around LangChain's native model initialization,
handling provider-specific configurations and applying necessary patches.
"""

import logging
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def apply_chatgpt_patch() -> None:
    """
    Apply hotfix for stop-parameter error in newer ChatGPT models.

    This patch removes the 'stop' parameter from kwargs to prevent errors.
    Note: Removing this patch changes the output behavior.
    """
    original_generate = ChatOpenAI._generate

    def patched_generate(self, messages, stop=None, **kwargs):
        kwargs.pop("stop", None)
        return original_generate(self, messages, **kwargs)

    ChatOpenAI._generate = patched_generate
    logger.debug("ChatOpenAI patch applied for stop parameter handling")


def create_chat_model(
        provider: str,
        model_name: str,
        temperature: float = 0,
        api_key: Optional[str] = None,
) -> BaseChatModel:
    """
    Create a chat model using LangChain's native init_chat_model.

    Args:
        provider: Model provider (e.g., 'openai', 'anthropic', 'google-vertexai')
        model_name: Name of the model (e.g., 'gpt-3.5-turbo', 'claude-3-5-sonnet-20241022')
        temperature: Sampling temperature (0 = deterministic, higher = more random)
        api_key: Optional API key for BYOK (Bring Your Own Key). If not provided,
                 uses the key from environment variables.

    Returns:
        Initialized chat model instance

    Examples:
        # Backend usage (uses OPENAI_API_KEY from .env)
        >>> llm = create_chat_model('openai', 'gpt-3.5-turbo', temperature=0)

        # BYOK usage (API provides the key)
        >>> llm = create_chat_model('openai', 'gpt-3.5-turbo', api_key='sk-...')
    """
    # Apply OpenAI-specific patches if needed
    if provider == "openai":
        apply_chatgpt_patch()

    # Build kwargs for init_chat_model
    kwargs = {
        "model": model_name,
        "model_provider": provider,
        "temperature": temperature,
    }

    # Add API key if provided (BYOK scenario)
    if api_key:
        kwargs["api_key"] = api_key
        logger.info(f"Creating {provider} model '{model_name}' with provided API key")
    else:
        logger.info(f"Creating {provider} model '{model_name}' with environment API key")

    # Use LangChain's native initialization
    llm = init_chat_model(**kwargs)

    return llm