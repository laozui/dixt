FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=7860

WORKDIR /app

# 安装基础工具与依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 下载 x-tunnel-linux (AMD64)
RUN curl -fsSL -o /app/x-tunnel https://www.baipiao.eu.org/xtunnel/x-tunnel-linux-amd64 \
    && chmod +x /app/x-tunnel

# 下载 cloudflared (AMD64)
RUN curl -fsSL -o /app/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
    && chmod +x /app/cloudflared

# 复制业务代码与依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# 暴露端口 (Render 默认 10000, 兼容其它平台)
EXPOSE 10000 7860 8080

ENTRYPOINT ["/app/entrypoint.sh"]
