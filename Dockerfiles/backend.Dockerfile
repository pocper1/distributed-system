# 使用官方 Python 3.10 映像作為基底
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴 (例如 psycopg2 需要的 libpq-dev)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 複製並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式程式碼
COPY . .

# 暴露應用程式運行的端口
EXPOSE 8000

# 設定啟動指令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
