import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from docx import Document
from pypdf import PdfMerger, PdfReader, PdfWriter
from pdf2docx import Converter

app = Flask(__name__)
CORS(app)

# 1. تحويل Word إلى PDF (نسخة محسنة التنسيق)
@app.route('/convert/office-to-pdf', methods=['POST'])
def office_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    docx_path = "temp.docx"
    pdf_path = "output.pdf"
    file.save(docx_path)

    try:
        # هنا نستخدم الطريقة المباشرة لإنشاء الـ PDF للحفاظ على الهوامش والخطوط قدر الإمكان
        import pdfkit
        html_path = "temp.html"
        doc = Document(docx_path)
        
        html_content = "<html><head><meta charset='utf-8'><style>body{font-family:'Arial','sans-serif';direction:rtl;text-align:right;padding:30px;line-height:1.6;} p{margin-bottom:10px;}</style></head><body>"
        for p in doc.paragraphs:
            if p.text.strip():
                # محاولة الحفاظ على التوسيط واليمين
                align = "center" if p.alignment == 1 else "right"
                html_content += f"<p style='text-align:{align};'>{p.text}</p>"
        html_content += "</body></html>"

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        options = {'encoding': "UTF-8", 'quiet': '', 'page-size': 'A4'}
        pdfkit.from_file(html_path, pdf_path, options=options)
        
        if os.path.exists(html_path): os.remove(html_path)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(docx_path): os.remove(docx_path)

# 2. تحويل PDF إلى Word (شغال رسميًا الحين!)
@app.route('/convert/pdf-to-word', methods=['POST'])
def pdf_to_word():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    pdf_path = "temp.pdf"
    docx_path = "output.docx"
    file.save(pdf_path)

    try:
        # تشغيل ماكينة تحويل الـ PDF وعكسه إلى ملف وورد مفتوح بالتنسيق
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
    if not files:
        return jsonify({"error": "No files provided"}), 400
    
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
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    pdf_path = "temp_c.pdf"
    output_path = "compressed.pdf"
    file.save(pdf_path)

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams() # ضغط محتوى الصفحة تلقائيًا
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(pdf_path): os.remove(pdf_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
