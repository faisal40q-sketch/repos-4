## استخدام نسخة بايثون المستقرة والمدعومة
FROM python:3.11-slim

# تثبيت LibreOffice والخطوط العربية لتجنب مشكلة المربعات أو الرموز الغريبة
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-kacst \
    fonts-liberation \
    fonts-dejavu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# نسخ ملف المكتبات أولاً لتسريع عملية البناء
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع
COPY . .

# المنفذ الافتراضي لـ Render
EXPOSE 10000

# أمر تشغيل السيرفر باستخدام gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
