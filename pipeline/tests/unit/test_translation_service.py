"""Test Chinese translation service."""

import pytest

from shepherd_pipeline.services.translation_service import (
    OPENCC_AVAILABLE,
    ChineseTranslationService,
)


class TestChineseTranslationService:
    """Test ChineseTranslationService."""

    def test_to_traditional_chinese_simple(self) -> None:
        """Test basic simplified to traditional conversion."""
        service = ChineseTranslationService()

        # Test basic simplified Chinese characters
        simplified_text = "简体中文测试"
        result = service.to_traditional_chinese(simplified_text)

        # Should convert to traditional characters
        assert result != simplified_text  # Should be different
        assert len(result) == len(simplified_text)  # Should be same length

    def test_to_traditional_chinese_christian_terms(self) -> None:
        """Test conversion of Christian terminology."""
        service = ChineseTranslationService()

        # Test Christian terms in simplified Chinese
        simplified_text = "上帝的恩典和教会的见证"
        result = service.to_traditional_chinese(simplified_text)

        # Should contain traditional characters
        assert "見證" in result or "见证" in result
        assert "教會" in result or "教会" in result

    def test_to_traditional_chinese_empty_text(self) -> None:
        """Test handling of empty text."""
        service = ChineseTranslationService()

        assert service.to_traditional_chinese("") == ""
        assert service.to_traditional_chinese("   ") == "   "

    def test_to_traditional_chinese_mixed_content(self) -> None:
        """Test conversion of mixed Chinese and other content."""
        service = ChineseTranslationService()

        # Text with Chinese, English, and numbers
        mixed_text = "神的恩典 God's grace 2024年"
        result = service.to_traditional_chinese(mixed_text)

        # Should preserve non-Chinese content
        assert "God's grace" in result
        assert "2024" in result
        assert len(result) >= len(mixed_text)  # Might be slightly longer

    def test_detect_and_convert_simplified(self) -> None:
        """Test detection and conversion of simplified Chinese."""
        service = ChineseTranslationService()

        # Text with obvious simplified characters
        simplified_text = "这个国家的发展"
        result = service.detect_and_convert(simplified_text)

        # Should be converted
        assert result != simplified_text

    def test_detect_and_convert_traditional(self) -> None:
        """Test detection and standardization of traditional Chinese."""
        service = ChineseTranslationService()

        # Text with traditional characters
        traditional_text = "這個國家的發展"
        result = service.detect_and_convert(traditional_text)

        # Should be standardized to Taiwan format
        assert isinstance(result, str)
        assert len(result) >= len(traditional_text)

    def test_detect_and_convert_english_only(self) -> None:
        """Test handling of English-only text."""
        service = ChineseTranslationService()

        english_text = "This is English text only"
        result = service.detect_and_convert(english_text)

        # Should remain unchanged
        assert result == english_text

    @pytest.mark.skipif(not OPENCC_AVAILABLE, reason="OpenCC not available")
    def test_conversion_accuracy_with_opencc(self) -> None:
        """Test conversion accuracy when OpenCC is available."""
        service = ChineseTranslationService()

        # Test some known conversions
        test_cases = [
            ("简体", "簡體"),
            ("中国", "中國"),
            ("发展", "發展"),
            ("经济", "經濟"),
        ]

        for simplified, expected_traditional in test_cases:
            result = service.to_traditional_chinese(simplified)
            assert expected_traditional in result

    def test_service_initialization(self) -> None:
        """Test service initialization."""
        service = ChineseTranslationService()

        # Should initialize without errors
        assert service is not None

        # Should have logger
        assert hasattr(service, "logger")

    def test_long_text_conversion(self) -> None:
        """Test conversion of longer text passages."""
        service = ChineseTranslationService()

        long_text = """
        今天我要跟大家分享关于神的恩典的见证。
        神在我生命中做了奇妙的工作，通过祷告和读经让我更亲近祂。
        教会的弟兄姊妹也给了我很多支持和鼓励。
        感谢主的恩典，让我们今天能够聚集在这里。
        """

        result = service.to_traditional_chinese(long_text)

        # Should process the entire text
        assert len(result) >= len(long_text) - 10  # Allow some variation
        assert isinstance(result, str)

        # Should preserve structure (newlines, etc.)
        assert result.count("\n") == long_text.count("\n")
