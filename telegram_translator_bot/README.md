# Telegram 翻译机器人

这是一个简单的 Telegram 翻译机器人，可以将用户发送的任何语言的文本或图片中的文字自动翻译成中文。

## 功能特点

- 自动识别并翻译任何语言的文本到中文
- 从图片中提取文字并翻译成中文
- 简单易用的命令界面
- 支持多种翻译和OCR API

## 环境要求

- Python 3.11（强烈推荐使用此版本以避免兼容性问题）
- Tesseract OCR（用于图片文字识别）
- Telegram Bot API令牌

## 安装步骤

1. 克隆或下载本项目到您的电脑

2. 确保您安装的是Python 3.11版本
   ```bash
   python --version
   ```
   如果不是3.11版本，请下载并安装Python 3.11

3. 安装Python依赖包
   ```bash
   pip install -r requirements.txt
   ```

4. 安装Tesseract OCR
   - Windows: 从[这里](https://github.com/UB-Mannheim/tesseract/wiki)下载并安装
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

5. 创建Telegram机器人并获取API令牌
   - 在Telegram中搜索 `@BotFather` 并开始对话
   - 发送 `/newbot` 命令创建一个新机器人
   - 按照提示设置机器人名称和用户名
   - 复制获取到的API令牌

6. 配置机器人
   - 打开 `config/config.py` 文件
   - 将您的Telegram Bot API令牌填入 `TELEGRAM_BOT_TOKEN`
   - 如需使用其他API，请相应配置相关字段

## 运行机器人

您有三种方式运行机器人：

### 1. 使用简化版HTTP请求方式（推荐）

不依赖于python-telegram-bot库，兼容性最好：

```bash
python src/simple.py
```

### 2. 使用旧版python-telegram-bot API

如果您需要使用其他python-telegram-bot功能：

```bash
# 先安装旧版API
pip install python-telegram-bot==13.15
python src/bot_simple.py
```

### 3. 使用新版python-telegram-bot API

```bash
# 先安装新版API
pip install python-telegram-bot>=20.0
python src/bot.py
```

## 使用方法

1. 在Telegram中搜索并打开您创建的机器人
2. 发送 `/start` 命令开始使用
3. 发送任何语言的文本消息，机器人会自动翻译成中文
4. 发送图片，机器人会提取图片中的文字并翻译成中文

## 故障排除

- 如果遇到模块兼容性问题，请确保使用Python 3.11版本
- 对于OCR相关问题，确保Tesseract已正确安装并且可以在命令行中使用
- 如果翻译API响应慢，可以考虑切换其他翻译服务

## 自定义与扩展

- 如需使用其他翻译API，请在 `src/translator.py` 中添加相应的实现
- 如需使用其他OCR API，请在 `src/ocr.py` 中添加相应的实现

## 部署到服务器

- 完整部署指南请参考 `deployment_guide.md`

## 许可证

MIT

## 作者

[您的名字] 

## 检查Tesseract版本

```bash
tesseract --version
``` 