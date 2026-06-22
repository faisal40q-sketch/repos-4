# استخدام نسخة بايثون المستقرة والمدعومة
FROM python:3.11-slim

# تثبيت LibreOffice وحزم الخطوط الأساسية لدعم اللغة العربية
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-dejavu \
    fonts-liberation \
    ttf-mscorefonts-installer \
    && apt-get clean \
    rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع إلى السيرفر
COPY . .

# تحديد المنفذ وتشغيل السيرفر باستخدام gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
