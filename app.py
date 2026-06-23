import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from pdf2docx import Converter
import pdfkit

app = Flask(__name__)
CORS(app)

# 1. تحويل Word إلى PDF
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
        doc = Document(docx_path)
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page { size: A4; margin: 15mm; }
                body { 
                    font-family: 'KacstOne', 'Arial', sans-serif; 
                    direction: rtl; 
                    text-align: right; 
                    line-height: 1.8;
                    font-size: 14pt;
                }
                .align-center { text-align: center; }
                .align-left { text-align: left; }
                .align-right { text-align: right; }
                .bold { font-weight: bold; }
            </style>
        </head>
        <body>
        """
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                html_content += "<br>"
                continue
            
            align_class = "align-right"
            if paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                align_class = "align-center"
            elif paragraph.alignment == WD_ALIGN_PARAGRAPH.LEFT:
                align_class = "align-left"

            p_html = ""
            for run in paragraph.runs:
                style = f"font-size: {run.font.size.pt if run.font.size else 14}pt;"
                if run.font.color and run.font.color.rgb:
                    style += f"color: #{run.font.color.rgb};"
                
                cls = "class='bold'" if run.bold else ""
                p_html += f"<span {cls} style='{style}'>{run.text}</span>"
            
            html_content += f"<div class='{align_class}'>{p_html}</div>"
        
        html_content += "</body></html>"

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        options = {'encoding': "UTF-8", 'quiet': '', 'enable-local-file-access': ''}
        pdfkit.from_file(html_path, pdf_path, options=options)
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        for path in [docx_path, html_path]:
            if os.path.exists(path): os.remove(path)

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
