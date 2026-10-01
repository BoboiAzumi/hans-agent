FROM python:3.12.14-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install torch==2.14.0 torchvision==0.25.0 torchaudio==2.14.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 3000 7860

CMD ["python", "main.py"]