# 使用官方 Python 映像作为基础映像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录内容到工作目录中
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 启动命令
CMD ["python", "main.py"]

