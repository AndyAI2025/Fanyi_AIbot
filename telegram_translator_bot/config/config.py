#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件，用于存储API密钥和其他设置
"""

# Telegram Bot API令牌（需要从BotFather获取）
# 请将"YOUR_TELEGRAM_BOT_TOKEN"替换为您从BotFather获取的实际令牌
# 获取步骤：
# 1. 在Telegram中搜索 @BotFather 并开始对话
# 2. 发送 /newbot 命令
# 3. 按照提示设置机器人名称和用户名
# 4. 复制BotFather提供的API令牌到这里
TELEGRAM_BOT_TOKEN = "7843869894:AAGzc9u9lVEHf6kSIQOXLmbW7Om3E6idH6c"

# 翻译API设置（Google Translate无需API密钥，此处仅作为示例）
TRANSLATION_API = "google"  # 使用哪种翻译API：'google'或'deepl'等
DEEPL_API_KEY = "YOUR_DEEPL_API_KEY"  # 如果使用DeepL需要填写

# OCR（光学字符识别）API设置
OCR_API = "tesseract"  # 使用哪种OCR: 'tesseract'（本地）或'google_vision'等
GOOGLE_VISION_API_KEY = "YOUR_GOOGLE_VISION_API_KEY"  # 如果使用Google Vision API需要填写

# 目标语言（中文）
TARGET_LANGUAGE = "zh-CN"

# 临时文件存储路径（用于存储用户发送的图片等）
TEMP_FOLDER = "./temp" 