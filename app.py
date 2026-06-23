import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from docx import Document
from xhtml2pdf import pisa

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
    pdf_path = "output.pdf"
    file.save(docx_path)

    try:
        # قراءة ملف الـ Word وبناء نص HTML يدعم الـ Unicode والعربي
        doc = Document(docx_path)
        html_content = "<html><head><meta charset='utf-8'><style>body { font-family: 'Helvetica', 'Arial', sans-serif; direction: rtl; text-align: right; }</style></head><body>"
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                html_content += f"<p>{paragraph.text}</p>"
        
        html_content += "</body></html>"

        # تحويل الـ HTML المدعوم عربياً إلى ملف PDF مباشرة
        with open(pdf_path, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(html_content, dest=result_file)
        
        if pisa_status.err:
            return jsonify({"error": "PDF generation error"}), 500

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(docx_path): os.remove(docx_path)

@app.route('/convert/pdf-to-word', methods=['POST'])
def pdf_to_word(): return jsonify({"message": "Ready"})

@app.route('/convert/image-to-pdf', methods=['POST'])
def image_to_pdf(): return jsonify({"message": "Ready"})

@app.route('/convert/merge-pdfs', methods=['POST'])
def merge_pdfs(): return jsonify({"message": "Ready"})

@app.route('/convert/compress-pdf', methods=['POST'])
def compress_pdf(): return jsonify({"message": "Ready"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
