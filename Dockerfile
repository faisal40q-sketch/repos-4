FROM python:3.11-slim

# تثبيت حزم LibreOffice الأساسية والخطوط العربية لضمان جودة وتطابق التنسيق 100%
RUN apt-get update && apt-get install -y \
    libreoffice-writer \
    libreoffice-java-common \
    fonts-kacst \
    fonts-liberation \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
