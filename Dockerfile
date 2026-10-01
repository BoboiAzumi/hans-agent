FROM python:3.12.14-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements --no-cache-dir

COPY . .

EXPOSE 3000 7860

CMD ["python", "main.py"]