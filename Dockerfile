FROM python:3.12.14-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir --index-url https://download.pytorch.org/whl/cpu

COPY . .

EXPOSE 3000 7860

CMD ["python", "main.py"]