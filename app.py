from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import tempfile
import os
import time

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

API_KEY = os.environ.get("CLOUDCONVERT_API_KEY")

@app.route("/convert", methods=["POST"])
def convert():
    try:
        file = request.files["file"]
        target_format = request.form.get("to", "pdf")
        filename = file.filename
        source_format = filename.rsplit(".", 1)[-1].lower()

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        # الخطوة ١: إنشاء Job
        job = requests.post("https://api.cloudconvert.com/v2/jobs", headers=headers, json={
            "tasks": {
                "upload-file": {"operation": "import/upload"},
                "convert-file": {
                    "operation": "convert",
                    "input": "upload-file",
                    "input_format": source_format,
                    "output_format": target_format,
                    "engine": "office" if source_format in ["docx","doc","pptx","xlsx"] else None
                },
                "export-file": {
                    "operation": "export/url",
                    "input": "convert-file"
                }
            }
        }).json()

        # الخطوة ٢: رفع الملف
        upload_task = job["data"]["tasks"][0]
        upload_url = upload_task["result"]["form"]["url"]
        upload_params = upload_task["result"]["form"]["parameters"]
        files_data = {**upload_params, "file": (filename, file.stream, file.content_type)}
        requests.post(upload_url, files=files_data)

        # الخطوة ٣: انتظار التحويل
        job_id = job["data"]["id"]
        for _ in range(30):
            time.sleep(2)
            status = requests.get(f"https://api.cloudconvert.com/v2/jobs/{job_id}", headers=headers).json()
            if status["data"]["status"] == "finished":
                break

        # الخطوة ٤: تحميل الملف
        export_task = [t for t in status["data"]["tasks"] if t["name"] == "export-file"][0]
        download_url = export_task["result"]["files"][0]["url"]
        output_filename = export_task["result"]["files"][0]["filename"]

        file_response = requests.get(download_url)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
        tmp.write(file_response.content)
        tmp.close()

        return send_file(tmp.name, as_attachment=True, download_name=output_filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
