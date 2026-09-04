"""
app.py
------
PackSure backend — Flask RESTful API.

Endpoints:
  POST /api/scan        -> upload a package image, run the full pipeline
  GET  /api/history      -> list previous scans
  GET  /api/report/<id>  -> download the PDF report for a scan
  GET  /api/health       -> health check
"""
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from ocr_engine import run_ocr, get_reader
from extractor import extract_fields
from rule_engine import check_compliance
from report_generator import generate_report
from database import init_db, db, ScanRecord

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
ALLOWED_EXT = {"png", "jpg", "jpeg", "webp", "bmp"}

app = Flask(__name__)
CORS(app)
init_db(app)

# Pre-warm EasyOCR model into RAM on server startup for instant scan responses
try:
    get_reader()
except Exception as _err:
    print(f"[App] Reader pre-warm warning: {_err}")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "PackSure backend"})


@app.route("/api/scan", methods=["POST"])
def scan():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided (field name 'image')"}), 400

    file = request.files["image"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing image file"}), 400

    safe_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename)}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    file.save(save_path)

    try:
        ocr_result = run_ocr(save_path)
        fields = extract_fields(
            ocr_result["raw_text"],
            lines_with_boxes=ocr_result.get("lines_with_boxes"),
            word_boxes=ocr_result.get("word_boxes"),
        )
        compliance = check_compliance(fields, ocr_result["avg_confidence"])
        report_path = generate_report(compliance, fields, safe_name, REPORT_DIR)
    except Exception as e:
        return jsonify({"error": f"Processing failed: {e}"}), 500

    record = ScanRecord(
        filename=safe_name,
        verdict=compliance["verdict"],
        issue_count=compliance["issue_count"],
        ocr_confidence=compliance["ocr_confidence"],
        commodity_name=fields.get("commodity_name"),
        manufacturer=fields.get("manufacturer"),
    )
    db.session.add(record)
    db.session.commit()

    response = {
        "scan_id": record.id,
        "verdict": compliance["verdict"],
        "review_reason": compliance["review_reason"],
        "ocr_confidence": compliance["ocr_confidence"],
        "extracted_fields": {k: v for k, v in fields.items() if not k.startswith("_")},
        "checked_fields": compliance["checked_fields"],
        "issues": compliance["issues"],
        "raw_text": fields.get("_raw_text"),
        "report_file": os.path.basename(report_path),
    }
    return jsonify(response)


@app.route("/api/history")
def history():
    records = ScanRecord.query.order_by(ScanRecord.created_at.desc()).limit(50).all()
    return jsonify([
        {
            "id": r.id,
            "filename": r.filename,
            "verdict": r.verdict,
            "issue_count": r.issue_count,
            "ocr_confidence": r.ocr_confidence,
            "commodity_name": r.commodity_name,
            "manufacturer": r.manufacturer,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ])


@app.route("/api/report/<path:report_file>")
def download_report(report_file):
    return send_from_directory(REPORT_DIR, report_file, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5001)

