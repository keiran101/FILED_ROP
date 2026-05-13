FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# uploads 和 logs 目录挂载为 volume，不打进镜像
RUN mkdir -p uploads logs

EXPOSE 1158

CMD ["python", "main.py"]
