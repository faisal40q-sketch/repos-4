FROM python:3.11-slim

# تثبيت أداة wkhtmltopdf والخطوط العربية الأساسية في ثوانٍ بدون مشاكل
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    fonts-kacst \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
