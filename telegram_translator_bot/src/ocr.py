#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OCR模块，使用pytesseract实现图片文字识别功能
"""

import os
import sys
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import tempfile
import langid
import logging
import platform

# 打印pytesseract版本和路径，用于调试
print(f"pytesseract版本: {pytesseract.__version__}")
print(f"tesseract路径: {pytesseract.pytesseract.tesseract_cmd}")

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import OCR_API, GOOGLE_VISION_API_KEY
from src.translator import TextTranslator

# 根据操作系统设置Tesseract路径
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# 打印设置后的路径确认
print(f"设置后的tesseract路径: {pytesseract.pytesseract.tesseract_cmd}")

class ImageOCR:
    """图片OCR类，用于从图片中提取文字"""
    
    def __init__(self):
        """初始化OCR引擎"""
        self.api = OCR_API
        self.translator = TextTranslator()
    
    def enhance_image(self, image_path):
        """增强图像以提高OCR识别率
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            str: 增强后的图像路径
        """
        try:
            # 打开图像
            logging.info(f"开始增强图像: {image_path}")
            img = Image.open(image_path)
            logging.info(f"原始图像大小: {img.size}, 模式: {img.mode}")
            
            # 转为RGB模式（处理可能的RGBA图像）
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                logging.info("将RGBA图像转换为RGB模式")
            elif img.mode != 'RGB':
                img = img.convert('RGB')
                logging.info(f"将{img.mode}图像转换为RGB模式")
            
            # 调整大小（如果图像太大）
            max_size = 2000
            if img.width > max_size or img.height > max_size:
                ratio = min(max_size / img.width, max_size / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
                logging.info(f"调整图像大小为: {new_size}")
            
            # 增加对比度
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # 增加对比度
            logging.info("增加图像对比度")
            
            # 增加亮度
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)  # 略微增加亮度
            logging.info("增加图像亮度")
            
            # 锐化图像
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)  # 增加锐度
            logging.info("增加图像锐度")
            
            # 应用去噪滤镜
            img = img.filter(ImageFilter.MedianFilter(size=3))
            logging.info("应用中值滤波去噪")
            
            # 二值化处理（可选，仅在需要时使用）
            # 转为灰度图
            gray_img = img.convert('L')
            # 使用阈值将图像二值化
            threshold = 150
            binary_img = gray_img.point(lambda x: 0 if x < threshold else 255, '1')
            logging.info("将图像转换为二值图像")
            
            # 保存增强后的图像
            enhanced_path = f"{image_path}_enhanced.jpg"
            binary_img.save(enhanced_path)
            logging.info(f"保存增强后的图像到: {enhanced_path}")
            
            return enhanced_path
        except Exception as e:
            logging.error(f"图像增强错误: {str(e)}")
            return image_path  # 如果增强失败，返回原始图像路径
        
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
        
        # 打印详细的调试信息
        logging.info(f"OCR处理图片开始: {image_path}")
        logging.info(f"Tesseract路径: {pytesseract.pytesseract.tesseract_cmd}")
        
        # 获取文件信息
        file_size = os.path.getsize(image_path)
        logging.info(f"图片文件大小: {file_size} 字节")
        
        # 获取Tesseract版本
        try:
            tesseract_version = pytesseract.get_tesseract_version()
            logging.info(f"Tesseract版本: {tesseract_version}")
        except Exception as e:
            logging.error(f"获取Tesseract版本失败: {str(e)}")
        
        # 获取可用的语言列表
        try:
            languages = pytesseract.get_languages()
            logging.info(f"Tesseract可用语言: {languages}")
        except Exception as e:
            logging.error(f"获取Tesseract语言列表失败: {str(e)}")
        
        text = ""
        
        try:
            if self.api == "tesseract":
                # 增强图像
                enhanced_image_path = self.enhance_image(image_path)
                logging.info(f"图像增强后保存到: {enhanced_image_path}")
                
                # 使用Tesseract OCR，支持多语言
                # chi_sim: 简体中文, eng: 英文, jpn: 日文
                image = Image.open(enhanced_image_path)
                logging.info(f"成功打开图像，大小: {image.size}, 模式: {image.mode}")
                
                # 直接尝试各种语言模式
                ocr_results = []
                
                # 尝试多语言识别
                try:
                    logging.info("尝试使用简体中文+英文识别")
                    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                    ocr_results.append(("chi_sim+eng", text))
                    logging.info(f"chi_sim+eng 识别结果长度: {len(text)}")
                except Exception as e:
                    logging.error(f"简体中文+英文识别失败: {str(e)}")
                
                if not text.strip():
                    try:
                        logging.info("尝试仅使用简体中文识别")
                        text = pytesseract.image_to_string(image, lang='chi_sim')
                        ocr_results.append(("chi_sim", text))
                        logging.info(f"chi_sim 识别结果长度: {len(text)}")
                    except Exception as e:
                        logging.error(f"简体中文识别失败: {str(e)}")
                
                if not text.strip():
                    try:
                        logging.info("尝试仅使用英文识别")
                        text = pytesseract.image_to_string(image, lang='eng')
                        ocr_results.append(("eng", text))
                        logging.info(f"eng 识别结果长度: {len(text)}")
                    except Exception as e:
                        logging.error(f"英文识别失败: {str(e)}")
                
                if not text.strip():
                    try:
                        logging.info("尝试不指定语言识别")
                        text = pytesseract.image_to_string(image)
                        ocr_results.append(("default", text))
                        logging.info(f"默认识别结果长度: {len(text)}")
                    except Exception as e:
                        logging.error(f"默认识别失败: {str(e)}")
                
                # 如果增强图像是临时创建的，删除它
                if enhanced_image_path != image_path and os.path.exists(enhanced_image_path):
                    os.unlink(enhanced_image_path)
                    logging.info(f"删除增强后的临时图像: {enhanced_image_path}")
                
                # 打印所有OCR尝试结果
                for lang, result in ocr_results:
                    result_preview = result[:50] + "..." if len(result) > 50 else result
                    logging.info(f"OCR结果 ({lang}): '{result_preview}'")
            
            elif self.api == "google_vision" and GOOGLE_VISION_API_KEY:
                # 这里可以添加Google Vision API的实现
                # 需要安装google-cloud-vision库
                pass
                
        except Exception as e:
            logging.error(f"OCR处理出错: {str(e)}")
            return ""
        
        # 最终文本清理和记录
        text = text.strip()
        text_preview = text[:100] + "..." if len(text) > 100 else text
        logging.info(f"最终OCR结果: '{text_preview}'")
        
        return text
    
    def process_image_to_text(self, image_path):
        """处理图片并提取文字，然后翻译成中文
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            dict: 包含原文和翻译结果的字典
        """
        # 从图片中提取文字
        extracted_text = self.extract_text_from_image(image_path)
        
        if not extracted_text:
            return {
                "success": False,
                "message": "无法从图片中提取文字",
                "original": "",
                "translated": ""
            }
        
        # 翻译提取出的文字
        translation_result = self.translator.translate_to_chinese(extracted_text)
        
        return {
            "success": True,
            "message": "成功从图片中提取并翻译文字",
            "original": translation_result["original"],
            "translated": translation_result["translated"],
            "detected_language": translation_result["detected_language"]
        }


# 简单测试
if __name__ == "__main__":
    ocr = ImageOCR()
    # 需要提供一个测试图片路径
    test_image_path = "test_image.png"
    if os.path.exists(test_image_path):
        result = ocr.process_image_to_text(test_image_path)
        print(f"OCR结果: {'成功' if result['success'] else '失败'}")
        if result["success"]:
            print(f"原文:\n{result['original']}")
            print(f"翻译:\n{result['translated']}")
            print(f"检测语言: {result['detected_language']}")
    else:
        print(f"测试图片不存在: {test_image_path}") 