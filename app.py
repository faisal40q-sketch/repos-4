import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
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
        doc = Document(docx_path)
        
        # قالب HTML فخم ومحسّن لحل مشاكل تداخل الخطوط والتنسيقات العربية
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {
                    size: A4;
                    margin: 15mm;
                }
                body { 
                    font-family: 'KacstOne', 'Arial', 'DejaVu Sans', sans-serif; 
                    direction: rtl; 
                    text-align: right; 
                    line-height: 1.8;
                    color: #111;
                    font-size: 14pt;
                    padding: 10px;
                }
                /* إطار وزخرفة عامة تحاكي الهوامش الجانبية الجمالية */
                .page-border {
                    border: 3px double #444;
                    padding: 20px;
                    min-height: 95%;
                }
                .align-center { text-align: center; }
                .align-left { text-align: left; }
                .align-right { text-align: right; }
                .align-justify { text-align: justify; }
                
                .bold { font-weight: bold; }
                .italic { font-style: italic; }
            </style>
        </head>
        <body>
            <div class="page-border">
        """
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                html_content += "<br>"
                continue
                
            # تحديد المحاذاة بدقة
            align_class = "align-right"
            if paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                align_class = "align-center"
            elif paragraph.alignment == WD_ALIGN_PARAGRAPH.LEFT:
                align_class = "align-left"
            elif paragraph.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
                align_class = "align-justify"

            # تجميع النص كاملاً في الفقرة لتجنب تقطيع الحروف العربية
            p_html = ""
            for run in paragraph.runs:
                style_classes = []
                run_style = ""
                
                if run.bold:
                    style_classes.append("bold")
                if run.italic:
                    style_classes.append("italic")
                if run.font.size:
                    run_style += f"font-size: {run.font.size.pt}pt;"
                if run.font.color and run.font.color.rgb:
                    run_style += f"color: #{run.font.color.rgb};"

                class_attr = f"class='{' '.join(style_classes)}'" if style_classes else ""
                style_attr = f"style='{run_style}'" if run_style else ""
                
                p_html += f"<span {class_attr} {style_attr}>{run.text}</span>"
            
            html_content += f"<div class='{align_class}'>{p_html}</div>"
        
        html_content += """
            </div>
        </body>
        </html>
        """

        # حفظ ملف HTML المؤقت
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        options = {
            'encoding': "UTF-8",
            'quiet': '',
            'enable-local-file-access': '',
            'margin-top': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'margin-right': '0mm'
        }
        
        pdfkit.from_file(html_path, pdf_path, options=options)

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        for path in [docx_path, html_path]:
            if os.path.exists(path): 
                os.remove(path)

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
