"""Chinese translation service using OpenCC."""

from typing import Any

try:
    from prefect import get_run_logger

    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False

try:
    from opencc import OpenCC  # type: ignore[import-untyped]

    OPENCC_AVAILABLE = True
except ImportError:
    OPENCC_AVAILABLE = False


class ChineseTranslationService:
    """Service for Chinese text conversion using OpenCC."""

    def __init__(self) -> None:
        # Try to get Prefect logger, fallback to None if not in Prefect context
        self.logger: Any = None
        try:
            if PREFECT_AVAILABLE:
                self.logger = get_run_logger()
        except Exception:
            pass

        if OPENCC_AVAILABLE:
            # Initialize OpenCC converters
            self.s2tw = OpenCC("s2tw")  # Simplified to Traditional (Taiwan)
            self.t2tw = OpenCC(
                "t2tw"
            )  # Traditional to Traditional (Taiwan) - standardization
        else:
            if self.logger:
                self.logger.warning("OpenCC not available, translation will be skipped")

    def to_traditional_chinese(self, text: str) -> str:
        """Convert text to Traditional Chinese (Taiwan standard)."""

        if not OPENCC_AVAILABLE:
            if self.logger:
                self.logger.warning("OpenCC not available, returning original text")
            return text

        if not text or not text.strip():
            return text

        try:
            # First convert simplified to traditional
            traditional = self.s2tw.convert(text)

            # Then standardize to Taiwan variant
            taiwan_traditional = self.t2tw.convert(traditional)

            if self.logger:
                self.logger.info(
                    f"Text converted to Traditional Chinese (TW): {len(text)} chars"
                )
            return str(taiwan_traditional)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Chinese translation failed: {e}")
            return text  # Return original text if conversion fails

    def detect_and_convert(self, text: str) -> str:
        """Detect text type and convert to Traditional Chinese (Taiwan)."""

        if not OPENCC_AVAILABLE:
            return text

        # Simple heuristic to detect if text contains simplified characters
        simplified_chars = set("国会时间长东发业产设认为说话语过个学来人么区域建发达觉")
        traditional_chars = set(
            "國會時間長東發業產設認為說話語過個學來人麼區域建發達覺"
        )

        has_simplified = any(char in simplified_chars for char in text)
        has_traditional = any(char in traditional_chars for char in text)

        if has_simplified and not has_traditional:
            if self.logger:
                self.logger.info(
                    "Detected Simplified Chinese, converting to Traditional"
                )
            return self.to_traditional_chinese(text)
        else:
            # Already traditional or mixed, just standardize to Taiwan format
            if self.logger:
                self.logger.info("Standardizing to Taiwan Traditional Chinese")
            try:
                return str(self.t2tw.convert(text)) if OPENCC_AVAILABLE else text
            except Exception:
                return text
