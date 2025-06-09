from langdetect import detect, detect_langs
from langdetect.lang_detect_exception import LangDetectException
import logging

logger = logging.getLogger(__name__)

class LanguageDetector:
    """语言检测工具类"""
    
    SUPPORTED_LANGUAGES = {
        "es": "Spanish",
        "zh-cn": "Chinese",
        "zh-tw": "Chinese",
        "zh": "Chinese"
    }
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        检测文本语言
        Args:
            text: 输入文本
        Returns:
            语言代码 ("es" 或 "zh")
        """
        try:
            # 获取所有可能的语言及其概率
            langs = detect_langs(text)
            
            # 记录检测到的语言概率
            for lang in langs:
                logger.debug(f"Detected language: {lang.lang} with probability: {lang.prob}")
            
            # 获取最可能的语言
            detected_lang = langs[0].lang
            
            # 处理中文的不同变体
            if detected_lang.startswith("zh"):
                return "zh"
            
            # 检查是否支持该语言
            if detected_lang in LanguageDetector.SUPPORTED_LANGUAGES:
                return detected_lang
            else:
                logger.warning(f"Unsupported language detected: {detected_lang}, falling back to Spanish")
                return "es"  # 默认使用西班牙语
                
        except LangDetectException as e:
            logger.error(f"Language detection error: {str(e)}")
            return "es"  # 出错时默认使用西班牙语
            
    @staticmethod
    def is_supported_language(lang_code: str) -> bool:
        """
        检查语言是否被支持
        Args:
            lang_code: 语言代码
        Returns:
            是否支持该语言
        """
        return lang_code in LanguageDetector.SUPPORTED_LANGUAGES 