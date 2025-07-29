"""Base HTTP service for LLM providers."""

from pathlib import Path
from typing import Any

import httpx

from .schema import BaseLLMService, CorrectionResult, SummaryResult, TranscriptionResult


class BaseHTTPService(BaseLLMService):
    """Base HTTP service with common request handling patterns."""

    def __init__(self, api_key: str, base_url: str) -> None:
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _make_chat_request(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int | None = None,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """Make a chat completion request."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        headers = self._get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]

    async def _make_transcription_request(
        self,
        audio_file_path: str,
        model: str,
        language: str = "zh",
        timeout: float = 120.0,
    ) -> dict[str, Any]:
        """Make an audio transcription request."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        with Path(audio_file_path).open("rb") as audio_file:
            files = {"file": audio_file}
            data = {
                "model": model,
                "language": language,
                "response_format": "verbose_json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=timeout,
                )
                response.raise_for_status()
                return response.json()  # type: ignore[no-any-return]

    def _handle_correction_error(
        self,
        error: Exception,
        original_text: str,
        target_language: str,
        model: str,
    ) -> CorrectionResult:
        """Handle correction errors with consistent fallback."""
        error_msg = self._extract_error_message(error)
        self.logger.error(f"Text correction failed: {error_msg}")

        return CorrectionResult(
            original_text=original_text,
            corrected_text="",
            language=target_language,
            model=model,
            failure_reason=error_msg,
        )

    def _handle_summarization_error(
        self,
        error: Exception,
        text: str,
        model: str,
        instructions: str | None = None,
    ) -> SummaryResult:
        """Handle summarization errors with consistent fallback."""
        error_msg = self._extract_error_message(error)
        self.logger.error(f"Text summarization failed: {error_msg}")

        fallback_summary = (
            f"摘要生成失敗。原文長度：{len(text)}字符。請檢查網路連接或API配置。"
        )

        return SummaryResult(
            summary=fallback_summary,
            word_count=len(fallback_summary),
            model=model,
            custom_instructions=instructions,
            failure_reason=error_msg,
        )

    def _handle_transcription_error(
        self,
        error: Exception,
        audio_file_path: str,
        language: str,
        model: str,
    ) -> TranscriptionResult:
        """Handle transcription errors with consistent fallback."""
        if isinstance(error, FileNotFoundError):
            error_msg = f"Audio file not found: {audio_file_path}"
            self.logger.error(error_msg)
        else:
            error_msg = self._extract_error_message(error)
            self.logger.error(f"Audio transcription failed: {error_msg}")

        return TranscriptionResult(
            raw_text="",
            language=language,
            model=model,
            failure_reason=error_msg,
        )

    def _extract_error_message(self, error: Exception) -> str:
        """Extract detailed error message from exception."""
        if hasattr(error, "response") and error.response is not None:
            try:
                error_json = error.response.json()
                return f"{error} - Response: {error_json}"
            except Exception:
                return f"{error} - Status: {error.response.status_code}, Text: {error.response.text[:200]}"
        return str(error)

    def _extract_model_from_response(
        self, response: dict[str, Any], default_model: str
    ) -> str:
        """Extract the actual model used from API response."""
        return response.get("model", default_model)  # type: ignore[no-any-return]
