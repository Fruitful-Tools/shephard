"""Mistral AI service implementation."""

from ...config.settings import settings
from .base_http_service import BaseHTTPService
from .provider_configs import MistralConfig
from .schema import CorrectionResult, SummaryResult, TranscriptionResult


class MistralService(BaseHTTPService):
    """Mistral API service for text correction, summarization, and transcription."""

    def __init__(self) -> None:
        config = MistralConfig()
        super().__init__(settings.mistral_api_key, config.base_url)
        self.config = config

    async def transcribe_audio(
        self,
        audio_chunk_path: str,
        language: str = "zh",  # Voxtral uses 'zh' for Chinese
        model: str = "voxtral-mini-latest",
    ) -> TranscriptionResult:
        """Transcribe audio chunk using Voxtral API (Mistral's audio service)."""
        try:
            self.logger.info(
                f"Starting Voxtral transcription for chunk: {audio_chunk_path}"
            )

            result = await self._make_transcription_request(
                audio_chunk_path, model, language
            )

            # Extract transcription text
            transcription_text = result.get("text", "").strip()
            model_used = self._extract_model_from_response(result, model)

            self.logger.info(
                f"Voxtral transcription completed: {len(transcription_text)} chars"
            )

            return TranscriptionResult(
                language=language,
                model=model_used,
                raw_text=transcription_text,
            )

        except Exception as e:
            return self._handle_transcription_error(
                e, audio_chunk_path, language, model
            )

    async def correct_text(
        self,
        text: str,
        target_language: str = "zh-TW",
        model: str = "mistral-small-latest",
    ) -> CorrectionResult:
        """Correct and enhance transcribed text using Mistral API."""
        try:
            messages = [
                {"role": "system", "content": self.config.get_correction_prompt()},
                {"role": "user", "content": text},
            ]

            result = await self._make_chat_request(messages, model, temperature=0.1)
            corrected_text = result["choices"][0]["message"]["content"].strip()
            model_used = self._extract_model_from_response(result, model)

            self.logger.info(
                f"Mistral correction completed: {len(text)} -> {len(corrected_text)} chars"
            )

            return CorrectionResult(
                original_text=text,
                corrected_text=corrected_text,
                language=target_language,
                model=model_used,
            )

        except Exception as e:
            return self._handle_correction_error(e, text, target_language, model)

    async def summarize_text(
        self,
        text: str,
        instructions: str | None = None,
        word_limit: int | None = None,
        model: str = "mistral-small-latest",
    ) -> SummaryResult:
        """Generate summary using Mistral API."""
        try:
            system_prompt = instructions or self.config.get_summarization_prompt()

            if word_limit:
                system_prompt += f"\n\n請將摘要控制在約{word_limit}字以內。"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"請為以下內容製作摘要：\n\n{text}"},
            ]

            max_tokens = word_limit * 2 if word_limit else 1000
            result = await self._make_chat_request(
                messages, model, temperature=0.3, max_tokens=max_tokens, timeout=45.0
            )

            summary = result["choices"][0]["message"]["content"].strip()
            model_used = self._extract_model_from_response(result, model)

            self.logger.info(f"Mistral summarization completed: {len(summary)} chars")

            return SummaryResult(
                summary=summary,
                word_count=len(summary),
                model=model_used,
                custom_instructions=instructions,
            )

        except Exception as e:
            return self._handle_summarization_error(e, text, model, instructions)
