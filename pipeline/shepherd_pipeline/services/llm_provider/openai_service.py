"""Real LLM API service implementations."""

from pathlib import Path

import httpx

from ...config.settings import settings
from ...models.pipeline import CorrectionResult, SummaryResult, TranscriptionResult
from .schema import BaseLLMService


class OpenAIService(BaseLLMService):
    """OpenAI API service for text correction and summarization."""

    def __init__(self) -> None:
        super().__init__()
        self.api_key = settings.openai_api_key
        self.base_url = "https://api.openai.com/v1"

    async def correct_text(
        self, text: str, target_language: str = "zh-TW", model: str = "gpt-4o-mini"
    ) -> CorrectionResult:
        """Correct and enhance transcribed text using OpenAI API."""

        # Christian context instructions in Chinese
        system_prompt = """這是一段audio transcription，因為是AI產生了，可能有許多錯字與問題，我需要你把它轉成正確的格式，注意這是基督教的文章或者講道或者見證，所以當你不太確定用語的時候，可以朝這個方向思考。

請修正以下內容：
1. 修正錯字和語法錯誤
2. 使用繁體中文（台灣）
3. 適當的標點符號
4. 保持基督教用語的準確性

只回傳修正後的文字，不要額外說明。"""

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.1,
            "max_tokens": 2000,
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

                if self.logger:
                    self.logger.info(
                        f"OpenAI correction completed: {len(text)} -> {len(corrected_text)} chars"
                    )

                return CorrectionResult(
                    original_text=text,
                    corrected_text=corrected_text,
                    language=target_language,
                    model=model,
                )

        except Exception as e:
            if self.logger:
                self.logger.error(f"OpenAI correction failed: {e}")
            # Fallback to original text if API fails
            return CorrectionResult(
                original_text=text,
                corrected_text="",
                language=target_language,
                model=model,
                failure_reason=str(e),
            )

    async def summarize_text(
        self,
        text: str,
        instructions: str | None = None,
        word_limit: int | None = None,
        model: str = "gpt-4o-mini",
    ) -> SummaryResult:
        """Generate summary using OpenAI API."""

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

                if self.logger:
                    self.logger.info(
                        f"OpenAI summarization completed: {len(summary)} chars"
                    )

                return SummaryResult(
                    summary=summary,
                    word_count=len(summary),
                    model=model,
                    custom_instructions=instructions,
                )

        except Exception as e:
            self.logger.error(f"OpenAI summarization failed: {e}")
            # Fallback summary
            fallback_summary = (
                f"摘要生成失敗。原文長度：{len(text)}字符。請檢查網路連接或API配置。"
            )
            return SummaryResult(
                summary=fallback_summary,
                word_count=len(fallback_summary),
                model=model,
                custom_instructions=instructions,
            )

    async def transcribe_audio(
        self, audio_file_path: str, language: str = "zh", model: str = "whisper-1"
    ) -> TranscriptionResult:
        """Transcribe audio using OpenAI Whisper API."""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }

            with Path(audio_file_path).open("rb") as audio_file:
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
                        f"Starting OpenAI Whisper transcription for chunk: {audio_file_path}"
                    )

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/audio/transcriptions",
                        headers=headers,
                        files=files,
                        data=data,
                        timeout=120.0,  # 2 minutes timeout
                    )

                    response.raise_for_status()
                    result = response.json()

                    # Extract transcription text
                    transcription_text = result.get("text", "").strip()

                    # Extract timestamps if available
                    timestamps = []
                    if "segments" in result:
                        for segment in result["segments"]:
                            timestamps.append(
                                {
                                    "start": segment.get("start", 0.0),
                                    "end": segment.get("end", 0.0),
                                    "text": segment.get("text", "").strip(),
                                }
                            )
                    elif "words" in result:
                        for word in result["words"]:
                            timestamps.append(
                                {
                                    "start": word.get("start", 0.0),
                                    "end": word.get("end", 0.0),
                                    "text": word.get("word", "").strip(),
                                }
                            )

                    if self.logger:
                        self.logger.info(
                            f"OpenAI Whisper transcription completed: {len(transcription_text)} chars"
                        )

                    return TranscriptionResult(
                        raw_text=transcription_text,
                        language=language,
                        model=model,
                    )

        except FileNotFoundError:
            if self.logger:
                self.logger.error(f"Audio file not found: {audio_file_path}")
            return TranscriptionResult(
                raw_text="",
                language=language,
                model=model,
                failure_reason="Audio file not found",
            )
        except Exception as e:
            error_details = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_json = e.response.json()
                    error_details = f"{e} - Response: {error_json}"
                except Exception:
                    error_details = f"{e} - Status: {e.response.status_code}, Text: {e.response.text[:200]}"

            if self.logger:
                self.logger.error(
                    f"OpenAI Whisper transcription failed: {error_details}"
                )
            return TranscriptionResult(
                raw_text="",
                language=language,
                model=model,
                failure_reason=error_details,
            )
