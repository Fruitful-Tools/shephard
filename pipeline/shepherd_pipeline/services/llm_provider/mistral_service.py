"""Real LLM API service implementations."""

from pathlib import Path

import httpx
import requests

from ...config.settings import settings
from ...models.pipeline import CorrectionResult, SummaryResult, TranscriptionResult
from .schema import BaseLLMService


class MistralService(BaseLLMService):
    """Real Mistral API service for text correction, summarization, and transcription."""

    def __init__(self) -> None:
        super().__init__()
        self.api_key = settings.mistral_api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.transcription_url = "https://api.mistral.ai/v1/audio/transcriptions"

    async def transcribe_audio(
        self,
        audio_chunk_path: str,
        language: str = "zh",  # Voxtral uses 'zh' for Chinese
        model: str = "voxtral-mini-latest",
    ) -> TranscriptionResult:
        """Transcribe audio chunk using Voxtral API (Mistral's audio service)."""
        try:
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }

            # Open the audio file
            with Path(audio_chunk_path).open("rb") as audio_file:
                files = {
                    "file": audio_file,
                }
                data = {
                    "model": model,
                    "language": language,
                    "response_format": "verbose_json",  # Get timestamps
                }

                if self.logger:
                    self.logger.info(
                        f"Starting Voxtral transcription for chunk: {audio_chunk_path}"
                    )

                # Make the API request (synchronous for file handling)
                response = requests.post(
                    self.transcription_url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=120.0,  # 2 minutes timeout for transcription
                )

                response.raise_for_status()
                result = response.json()

                # Extract transcription text
                transcription_text = result.get("text", "").strip()
                model_used = result.get("model", model)

                self.logger.info(
                    f"Voxtral transcription completed: {len(transcription_text)} chars"
                )

                return TranscriptionResult(
                    language=language,
                    model=model_used,
                    raw_text=transcription_text,
                )

        except FileNotFoundError:
            self.logger.error(f"Audio file not found: {audio_chunk_path}")
            return TranscriptionResult(
                language=language,
                model=model,
                raw_text="",
                failure_reason="Audio file not found",
            )
        except requests.exceptions.RequestException as e:
            error_details = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_details = f"{e} - Response: {error_json}"
                except Exception:
                    error_details = f"{e} - Status: {e.response.status_code}, Text: {e.response.text[:200]}"

            self.logger.error(f"Mistral API request failed: {error_details}")
            return TranscriptionResult(
                language=language,
                model=model,
                raw_text="",
                failure_reason=error_details,
            )
        except Exception as e:
            self.logger.error(f"Mistral transcription failed: {e}")
            return TranscriptionResult(
                language=language,
                model=model,
                raw_text="",
                failure_reason=str(e),
            )

    async def correct_text(
        self,
        text: str,
        target_language: str = "zh-TW",
        model: str = "mistral-small-latest",
    ) -> CorrectionResult:
        """Correct and enhance transcribed text using Mistral API."""

        # Christian context instructions in Chinese
        system_prompt = """你是一個很熟悉基督教用語的繁體中文文字編輯，這是一段audio transcription，因為是AI產生了，可能有許多錯字與辨識不出來的問題。請你單純修正錯誤的文字，根據上下文給出最合裡的修訂文字，不要額外說明。"""

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.1,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()

                result = response.json()
                corrected_text = result["choices"][0]["message"]["content"].strip()
                model_used = result.get("model", model)

                self.logger.info(
                    f"Mistral correction completed: {len(text)} -> {len(corrected_text)} chars"
                )

                return CorrectionResult(
                    original_text=text,
                    corrected_text=corrected_text,
                    language=target_language,
                    model=model_used,
                )

        except httpx.HTTPStatusError as e:
            error_detail = ""
            if e.response:
                try:
                    error_json = e.response.json()
                    error_detail = f" - {error_json}"
                except Exception:
                    error_detail = f" - Status: {e.response.status_code}, Text: {e.response.text[:200]}"

            self.logger.error(f"Mistral correction failed: {e}{error_detail}")
            # Fallback to original text if API fails
            return CorrectionResult(
                original_text=text,
                corrected_text="",
                language=target_language,
                model=model_used,
                failure_reason=str(e),
            )
        except Exception as e:
            self.logger.error(
                f"Mistral correction failed with unexpected error: {type(e).__name__}: {e}"
            )
            # Fallback to original text if API fails
            return CorrectionResult(
                original_text=text,
                corrected_text=text,
                language=target_language,
                model=f"{model}_failed",
                failure_reason=str(e),
            )

    async def summarize_text(
        self,
        text: str,
        instructions: str | None = None,
        word_limit: int | None = None,
        model: str = "mistral-small-latest",
    ) -> SummaryResult:
        """Generate summary using Mistral API."""

        # Default Christian-focused summarization prompt
        default_instructions = """請為這段基督教內容製作摘要，重點包括：
1. 主要的屬靈教導或信息
2. 重要的聖經引用或原則
3. 實際的應用或呼籲
4. 見證或例子的核心要點

請用繁體中文（台灣）回應，保持基督教用語的準確性。"""

        system_prompt = instructions or default_instructions

        if word_limit:
            system_prompt += f"\n\n請將摘要控制在約{word_limit}字以內。"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"請為以下內容製作摘要：\n\n{text}"},
            ],
            "temperature": 0.3,
            "max_tokens": word_limit * 2 if word_limit else 1000,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=45.0,
                )
                response.raise_for_status()

                result = response.json()
                summary = result["choices"][0]["message"]["content"].strip()
                model_used = result.get("model", model)

                self.logger.info(
                    f"Mistral summarization completed: {len(summary)} chars"
                )

                return SummaryResult(
                    summary=summary,
                    word_count=len(summary),
                    model=model_used,
                    custom_instructions=instructions,
                )

        except Exception as e:
            self.logger.error(f"Mistral summarization failed: {e}")
            # Fallback summary
            fallback_summary = (
                f"摘要生成失敗。原文長度：{len(text)}字符。請檢查網路連接或API配置。"
            )
            return SummaryResult(
                summary=fallback_summary,
                word_count=len(fallback_summary),
                model=model_used,
                custom_instructions=instructions,
                failure_reason=str(e),
            )
