"""
generate_sample_labels.py
--------------------------
Creates a handful of synthetic package-label images so you can test the
PackSure pipeline immediately, without waiting on a dataset download.
One label is deliberately INCOMPLETE (missing MRP + batch no.) so you
can see a "Non-Compliant" result too.

Run:  python generate_sample_labels.py
Output: sample_images/label_1_compliant.png
        sample_images/label_2_missing_mrp.png
        sample_images/label_3_missing_batch.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = os.path.join(os.path.dirname(__file__), "sample_images")
os.makedirs(OUT_DIR, exist_ok=True)


def font(size=22):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()


def render_label(lines, path, size=(700, 500)):
    img = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(img)
    y = 30
    for line, fsize in lines:
        draw.text((30, y), line, fill="black", font=font(fsize))
        y += fsize + 18
    img.save(path)
    print("wrote", path)


render_label(
    [
        ("ABC Atta - Whole Wheat Flour", 24),
        ("Net Qty: 500 g", 20),
        ("MRP: Rs. 125.00 (incl. of all taxes)", 20),
        ("Mfg Date: 12/04/2026", 20),
        ("Best Before: 11/04/2027", 20),
        ("Batch No: B12345", 20),
        ("Mfd by: ABC Foods Pvt Ltd, Nagpur, MH", 18),
        ("Customer Care: 1800-123-4567", 18),
        ("care@abcfoods.com", 18),
        ("FSSAI Lic No: 10012022000125", 18),
    ],
    os.path.join(OUT_DIR, "label_1_compliant.png"),
)

render_label(
    [
        ("Sunrise Cooking Oil", 24),
        ("Net Qty: 1 L", 20),
        ("Mfg Date: 01/2026", 20),
        ("Mfd by: Sunrise Agro Pvt Ltd", 18),
        ("Customer Care: 1800-999-1111", 18),
        # MRP and Batch No. intentionally omitted
    ],
    os.path.join(OUT_DIR, "label_2_missing_mrp_batch.png"),
)

render_label(
    [
        ("Sparkle Detergent Powder", 24),
        ("Net Qty: 1 kg", 20),
        ("MRP: Rs. 89.00", 20),
        ("Mfg Date: 03/2026", 20),
        ("Mfd by: Sparkle Chem Pvt Ltd", 18),
        # Customer care & batch omitted
    ],
    os.path.join(OUT_DIR, "label_3_missing_care_batch.png"),
)
