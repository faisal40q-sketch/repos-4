FROM python:3.11-slim

# تثبيت حزم نظام لينكس الكاملة لـ LibreOffice لضمان التعرف على أمر soffice
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-kacst \
    fonts-liberation \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
