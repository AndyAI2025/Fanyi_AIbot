# Telegram翻译机器人部署指南（阿里云）

本指南将引导您如何将Telegram翻译机器人部署到阿里云服务器上。适合没有编程和开发经验的新手用户。

## 前提条件

1. 一个已配置好的阿里云ECS服务器（Linux系统，推荐Ubuntu或CentOS）
2. 服务器已开放对外网络连接
3. Telegram Bot API令牌（从BotFather获取）

## 步骤1：连接到您的阿里云服务器

1. 使用SSH客户端连接到您的服务器
   - Windows用户可以使用PuTTY或Windows Terminal
   - Mac/Linux用户可以使用Terminal

2. 使用您的服务器登录凭据登录
   ```
   ssh username@your_server_ip
   ```

## 步骤2：安装必要的软件

1. 更新系统包
   ```bash
   sudo apt update && sudo apt upgrade -y   # Ubuntu/Debian
   # 或
   sudo yum update -y                        # CentOS/RHEL
   ```

2. 安装Python和其他必要的工具
   ```bash
   # Ubuntu/Debian
   sudo apt install -y python3 python3-pip git tesseract-ocr

   # CentOS/RHEL
   sudo yum install -y python3 python3-pip git
   # 对于CentOS，需要额外步骤安装Tesseract，请参考Tesseract官方文档
   ```

## 步骤3：下载项目到服务器

1. 克隆或上传项目到服务器
   ```bash
   git clone https://github.com/yourusername/telegram_translator_bot.git
   # 或者通过SFTP/SCP上传您的项目文件
   ```

2. 进入项目目录
   ```bash
   cd telegram_translator_bot
   ```

## 步骤4：配置项目

1. 安装Python依赖
   ```bash
   pip3 install -r requirements.txt
   ```

2. 配置Bot Token
   ```bash
   # 使用nano或vim编辑配置文件
   nano config/config.py
   ```

3. 修改配置文件中的TELEGRAM_BOT_TOKEN为您的实际Token
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_ACTUAL_BOT_TOKEN"
   ```

4. 保存文件并退出编辑器
   - 在nano中：按`Ctrl+O`保存，然后按`Ctrl+X`退出
   - 在vim中：按`Esc`，然后输入`:wq`并按Enter

## 步骤5：后台运行机器人

为了让机器人在您关闭SSH连接后仍然运行，我们需要使用`nohup`或`screen`命令：

1. 使用nohup（简单方法）
   ```bash
   # 创建logs目录
   mkdir -p logs
   
   # 后台运行机器人
   nohup python3 src/bot.py > logs/bot.log 2>&1 &
   
   # 记下进程ID（后续如需停止机器人使用）
   echo $! > bot.pid
   ```

2. 或使用screen（更灵活的方法）
   ```bash
   # 安装screen
   sudo apt install screen   # Ubuntu/Debian
   # 或
   sudo yum install screen   # CentOS/RHEL
   
   # 创建新的screen会话
   screen -S telegram_bot
   
   # 在screen会话中启动机器人
   python3 src/bot.py
   
   # 按Ctrl+A，然后按D来分离screen会话（机器人将继续在后台运行）
   ```

## 步骤6：验证机器人是否正常运行

1. 在Telegram中打开您的机器人
2. 发送 `/start` 命令
3. 如果机器人响应，说明部署成功！

## 管理您的机器人

### 查看日志
```bash
# 如果使用nohup
tail -f logs/bot.log

# 如果使用screen
screen -r telegram_bot  # 重新连接到screen会话
# 按Ctrl+A，然后按D再次分离
```

### 停止机器人
```bash
# 如果使用nohup
kill $(cat bot.pid)

# 如果使用screen
screen -r telegram_bot  # 重新连接到screen会话
# 在会话中按Ctrl+C停止程序
# 输入exit退出screen会话
```

### 设置开机自启动

1. 创建systemd服务文件
   ```bash
   sudo nano /etc/systemd/system/telegram_bot.service
   ```

2. 添加以下内容（记得修改路径和用户名）
   ```
   [Unit]
   Description=Telegram Translator Bot
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/telegram_translator_bot
   ExecStart=/usr/bin/python3 /path/to/telegram_translator_bot/src/bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. 启用并启动服务
   ```bash
   sudo systemctl enable telegram_bot
   sudo systemctl start telegram_bot
   ```

4. 检查服务状态
   ```bash
   sudo systemctl status telegram_bot
   ```

## 常见问题解决

1. **机器人不响应**
   - 检查日志文件中是否有错误信息
   - 确认Telegram Bot Token是否正确
   - 检查服务器网络连接

2. **OCR功能不工作**
   - 确认已正确安装Tesseract OCR
   - 检查日志中的错误信息

3. **机器人意外停止**
   - 检查系统资源使用情况（CPU、内存）
   - 查看日志文件以了解停止原因
   - 考虑增加服务器资源

## 后续维护

- 定期更新系统和依赖包
  ```bash
  sudo apt update && sudo apt upgrade -y
  pip3 install --upgrade -r requirements.txt
  ```

- 监控服务器性能和日志
- 定期备份配置文件和重要数据

---

如有任何问题，请随时查阅相关文档或寻求帮助。 