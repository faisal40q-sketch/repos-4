import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from converter import DocumentConverterEngine

app = Flask(__name__)
CORS(app)  # للسماح لـ Lovable بالاتصال بالسيرفر بدون مشاكل أمنية

UPLOAD_FOLDER = '/tmp/uploads' if os.name != 'nt' else './uploads'
OUTPUT_FOLDER = '/tmp/outputs' if os.name != 'nt' else './outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

engine = DocumentConverterEngine()

# 1. Word / Excel / PPT to PDF
@app.route('/convert/office-to-pdf', methods=['POST'])
def office_to_pdf():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    result = engine.office_to_pdf(input_path, OUTPUT_FOLDER)
    if result["status"] == "success":
        return send_file(result["file_path"], as_attachment=True)
    return jsonify({"error": result["message"]}), 500

# 2. PDF to Word
@app.route('/convert/pdf-to-word', methods=['POST'])
def pdf_to_word():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    result = engine.pdf_to_word(input_path, OUTPUT_FOLDER)
    if result["status"] == "success":
        return send_file(result["file_path"], as_attachment=True)
    return jsonify({"error": result["message"]}), 500

# 3. Image to PDF
@app.route('/convert/image-to-pdf', methods=['POST'])
def image_to_pdf():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    base_name = os.path.splitext(file.filename)[0]
    output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.pdf")
    result = engine.image_to_pdf(input_path, output_path)
    if result["status"] == "success":
        return send_file(result["file_path"], as_attachment=True)
    return jsonify({"error": result["message"]}), 500

# 4. PDF to Image
@app.route('/convert/pdf-to-image', methods=['POST'])
def pdf_to_image():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    result = engine.pdf_to_image(input_path, OUTPUT_FOLDER)
    if result["status"] == "success":
        # بما أنها صور متعددة، نعيد قائمة بمسارات الصور أو يمكنك ضغطها في ملف ZIP لاحقاً
        return jsonify({"status": "success", "files": result["file_paths"]})
    return jsonify({"error": result["message"]}), 500

# 5. Merge PDFs
@app.route('/convert/merge-pdfs', methods=['POST'])
def merge_pdfs():
    files = request.files.getlist('files')
    if not files: return jsonify({"error": "No files"}), 400
    paths = []
    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        paths.append(path)
    output_path = os.path.join(OUTPUT_FOLDER, "merged_document.pdf")
    result = engine.merge_pdfs(paths, output_path)
    if result["status"] == "success":
        return send_file(result["file_path"], as_attachment=True)
    return jsonify({"error": result["message"]}), 500

# 6. Split PDF
@app.route('/convert/split-pdf', methods=['POST'])
def split_pdf():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    result = engine.split_pdf(input_path, OUTPUT_FOLDER)
    if result["status"] == "success":
        return jsonify({"status": "success", "files": result["file_paths"]})
    return jsonify({"error": result["message"]}), 500

# 7. Compress PDF
@app.route('/convert/compress-pdf', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)
    output_path = os.path.join(OUTPUT_FOLDER, f"compressed_{file.filename}")
    result = engine.compress_pdf(input_path, output_path)
    if result["status"] == "success":
        return send_file(result["file_path"], as_attachment=True)
    return jsonify({"error": result["message"]}), 500

if __name__ == '__main__':
    # السيرفر سيعمل على المنفذ 5000 بشكل افتراضي
    app.run(host='0.0.0.0', port=5000, debug=True)