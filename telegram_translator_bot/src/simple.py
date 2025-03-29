#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram翻译机器人 - 超简化版本
使用HTTP请求直接与Telegram API通信，不依赖复杂的库
"""

import os
import sys
import time
import json
import logging
import tempfile
import requests
import platform
import hashlib
from urllib.parse import urljoin
import pytesseract

# 检查Python版本
python_version = platform.python_version()
if not python_version.startswith('3.11'):
    print(f"警告: 当前Python版本为 {python_version}，推荐使用Python 3.11以确保最佳兼容性")
    print("您可以继续运行，但可能会遇到兼容性问题")
    time.sleep(2)  # 暂停2秒，让用户看到警告信息

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.translator import TextTranslator
from src.ocr import ImageOCR
from config.config import TEMP_FOLDER

# 设置更详细的日志格式
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 创建临时文件夹（如果不存在）
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# 初始化翻译器和OCR
translator = TextTranslator()
ocr_engine = ImageOCR()

# 设置Telegram Bot API令牌
TOKEN = "7843869894:AAGzc9u9lVEHf6kSIQOXLmbW7Om3E6idH6c"  # 使用您提供的令牌
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# 存储已处理的更新ID，防止重复处理
processed_update_ids = set()

# 存储已处理的文件ID，防止对同一文件进行多次OCR
processed_file_ids = {}

# 控制重试次数和间隔
MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def get_updates(offset=None):
    """获取机器人更新"""
    url = urljoin(BASE_URL, "getUpdates")
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    
    for retry in range(MAX_RETRIES):
        try:
            # 添加超时参数，避免长时间阻塞
            response = requests.get(url, params=params, timeout=60)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取更新失败，状态码: {response.status_code}，响应: {response.text}")
                time.sleep(RETRY_DELAY * (retry + 1))
        except Exception as e:
            logger.error(f"获取更新时出错 (尝试 {retry+1}/{MAX_RETRIES}): {e}")
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (retry + 1))
    
    return {"ok": False}


def send_message(chat_id, text):
    """发送消息"""
    url = urljoin(BASE_URL, "sendMessage")
    params = {
        "chat_id": chat_id,
        "text": text
    }
    
    for retry in range(MAX_RETRIES):
        try:
            # 添加超时参数，避免长时间阻塞
            response = requests.post(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"发送消息失败，状态码: {response.status_code}，响应: {response.text}")
                time.sleep(RETRY_DELAY * (retry + 1))
        except Exception as e:
            logger.error(f"发送消息时出错 (尝试 {retry+1}/{MAX_RETRIES}): {e}")
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (retry + 1))
    
    return {"ok": False}


def delete_message(chat_id, message_id):
    """删除消息"""
    if not message_id:
        logger.warning(f"尝试删除消息失败: message_id为空")
        return {"ok": False}
        
    url = urljoin(BASE_URL, "deleteMessage")
    params = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    
    for retry in range(MAX_RETRIES):
        try:
            # 添加超时参数
            logger.info(f"尝试删除消息: chat_id={chat_id}, message_id={message_id}")
            response = requests.post(url, params=params, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    logger.info(f"成功删除消息: message_id={message_id}")
                    return result
                else:
                    logger.error(f"删除消息API返回错误: {result.get('description', '未知错误')}")
            else:
                logger.error(f"删除消息失败，状态码: {response.status_code}，响应: {response.text}")
            time.sleep(RETRY_DELAY * (retry + 1))
        except Exception as e:
            logger.error(f"删除消息时出错 (尝试 {retry+1}/{MAX_RETRIES}): {e}")
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (retry + 1))
    
    return {"ok": False}


def get_file(file_id):
    """获取文件信息"""
    url = urljoin(BASE_URL, "getFile")
    params = {"file_id": file_id}
    
    for retry in range(MAX_RETRIES):
        try:
            # 添加超时参数
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取文件信息失败，状态码: {response.status_code}，响应: {response.text}")
                time.sleep(RETRY_DELAY * (retry + 1))
        except Exception as e:
            logger.error(f"获取文件信息时出错 (尝试 {retry+1}/{MAX_RETRIES}): {e}")
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (retry + 1))
    
    return {"ok": False}


def download_file(file_path, destination):
    """下载文件"""
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    
    for retry in range(MAX_RETRIES):
        try:
            # 添加超时参数
            response = requests.get(url, stream=True, timeout=60)
            if response.status_code == 200:
                with open(destination, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
            else:
                logger.error(f"下载文件失败，状态码: {response.status_code}")
                time.sleep(RETRY_DELAY * (retry + 1))
        except Exception as e:
            logger.error(f"下载文件时出错 (尝试 {retry+1}/{MAX_RETRIES}): {e}")
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (retry + 1))
    
    return False


def handle_message(message):
    """处理收到的消息"""
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")
    photo = message.get("photo")
    
    if not chat_id:
        return
    
    if text:
        # 处理文本消息
        if text == "/start":
            welcome_message = """
欢迎使用翻译机器人！

我可以帮你将任何语言翻译成中文，只需发送文本消息或图片给我。

- 发送文字消息：我会自动检测语言并翻译成中文
- 发送图片：我会识别图片中的文字并翻译成中文

使用 /help 查看更多帮助信息。
"""
            send_message(chat_id, welcome_message)
            
        elif text == "/help":
            help_message = """
使用方法：

1. 翻译文本：直接发送任何语言的文本，我会自动翻译成中文
2. 翻译图片中的文字：发送图片，我会识别图片中的文字并翻译成中文

请注意：
- 只支持文本和图片翻译
- 翻译结果仅供参考
- 大型图片处理可能需要一些时间

如有问题，请联系开发者。
"""
            send_message(chat_id, help_message)
            
        elif not text.startswith("/"):
            # 翻译文本
            logger.info(f"收到来自 {message.get('from', {}).get('first_name')} 的文本: {text[:20]}...")
            result = translator.translate_to_chinese(text)
            
            # 准备回复消息
            if result["original"] == result["translated"]:
                # 如果原文和译文相同（可能已经是中文）
                reply_text = f"文本已经是中文，无需翻译。"
            else:
                # 显示原文和译文
                reply_text = f"原文 [{result['detected_language']}]:\n{result['original']}\n\n译文:\n{result['translated']}"
            
            send_message(chat_id, reply_text)
    
    elif photo:
        # 获取最大尺寸的图片
        file_id = photo[-1]["file_id"]
        
        # 检查该图片是否已经处理过
        if file_id in processed_file_ids:
            logger.info(f"跳过已处理的图片文件: ID={file_id}")
            # 如果超过一定时间（例如10分钟），可以清除缓存，允许重新处理
            cached_time = processed_file_ids[file_id]["time"]
            if time.time() - cached_time > 600:  # 10分钟
                logger.info(f"缓存已过期，允许重新处理图片: ID={file_id}")
                del processed_file_ids[file_id]
            else:
                return
        
        # 告知用户正在处理
        processing_result = send_message(chat_id, "正在处理图片，请稍等...")
        processing_msg_id = None
        if processing_result and processing_result.get("ok"):
            processing_msg_id = processing_result["result"]["message_id"]
            logger.info(f"已发送处理中消息: message_id={processing_msg_id}")
        
        file_info = get_file(file_id)
        
        if file_info.get("ok"):
            file_path = file_info["result"]["file_path"]
            
            # 创建临时文件保存图片
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=TEMP_FOLDER) as temp_file:
                temp_path = temp_file.name
            
            try:
                # 下载图片到临时文件
                if download_file(file_path, temp_path):
                    logger.info(f"收到来自 {message.get('from', {}).get('first_name')} 的图片，保存至 {temp_path}")
                    
                    # 使用OCR处理图片
                    result = ocr_engine.process_image_to_text(temp_path)
                    
                    # 删除临时文件
                    os.unlink(temp_path)
                    
                    # 发送处理完成消息（稍后也会删除）
                    complete_result = send_message(chat_id, "处理完成。")
                    complete_msg_id = None
                    if complete_result and complete_result.get("ok"):
                        complete_msg_id = complete_result["result"]["message_id"]
                        logger.info(f"已发送处理完成消息: message_id={complete_msg_id}")
                    
                    # 准备回复消息
                    if result["success"]:
                        if result["original"] == result["translated"]:
                            # 如果原文和译文相同（可能已经是中文）
                            reply_text = f"图片中的文字已经是中文，无需翻译。\n\n文字内容:\n{result['original']}"
                        else:
                            if result["original"]:
                                # 显示原文和译文
                                reply_text = f"图片OCR结果 [{result['detected_language']}]:\n{result['original']}\n\n译文:\n{result['translated']}"
                            else:
                                # 如果没有文字但有内容描述
                                reply_text = "图片中没有检测到文字，但已分析图片内容。"
                        
                        # 如果有内容描述，添加到回复中
                        if result.get("content_description"):
                            if reply_text:
                                reply_text += "\n\n图片内容描述:\n" + result["content_description"]
                            else:
                                reply_text = "图片内容描述:\n" + result["content_description"]
                    else:
                        reply_text = "无法从图片中提取文字或理解内容。请确保图片清晰可见。"
                    
                    # 记录处理结果到缓存
                    processed_file_ids[file_id] = {
                        "time": time.time(),
                        "result": reply_text
                    }
                    
                    # 发送实际的OCR结果
                    send_message(chat_id, reply_text)
                    
                    # 删除处理中消息
                    if processing_msg_id:
                        delete_result = delete_message(chat_id, processing_msg_id)
                        if not delete_result.get("ok"):
                            logger.warning(f"删除处理中消息失败: message_id={processing_msg_id}")
                    
                    # 删除处理完成消息
                    if complete_msg_id:
                        delete_result = delete_message(chat_id, complete_msg_id)
                        if not delete_result.get("ok"):
                            logger.warning(f"删除处理完成消息失败: message_id={complete_msg_id}")
                else:
                    send_message(chat_id, "下载图片失败，请重试。")
                    # 删除处理中的消息
                    if processing_msg_id:
                        delete_result = delete_message(chat_id, processing_msg_id)
                        if not delete_result.get("ok"):
                            logger.warning(f"删除处理中消息失败: message_id={processing_msg_id}")
            except Exception as e:
                logger.error(f"处理图片时出错: {e}")
                error_msg = f"处理图片时出错，请重试。错误信息: {str(e)[:100]}"
                send_message(chat_id, error_msg)
                # 删除处理中的消息
                if processing_msg_id:
                    delete_result = delete_message(chat_id, processing_msg_id)
                    if not delete_result.get("ok"):
                        logger.warning(f"删除处理中消息失败: message_id={processing_msg_id}")
        else:
            # 删除处理中的消息
            if processing_msg_id:
                delete_result = delete_message(chat_id, processing_msg_id)
                if not delete_result.get("ok"):
                    logger.warning(f"删除处理中消息失败: message_id={processing_msg_id}")
            send_message(chat_id, "获取图片信息失败，请重试。")
    
    else:
        # 处理其他类型的消息
        send_message(chat_id, "请发送文本消息或图片。我只能处理这两种类型的输入。")


def main():
    """主函数"""
    logger.info("启动Telegram翻译机器人...")
    
    # 获取更新的偏移量
    offset = None
    
    while True:
        try:
            # 获取更新
            updates = get_updates(offset)
            
            if updates.get("ok"):
                for update in updates["result"]:
                    update_id = update["update_id"]
                    
                    # 检查是否处理过此更新
                    if update_id in processed_update_ids:
                        logger.info(f"跳过已处理的更新: ID={update_id}")
                        continue
                    
                    # 更新偏移量，以便获取新的更新
                    offset = update_id + 1
                    
                    # 标记为已处理
                    processed_update_ids.add(update_id)
                    
                    # 如果集合太大，移除旧的ID
                    if len(processed_update_ids) > 1000:
                        # 保留最新的500个ID
                        processed_update_ids.clear()
                        processed_update_ids.update(list(processed_update_ids)[-500:])
                    
                    # 处理消息
                    if "message" in update:
                        handle_message(update["message"])
            
            # 短暂暂停，避免过于频繁的请求
            time.sleep(1)
            
        except KeyboardInterrupt:
            logger.info("机器人已停止")
            break
        except requests.exceptions.RequestException as e:
            # 添加重试逻辑
            logger.error(f"网络请求错误: {e}")
            logger.info("等待30秒后重试...")
            time.sleep(30)  # 网络错误后等待较长时间再重试
        except Exception as e:
            logger.error(f"运行时出错: {e}")
            time.sleep(5)  # 一般错误后等待一段时间再重试


if __name__ == "__main__":
    main()