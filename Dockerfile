FROM python:3.11-slim

# تحديث مستودعات النظام وتثبيت أداة wkhtmltopdf مع الخطوط العربية الرسمية الأساسية لضمان تحويل النصوص بشكل صحيح
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    fonts-kacst \
    fonts-liberation \
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
