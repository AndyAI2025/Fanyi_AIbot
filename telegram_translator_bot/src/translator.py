#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译模块，使用translate库实现文本翻译功能
"""

import sys
import os
import langid
from translate import Translator

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import TRANSLATION_API, TARGET_LANGUAGE, DEEPL_API_KEY

class TextTranslator:
    """文本翻译类，支持多种翻译API"""
    
    def __init__(self):
        """初始化翻译器"""
        self.api = TRANSLATION_API
        self.target_language = TARGET_LANGUAGE.split('-')[0]  # translate库使用简化的语言代码
        
    def detect_language(self, text):
        """检测文本语言
        
        Args:
            text (str): 待检测的文本
            
        Returns:
            str: 检测到的语言代码
        """
        try:
            lang, _ = langid.classify(text)
            return lang
        except Exception as e:
            print(f"语言检测错误: {str(e)}")
            return "auto"  # 默认返回auto
    
    def translate_to_chinese(self, text):
        """将文本翻译成中文
        
        Args:
            text (str): 待翻译的文本
            
        Returns:
            dict: 包含原文、翻译结果和检测到的语言的字典
        """
        if not text or not text.strip():
            return {
                "original": text,
                "translated": "",
                "detected_language": "unknown"
            }
        
        detected_lang = self.detect_language(text)
        
        # 如果已经是中文，无需翻译
        if detected_lang in ['zh', 'zh-CN', 'zh-TW']:
            return {
                "original": text,
                "translated": text,
                "detected_language": detected_lang
            }
        
        # 执行翻译
        try:
            translator = Translator(to_lang=self.target_language, from_lang=detected_lang)
            translated_text = translator.translate(text)
            
            return {
                "original": text,
                "translated": translated_text,
                "detected_language": detected_lang
            }
        except Exception as e:
            print(f"翻译错误: {str(e)}")
            return {
                "original": text,
                "translated": f"翻译出错: {str(e)}",
                "detected_language": detected_lang
            }


# 简单测试
if __name__ == "__main__":
    translator = TextTranslator()
    result = translator.translate_to_chinese("Hello, world!")
    print(f"原文: {result['original']}")
    print(f"翻译: {result['translated']}")
    print(f"检测语言: {result['detected_language']}") 