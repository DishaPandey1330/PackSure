"""Test extraction on Denver Deodorant label."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from ocr_engine import run_ocr
from extractor import extract_fields

IMAGE = 'uploads/denver_test.jpg'
res = run_ocr(IMAGE)

print("=" * 50)
print("RAW OCR TEXT")
print("=" * 50)
print(res["raw_text"])

fields = extract_fields(res["raw_text"], res.get("lines_with_boxes"), res.get("word_boxes"))
print("=" * 50)
print("EXTRACTION RESULTS")
print("=" * 50)
for k, v in fields.items():
    if k != "_raw_text":
        print(f"  {k:>20}: {v}")
