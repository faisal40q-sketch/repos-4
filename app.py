from xhtml2pdf import pisa

# 1. اكتب النص أو كود الـ HTML الذي تريد تحويله إلى PDF
html_content = """
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; font-size: 14px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>مرحباً بك في مستند الـ PDF الجديد</h1>
    <p>تم إنشاء هذا الملف بنجاح باستخدام مكتبة xhtml2pdf المستقرة.</p>
</body>
</html>
"""

# 2. اسم ملف الـ PDF النهائي الذي سيتم حفظه
output_pdf_name = "output_document.pdf"

# 3. كود فتح الملف وتحويل الـ HTML إلى PDF تلقائياً
with open(output_pdf_name, "w+b") as result_file:
    pisa_status = pisa.CreatePDF(html_content, dest=result_file)

# 4. التحقق من نجاح العملية
if not pisa_status.err:
    print("تم إنشاء ملف الـ PDF وتعديل الكود بنجاح!")
else:
    print("حدث خطأ أثناء إنشاء الملف.")
