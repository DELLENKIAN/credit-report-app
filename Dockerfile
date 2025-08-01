FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
