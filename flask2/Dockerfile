# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录的所有文件到容器中的 /app 目录
COPY . /app

# 升级 pip
RUN pip install --upgrade pip

# 安装 Flask 及其它依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 暴露 Flask 默认端口
EXPOSE 5000