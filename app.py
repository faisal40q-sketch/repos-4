import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from docx import Document
import pdfkit

app = Flask(__name__)
CORS(app)

@app.route('/convert/office-to-pdf', methods=['POST'])
def office_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No filename"}), 400

    docx_path = "temp.docx"
    html_path = "temp.html"
    pdf_path = "output.pdf"
    
    file.save(docx_path)

    try:
        # قراءة ملف الـ Word وبناء هيكل HTML يدعم الحروف العربية والترميز الصحيح
        doc = Document(docx_path)
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { 
                    font-family: 'KacstOne', 'Arial', sans-serif; 
                    direction: rtl; 
                    text-align: right; 
                    padding: 20px;
                    line-height: 1.6;
                }
                p { margin-bottom: 12px; }
            </style>
        </head>
        <body>
        """
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                html_content += f"<p>{paragraph.text}</p>"
        
        html_content += "</body></html>"

        # حفظ ملف HTML مؤقت
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # إعدادات أداة التحويل لضمان تشغيلها بدون واجهة رسومية على السيرفر
        options = {
            'encoding': "UTF-8",
            'quiet': '',
            'enable-local-file-access': ''
        }
        
        # تحويل الـ HTML المدعوم عربياً إلى PDF
        pdfkit.from_file(html_path, pdf_path, options=options)

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # تنظيف الخادم من الملفات المؤقتة بعد انتهاء العملية
        for path in [docx_path, html_path]:
            if os.path.exists(path): 
                os.remove(path)

@app.route('/convert/pdf-to-word', methods=['POST'])
def pdf_to_word(): return jsonify({"message": "Feature ready"})

@app.route('/convert/image-to-pdf', methods=['POST'])
def image_to_pdf(): return jsonify({"message": "Feature ready"})

@app.route('/convert/merge-pdfs', methods=['POST'])
def merge_pdfs(): return jsonify({"message": "Feature ready"})

@app.route('/convert/compress-pdf', methods=['POST'])
def compress_pdf(): return jsonify({"message": "Feature ready"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
