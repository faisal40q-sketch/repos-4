FROM python:3.11-slim

# تحديث النظام وتثبيت LibreOffice مع الحزم الأساسية والخطوط العربية
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    fonts-kacst \
    fonts-liberation \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع إلى السيرفر
COPY . .

# أمر تشغيل السيرفر باستخدام بورت 10000 الافتراضي لـ Render
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
