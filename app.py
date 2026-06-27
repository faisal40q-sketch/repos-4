import os
import subprocess
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2docx import Converter

app = Flask(__name__)
CORS(app)

# 1. تحويل Word إلى PDF (باستخدام المسار الصريح والمباشر لـ LibreOffice)
@app.route('/convert/office-to-pdf', methods=['POST'])
def office_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No filename"}), 400

    docx_path = "temp.docx"
    file.save(docx_path)

    # تحديد المسارات المتوقعة لـ soffice في خوادم لينكس لضمان تشغيله حتماً
    soffice_paths = [
        '/usr/bin/soffice',
        '/usr/lib/libreoffice/program/soffice',
        'soffice' # كخيار أخير
    ]
    
    chosen_path = None
    for path in soffice_paths:
        if os.path.exists(path) or path == 'soffice':
            chosen_path = path
            break

    try:
        # أمر التشغيل بالمسار المباشر والصريح
        cmd = [
            chosen_path,
            '--headless',
            '--convert-to', 'pdf',
            docx_path
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        pdf_path = "temp.pdf"
        
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, download_name="converted.pdf")
        else:
            # طباعة الخطأ بالتفصيل مع المسار المستخدم إذا فشل
            return jsonify({"error": f"Conversion failed using {chosen_path}: {result.stderr}"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(docx_path): os.remove(docx_path)
        if os.path.exists("temp.pdf"): os.remove("temp.pdf")

# 2. تحويل PDF إلى Word
@app.route('/convert/pdf-to-word', methods=['POST'])
def pdf_to_word():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    pdf_path = "temp.pdf"
    docx_path = "output.docx"
    file.save(pdf_path)

    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        return send_file(docx_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(pdf_path): os.remove(pdf_path)

# 3. دمج ملفات PDF
@app.route('/convert/merge-pdfs', methods=['POST'])
def merge_pdfs():
    files = request.files.getlist('files')
    if not files: return jsonify({"error": "No files"}), 400
    
    merger = PdfMerger()
    temp_paths = []
    try:
        for i, file in enumerate(files):
            path = f"temp_{i}.pdf"
            file.save(path)
            temp_paths.append(path)
            merger.append(path)
        
        output_path = "merged.pdf"
        merger.write(output_path)
        merger.close()
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        for path in temp_paths:
            if os.path.exists(path): os.remove(path)

# 4. ضغط ملف PDF
@app.route('/convert/compress-pdf', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    
    file = request.files['file']
    pdf_path = "temp_c.pdf"
    output_path = "compressed.pdf"
    file.save(pdf_path)

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(pdf_path): os.remove(pdf_path)

@app.route('/convert/image-to-pdf', methods=['POST'])
def image_to_pdf(): return jsonify({"message": "Ready"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
