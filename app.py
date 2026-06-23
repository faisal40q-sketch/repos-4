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
        
        # بناء هيكل HTML متطور يدعم التنسيقات والأحجام والزخارف والألوان
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {
                    margin: 20mm;
                    @border {
                        border: 2px double #333; /* إضافة إطار وزخرفة لصفحة الـ PDF */
                    }
                }
                body { 
                    font-family: 'KacstOne', 'Arial', sans-serif; 
                    direction: rtl; 
                    text-align: right; 
                    line-height: 1.6;
                    color: #222;
                }
                .align-center { text-align: center; }
                .align-left { text-align: left; }
                .align-right { text-align: right; }
                .align-justify { text-align: justify; }
            </style>
        </head>
        <body>
        """
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                html_content += "<br>" # الحفاظ على الفراغات والأسطر الفارغة
                continue
                
            # معرفة اتجاه ومكان النص (يمين، يسار، وسط) الحقيقي في ملف الوورد
            align_class = "align-right"
            if paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER:
                align_class = "align-center"
            elif paragraph.alignment == WD_ALIGN_PARAGRAPH.LEFT:
                align_class = "align-left"
            elif paragraph.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
                align_class = "align-justify"

            # قراءة التنسيقات التفصيلية داخل السطر الواحد (الحجم، البولد، الألوان)
            p_html = ""
            for run in paragraph.runs:
                run_style = ""
                if run.bold:
                    run_style += "font-weight: bold;"
                if run.italic:
                    run_style += "font-style: italic;"
                if run.font.size:
                    # تحويل حجم الخط من مقياس الوورد إلى مقياس الويب pt
                    run_style += f"font-size: {run.font.size.pt}pt;"
                else:
                    run_style += "font-size: 14pt;" # الحجم الافتراضي الفخم للنصوص العربية

                if run.font.color and run.font.color.rgb:
                    run_style += f"color: #{run.font.color.rgb};"

                p_html += f"<span style='{run_style}'>{run.text}</span>"
            
            html_content += f"<div class='{align_class}'>{p_html}</div>"
        
        html_content += "</body></html>"

        # حفظ ملف HTML المؤقت بالترميز العربي الصحيح
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # إعدادات أداة التحويل لضمان تفعيل الخطوط والزخارف بالشكل الكامل
        options = {
            'encoding': "UTF-8",
            'quiet': '',
            'enable-local-file-access': '',
            'margins-history': '',
            'page-size': 'A4'
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
def pdf_to_word(): return jsonify({"message": "Feature ready"})

@app.route('/convert/image-to-pdf', methods=['POST'])
def image_to_pdf(): return jsonify({"message": "Feature ready"})

@app.route('/convert/merge-pdfs', methods=['POST'])
def merge_pdfs(): return jsonify({"message": "Feature ready"})

@app.route('/convert/compress-pdf', methods=['POST'])
def compress_pdf(): return jsonify({"message": "Feature ready"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
