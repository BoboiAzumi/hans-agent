FROM python:3.12.14-slim

WORKDIR /app

COPY requirements-cpu.txt .

RUN pip install -r requirements-cpu.txt --no-cache-dir

COPY . .

EXPOSE 3000 7860

CMD ["python", "main.py"]