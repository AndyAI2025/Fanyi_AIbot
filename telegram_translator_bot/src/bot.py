#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram机器人主模块，使用python-telegram-bot库实现机器人功能
整合翻译和OCR功能
"""

import os
import sys
import logging
import tempfile
import platform
import time
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 检查Python版本
python_version = platform.python_version()
if not python_version.startswith('3.11'):
    print(f"警告: 当前Python版本为 {python_version}，推荐使用Python 3.11以确保最佳兼容性")
    print("您可以继续运行，但可能会遇到兼容性问题")
    time.sleep(2)  # 暂停2秒，让用户看到警告信息

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import TELEGRAM_BOT_TOKEN, TEMP_FOLDER
from src.translator import TextTranslator
from src.ocr import ImageOCR

# 配置日志
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/start命令"""
    welcome_message = """
欢迎使用翻译机器人！

我可以帮你将任何语言翻译成中文，只需发送文本消息或图片给我。

- 发送文字消息：我会自动检测语言并翻译成中文
- 发送图片：我会识别图片中的文字并翻译成中文

使用 /help 查看更多帮助信息。
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/help命令"""
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
    await update.message.reply_text(help_message)


async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理文本消息并翻译"""
    user_text = update.message.text
    
    # 记录日志
    logger.info(f"收到来自 {update.effective_user.first_name} 的文本: {user_text[:20]}...")
    
    # 调用翻译功能
    result = translator.translate_to_chinese(user_text)
    
    # 准备回复消息
    if result["original"] == result["translated"]:
        # 如果原文和译文相同（可能已经是中文）
        reply_text = f"文本已经是中文，无需翻译。"
    else:
        # 显示原文和译文
        reply_text = f"原文 [{result['detected_language']}]:\n{result['original']}\n\n译文:\n{result['translated']}"
    
    # 发送回复
    await update.message.reply_text(reply_text)


async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理图片消息，提取文字并翻译"""
    # 告知用户正在处理
    processing_message = await update.message.reply_text("正在处理图片，请稍等...")
    
    try:
        # 获取图片文件
        photo_file = await update.message.photo[-1].get_file()
        
        # 创建临时文件保存图片
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=TEMP_FOLDER) as temp_file:
            temp_path = temp_file.name
        
        # 下载图片到临时文件
        await photo_file.download_to_drive(destination=temp_path)
        
        # 记录日志
        logger.info(f"收到来自 {update.effective_user.first_name} 的图片，保存至 {temp_path}")
        
        # 使用OCR处理图片
        result = ocr_engine.process_image_to_text(temp_path)
        
        # 删除临时文件
        os.unlink(temp_path)
        
        # 准备回复消息
        if result["success"]:
            if result["original"] == result["translated"]:
                # 如果原文和译文相同（可能已经是中文）
                reply_text = f"图片中的文字已经是中文，无需翻译。\n\n文字内容:\n{result['original']}"
            else:
                # 显示原文和译文
                reply_text = f"图片OCR结果 [{result['detected_language']}]:\n{result['original']}\n\n译文:\n{result['translated']}"
        else:
            reply_text = "无法从图片中提取文字。请确保图片中包含清晰的文本内容。"
        
        # 发送回复并删除处理中消息
        await processing_message.delete()
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        logger.error(f"处理图片时出错: {str(e)}")
        await processing_message.edit_text("处理图片时出错，请重试或发送其他图片。")


async def handle_other_types(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理其他类型的消息（非文本或图片）"""
    await update.message.reply_text("请发送文本消息或图片。我只能处理这两种类型的输入。")


def main() -> None:
    """启动机器人"""
    # 检查API令牌
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("错误: 请在config.py中设置您的Telegram Bot Token")
        return
    
    # 创建应用，禁用job队列以避免pytz问题
    builder = Application.builder().token(TELEGRAM_BOT_TOKEN)
    builder.job_queue = None  # 禁用JobQueue
    application = builder.build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # 添加消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    application.add_handler(MessageHandler(filters.PHOTO, process_image))
    application.add_handler(MessageHandler(~filters.TEXT & ~filters.PHOTO, handle_other_types))
    
    # 启动机器人
    print("启动翻译机器人...")
    application.run_polling()


if __name__ == "__main__":
    main() 
