"""Provider configuration classes for different LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ProviderConfig(ABC):
    """Base configuration for LLM providers."""

    base_url: str
    transcription_endpoint: str
    default_correction_model: str
    default_summarization_model: str
    default_transcription_model: str

    @abstractmethod
    def get_correction_prompt(self) -> str:
        """Get the system prompt for text correction."""
        pass

    @abstractmethod
    def get_summarization_prompt(self) -> str:
        """Get the default system prompt for text summarization."""
        pass

    @abstractmethod
    def get_transcription_params(self, model: str, language: str) -> dict[str, Any]:
        """Get provider-specific transcription parameters."""
        pass

    @abstractmethod
    def get_chat_params(
        self, model: str, temperature: float = 0.1, max_tokens: int | None = None
    ) -> dict[str, Any]:
        """Get provider-specific chat completion parameters."""
        pass


@dataclass
class OpenAIConfig(ProviderConfig):
    """Configuration for OpenAI API."""

    base_url: str = "https://api.openai.com/v1"
    transcription_endpoint: str = "https://api.openai.com/v1/audio/transcriptions"
    default_correction_model: str = "gpt-4o-mini"
    default_summarization_model: str = "gpt-4o-mini"
    default_transcription_model: str = "whisper-1"

    def get_correction_prompt(self) -> str:
        """Get OpenAI-specific correction prompt."""
        return """這是一段audio transcription，因為是AI產生了，可能有許多錯字與問題，我需要你把它轉成正確的格式，注意這是基督教的文章或者講道或者見證，所以當你不太確定用語的時候，可以朝這個方向思考。

請修正以下內容：
1. 修正錯字和語法錯誤
2. 使用繁體中文（台灣）
3. 適當的標點符號
4. 保持基督教用語的準確性

只回傳修正後的文字，不要額外說明。"""

    def get_summarization_prompt(self) -> str:
        """Get OpenAI-specific summarization prompt."""
        return """請為這段基督教內容製作摘要，重點包括：
1. 主要的屬靈教導或信息
2. 重要的聖經引用或原則
3. 實際的應用或呼籲
4. 見證或例子的核心要點

請用繁體中文（台灣）回應，保持基督教用語的準確性。"""

    def get_transcription_params(self, model: str, language: str) -> dict[str, Any]:
        """Get OpenAI-specific transcription parameters."""
        return {
            "model": model,
            "language": language,
            "response_format": "verbose_json",
        }

    def get_chat_params(
        self, model: str, temperature: float = 0.1, max_tokens: int | None = None
    ) -> dict[str, Any]:
        """Get OpenAI-specific chat completion parameters."""
        params = {
            "model": model,
            "temperature": temperature,
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        return params


@dataclass
class MistralConfig(ProviderConfig):
    """Configuration for Mistral API."""

    base_url: str = "https://api.mistral.ai/v1"
    transcription_endpoint: str = "https://api.mistral.ai/v1/audio/transcriptions"
    default_correction_model: str = "mistral-small-latest"
    default_summarization_model: str = "mistral-small-latest"
    default_transcription_model: str = "voxtral-mini-latest"

    def get_correction_prompt(self) -> str:
        """Get Mistral-specific correction prompt."""
        return """你是一個很熟悉基督教用語的繁體中文文字編輯，這是一段audio transcription，因為是AI產生了，可能有許多錯字與辨識不出來的問題。請你單純修正錯誤的文字，根據上下文給出最合裡的修訂文字，不要額外說明。"""

    def get_summarization_prompt(self) -> str:
        """Get Mistral-specific summarization prompt."""
        return """請為這段基督教內容製作摘要，重點包括：
1. 主要的屬靈教導或信息
2. 重要的聖經引用或原則
3. 實際的應用或呼籲
4. 見證或例子的核心要點

請用繁體中文（台灣）回應，保持基督教用語的準確性。"""

    def get_transcription_params(self, model: str, language: str) -> dict[str, Any]:
        """Get Mistral-specific transcription parameters."""
        return {
            "model": model,
            "language": language,  # Voxtral uses 'zh' for Chinese
            "response_format": "verbose_json",
        }

    def get_chat_params(
        self, model: str, temperature: float = 0.1, max_tokens: int | None = None
    ) -> dict[str, Any]:
        """Get Mistral-specific chat completion parameters."""
        params = {
            "model": model,
            "temperature": temperature,
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        return params


# Provider registry for easy extension
PROVIDER_CONFIGS = {
    "openai": OpenAIConfig(),
    "mistral": MistralConfig(),
}
