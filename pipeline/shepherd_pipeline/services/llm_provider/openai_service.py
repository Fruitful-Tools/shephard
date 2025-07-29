"""OpenAI service implementation."""

from ...config.settings import settings
from .base_http_service import BaseHTTPService
from .provider_configs import OpenAIConfig
from .schema import CorrectionResult, SummaryResult, TranscriptionResult


class OpenAIService(BaseHTTPService):
    """OpenAI API service for text correction, summarization, and transcription."""

    def __init__(self) -> None:
        config = OpenAIConfig()
        super().__init__(settings.openai_api_key, config.base_url)
        self.config = config

    async def correct_text(
        self, text: str, target_language: str = "zh-TW", model: str = "gpt-4o-mini"
    ) -> CorrectionResult:
        """Correct and enhance transcribed text using OpenAI API."""
        try:
            messages = [
                {"role": "system", "content": self.config.get_correction_prompt()},
                {"role": "user", "content": text},
            ]

            result = await self._make_chat_request(
                messages, model, temperature=0.1, max_tokens=2000
            )
            corrected_text = result["choices"][0]["message"]["content"].strip()
            model_used = self._extract_model_from_response(result, model)

            self.logger.info(
                f"OpenAI correction completed: {len(text)} -> {len(corrected_text)} chars"
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
        model: str = "gpt-4o-mini",
    ) -> SummaryResult:
        """Generate summary using OpenAI API."""
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

            self.logger.info(f"OpenAI summarization completed: {len(summary)} chars")

            return SummaryResult(
                summary=summary,
                word_count=len(summary),
                model=model_used,
                custom_instructions=instructions,
            )

        except Exception as e:
            return self._handle_summarization_error(e, text, model, instructions)

    async def transcribe_audio(
        self, audio_file_path: str, language: str = "zh", model: str = "whisper-1"
    ) -> TranscriptionResult:
        """Transcribe audio using OpenAI Whisper API."""
        try:
            self.logger.info(
                f"Starting OpenAI Whisper transcription for chunk: {audio_file_path}"
            )

            result = await self._make_transcription_request(
                audio_file_path, model, language
            )

            # Extract transcription text
            transcription_text = result.get("text", "").strip()
            model_used = self._extract_model_from_response(result, model)

            # Note: Timestamps handling removed for simplification
            # Could be added back if needed in the future

            self.logger.info(
                f"OpenAI Whisper transcription completed: {len(transcription_text)} chars"
            )

            return TranscriptionResult(
                raw_text=transcription_text,
                language=language,
                model=model_used,
            )

        except Exception as e:
            return self._handle_transcription_error(e, audio_file_path, language, model)
