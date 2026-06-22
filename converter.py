import os
import subprocess
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image

class DocumentConverterEngine:
    def __init__(self):
        pass

    # 1. Word to PDF / Excel to PDF / PowerPoint to PDF
    # نستخدم LibreOffice لأنه الأضمن والأقوى عالمياً في الحفاظ على تنسيق اللغة العربية
    def office_to_pdf(self, input_file_path, output_dir):
        try:
            # الأمر يقوم بتحويل أي ملف أوفيس إلى PDF بدون واجهة رسومية وبشكل صامت
            command = [
                'libreoffice', '--headless', '--convert-to', 'pdf',
                '--outdir', output_dir, input_file_path
            ]
            # لو كنت تستخدم ويندوز، تأكد من كتابة المسار الكامل لـ soffice.exe إذا لم يعمل الأمر المباشر
            subprocess.run(command, check=True)
            
            # الحصول على اسم الملف الجديد بامتداد pdf
            base_name = os.path.splitext(os.path.basename(input_file_path))[0]
            output_file_path = os.path.join(output_dir, f"{base_name}.pdf")
            return {"status": "success", "file_path": output_file_path}
        except Exception as e:
            return {"status": "error", "message": f"Office to PDF failed: {str(e)}"}

    # 2. PDF to Word
    # تحويل PDF العربي إلى Word تحدي كبير، الحل الأفضل هو تحويل الصفحات لصور ثم تضمينها أو استخدام LibreOffice عكسياً
    def pdf_to_word(self, input_pdf_path, output_dir):
        try:
            base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
            output_file_path = os.path.join(output_dir, f"{base_name}.docx")
            
            # استدعاء LibreOffice لتحويل الـ PDF إلى Docx (يحافظ على النصوص العربية والاتجاهات بشكل ممتاز)
            command = [
                'libreoffice', '--headless', '--convert-to', 'docx',
                '--outdir', output_dir, input_pdf_path
            ]
            subprocess.run(command, check=True)
            return {"status": "success", "file_path": output_file_path}
        except Exception as e:
            return {"status": "error", "message": f"PDF to Word failed: {str(e)}"}

    # 3. Image to PDF
    def image_to_pdf(self, input_image_path, output_pdf_path):
        try:
            image = Image.open(input_image_path)
            # التأكد من تحويل الصورة إلى صيغة RGB قبل الحفظ كـ PDF
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            image.save(output_pdf_path, "PDF")
            return {"status": "success", "file_path": output_pdf_path}
        except Exception as e:
            return {"status": "error", "message": f"Image to PDF failed: {str(e)}"}

    # 4. PDF to Image
    # يقوم بتحويل كل صفحة في الـ PDF إلى صورة منفصلة داخل مجلد مخصص
    def pdf_to_image(self, input_pdf_path, output_dir, img_format="JPEG"):
        try:
            # ملاحظة: تحتاج لتثبيت أداة poppler على النظام لتعمل هذه المكتبة بنجاح
            pages = convert_from_path(input_pdf_path, dpi=200)
            base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
            generated_images = []
            
            for i, page in enumerate(pages):
                image_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.{img_format.lower()}")
                page.save(image_path, img_format)
                generated_images.append(image_path)
                
            return {"status": "success", "file_paths": generated_images}
        except Exception as e:
            return {"status": "error", "message": f"PDF to Image failed: {str(e)}"}

    # 5. Merge PDF (دمج عدة ملفات PDF في ملف واحد)
    def merge_pdfs(self, list_of_pdf_paths, output_pdf_path):
        try:
            merger = PdfMerger()
            for pdf in list_of_pdf_paths:
                merger.append(pdf)
            merger.write(output_pdf_path)
            merger.close()
            return {"status": "success", "file_path": output_pdf_path}
        except Exception as e:
            return {"status": "error", "message": f"Merge PDF failed: {str(e)}"}

    # 6. Split PDF (تقسيم ملف PDF إلى صفحات منفصلة أو استخراج صفحات معينة)
    def split_pdf(self, input_pdf_path, output_dir):
        try:
            reader = PdfReader(input_pdf_path)
            base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
            generated_pdfs = []
            
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                output_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
                with open(output_path, "wb") as f:
                    writer.write(f)
                generated_pdfs.append(output_path)
                
            return {"status": "success", "file_paths": generated_pdfs}
        except Exception as e:
            return {"status": "error", "message": f"Split PDF failed: {str(e)}"}

    # 7. Compress PDF (تقليل حجم ملف PDF عبر تقليل جودة الصور والبيانات الزائدة)
    def compress_pdf(self, input_pdf_path, output_pdf_path):
        try:
            reader = PdfReader(input_pdf_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                # ضغط الصور داخل الصفحة إن وجدت دون التأثير على النصوص العربية
                page.compress_content_streams() 
                writer.add_page(page)
                
            with open(output_pdf_path, "wb") as f:
                writer.write(f)
            return {"status": "success", "file_path": output_pdf_path}
        except Exception as e:
            return {"status": "error", "message": f"Compress PDF failed: {str(e)}"}

# =====================================================================
# مثال على كيفية تشغيل واستدعاء الكود (للتجربة والاختبار المحلي):
# =====================================================================
if __name__ == "__main__":
    engine = DocumentConverterEngine()
    
    # تأكد من إنشاء مجلد اسمه 'test_files' بجانب السكربت لتجربة الأكواد
    output_directory = "./test_files"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
    print("المحرك جاهز الآن للربط والعمل!")
    # لاستدعاء أي دالة مستقبلاً، مثال:
    # result = engine.office_to_pdf("my_word_doc.docx", output_directory)
    # print(result)