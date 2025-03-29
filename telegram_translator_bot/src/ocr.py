#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图像理解模块，使用Google Gemini API实现图片内容识别和理解功能
原基于pytesseract的OCR功能已被替换
"""

import os
import sys
import logging
import tempfile
import requests
from PIL import Image
import json
import base64
from io import BytesIO

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import GEMINI_API_KEY
from src.translator import TextTranslator

# 设置API密钥
GEMINI_API_KEY = "AIzaSyDGZiLlCNH9SjTExG82j3X3KoOwYAThVgk"  # 您提供的API密钥
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"

class ImageOCR:
    """图片OCR类，使用Gemini API从图片中提取文字和理解内容"""
    
    def __init__(self):
        """初始化Gemini引擎"""
        self.translator = TextTranslator()
    
    def _encode_image(self, image_path):
        """将图像编码为base64格式
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            str: base64编码的图像
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _resize_image_if_needed(self, image_path, max_size_mb=3.5):
        """如果图像太大，调整其大小
        
        Args:
            image_path (str): 图片文件路径
            max_size_mb (float): 最大文件大小（MB）
            
        Returns:
            str: 可能调整大小后的图像路径
        """
        try:
            # 获取文件大小（MB）
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            logging.info(f"原始图像大小: {file_size_mb:.2f} MB")
            
            # 如果文件大小低于限制，直接返回
            if file_size_mb <= max_size_mb:
                return image_path
            
            # 打开图像并调整大小
            img = Image.open(image_path)
            logging.info(f"原始图像尺寸: {img.size}, 模式: {img.mode}")
            
            # 计算需要的缩放比例
            scale_factor = (max_size_mb / file_size_mb) ** 0.5
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            
            # 调整图像大小
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            logging.info(f"调整后的图像尺寸: {resized_img.size}")
            
            # 保存调整后的图像
            resized_path = f"{image_path}_resized.jpg"
            if img.mode == 'RGBA':
                resized_img = resized_img.convert('RGB')
            
            resized_img.save(resized_path, quality=85, optimize=True)
            
            # 检查新文件大小
            new_size_mb = os.path.getsize(resized_path) / (1024 * 1024)
            logging.info(f"调整后的图像大小: {new_size_mb:.2f} MB")
            
            return resized_path
        except Exception as e:
            logging.error(f"调整图像大小时出错: {str(e)}")
            return image_path
    
    def extract_text_from_image(self, image_path):
        """从图片中提取文字
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            str: 从图片中提取的文字
        """
        if not os.path.exists(image_path):
            logging.error(f"图片文件不存在: {image_path}")
            return ""
        
        logging.info(f"开始处理图片: {image_path}")
        
        try:
            # 调整图像大小（如果需要）
            processed_image_path = self._resize_image_if_needed(image_path)
            
            # 将图像编码为base64
            base64_image = self._encode_image(processed_image_path)
            
            # 准备API请求
            headers = {
                "Content-Type": "application/json",
            }
            
            # 构建请求体
            data = {
                "contents": [{
                    "parts": [
                        {"text": "请提取这张图片中的所有文字，只返回文字内容，不要添加额外的解释或描述。如果图片没有文字，请回复'无文字内容'。如果有多种语言，请保留所有语言的内容。"},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }],
                "generation_config": {
                    "temperature": 0.4,
                    "top_p": 1,
                    "top_k": 32,
                    "max_output_tokens": 2048,
                }
            }
            
            # 发送API请求
            api_url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
            logging.info("发送请求到Gemini API")
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    logging.info(f"Gemini API返回成功，文本长度: {len(text)}")
                    
                    # 如果返回了"无文字内容"，将其视为空结果
                    if text.strip() == "无文字内容":
                        logging.info("图片中没有检测到文字")
                        return ""
                    
                    # 返回提取的文本
                    return text
                else:
                    logging.error(f"Gemini API返回异常格式: {json.dumps(result)[:200]}")
            else:
                error_info = response.text[:200] if response.text else f"状态码: {response.status_code}"
                logging.error(f"Gemini API请求失败: {error_info}")
            
            # 如果创建了临时文件，删除它
            if processed_image_path != image_path and os.path.exists(processed_image_path):
                os.unlink(processed_image_path)
                logging.info(f"删除临时调整大小的图像: {processed_image_path}")
                
        except Exception as e:
            logging.error(f"处理图片出错: {str(e)}")
            return ""
        
        return ""
    
    def extract_image_content(self, image_path):
        """理解图片内容
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            str: 图片内容描述
        """
        if not os.path.exists(image_path):
            logging.error(f"图片文件不存在: {image_path}")
            return ""
        
        logging.info(f"开始分析图片内容: {image_path}")
        
        try:
            # 调整图像大小（如果需要）
            processed_image_path = self._resize_image_if_needed(image_path)
            
            # 将图像编码为base64
            base64_image = self._encode_image(processed_image_path)
            
            # 准备API请求
            headers = {
                "Content-Type": "application/json",
            }
            
            # 构建请求体 - 请求对图像内容的理解
            data = {
                "contents": [{
                    "parts": [
                        {"text": "请详细描述这张图片中的内容，包括主要物体、场景、人物、文字等。用中文回答。"},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }],
                "generation_config": {
                    "temperature": 0.7,
                    "top_p": 1,
                    "top_k": 32,
                    "max_output_tokens": 2048,
                }
            }
            
            # 发送API请求
            api_url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
            logging.info("发送图像内容理解请求到Gemini API")
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    description = result["candidates"][0]["content"]["parts"][0]["text"]
                    logging.info(f"Gemini API返回成功，描述长度: {len(description)}")
                    return description
                else:
                    logging.error(f"Gemini API返回异常格式: {json.dumps(result)[:200]}")
            else:
                error_info = response.text[:200] if response.text else f"状态码: {response.status_code}"
                logging.error(f"Gemini API请求失败: {error_info}")
            
            # 如果创建了临时文件，删除它
            if processed_image_path != image_path and os.path.exists(processed_image_path):
                os.unlink(processed_image_path)
                logging.info(f"删除临时调整大小的图像: {processed_image_path}")
                
        except Exception as e:
            logging.error(f"处理图片内容出错: {str(e)}")
            return ""
        
        return ""
    
    def process_image_to_text(self, image_path):
        """处理图片并提取文字，然后翻译成中文
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            dict: 包含原文和翻译结果的字典
        """
        # 从图片中提取文字
        extracted_text = self.extract_text_from_image(image_path)
        
        # 理解图片内容
        content_description = self.extract_image_content(image_path)
        
        # 如果无法提取文字但有内容描述
        if not extracted_text and content_description:
            return {
                "success": True,
                "message": "无法提取文字，但已分析图片内容",
                "original": "",
                "translated": "",
                "detected_language": "",
                "content_description": content_description
            }
        
        # 如果既无法提取文字也无法理解内容
        if not extracted_text and not content_description:
            return {
                "success": False,
                "message": "无法从图片中提取文字或理解内容",
                "original": "",
                "translated": "",
                "content_description": ""
            }
        
        # 翻译提取出的文字
        translation_result = self.translator.translate_to_chinese(extracted_text)
        
        return {
            "success": True,
            "message": "成功从图片中提取并翻译文字",
            "original": translation_result["original"],
            "translated": translation_result["translated"],
            "detected_language": translation_result["detected_language"],
            "content_description": content_description
        }


# 简单测试
if __name__ == "__main__":
    ocr = ImageOCR()
    # 需要提供一个测试图片路径
    test_image_path = "test_image.png"
    if os.path.exists(test_image_path):
        result = ocr.process_image_to_text(test_image_path)
        print(f"图像处理结果: {'成功' if result['success'] else '失败'}")
        if result["success"]:
            if result.get("original"):
                print(f"提取的文字:\n{result['original']}")
                print(f"翻译结果:\n{result['translated']}")
                print(f"检测语言: {result['detected_language']}")
            if result.get("content_description"):
                print(f"图像内容描述:\n{result['content_description']}")
    else:
        print(f"测试图片不存在: {test_image_path}") 