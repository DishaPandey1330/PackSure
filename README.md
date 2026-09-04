# PackSure — SIH26034 (Team ERRORACCESS)

A working prototype of the solution described in your SIH idea presentation:
**"Software System to check compliance of Packaged Commodities under Legal
Metrology (Packaged Commodities) Rules, 2011 by scanning products, images
and labels."**

It follows the exact workflow and tech stack from your slides:

```
Scan/Upload Image → OpenCV preprocessing → Tesseract OCR → NLP/Regex field
extraction → Rule Engine compliance check → Result (Compliant /
Non-Compliant / Needs Review) → Downloadable PDF report
```

| Layer                 | Tech (matches your PPT)                     |
|------------------------|---------------------------------------------|
| Frontend               | React.js (Vite)                              |
| Backend                | Flask (Python), RESTful APIs                 |
| Image Processing       | OpenCV                                       |
| OCR                    | Tesseract OCR (pytesseract)                  |
| Information Extraction | NLP + Regex                                  |
| Compliance Engine      | Python rule engine                           |
| Database               | SQLite by default (1-line swap to PostgreSQL)|
| Report Generation      | ReportLab (PDF)                              |

This has already been built and tested end-to-end — three sample labels
were scanned and correctly classified as Compliant / Non-Compliant during
development. You just need to run it on your own machine.

---

## 1. What's in this folder

```
PackSure/
├── backend/
│   ├── app.py                  Flask API (the server)
│   ├── ocr_engine.py           OpenCV preprocessing + Tesseract OCR
│   ├── extractor.py            NLP/Regex → structured fields
│   ├── rule_engine.py          Compliance checking logic
│   ├── rules.py                Legal Metrology mandatory-field rules
│   ├── report_generator.py     PDF report builder
│   ├── database.py             SQLite models (scan history, products)
│   ├── seed_products.py        Optional: load Kaggle dataset into DB
│   ├── generate_sample_labels.py   Makes 3 test label images instantly
│   ├── requirements.txt
│   └── sample_images/          Pre-generated test labels (after step 3)
└── frontend/
    ├── src/App.jsx             The UI
    ├── src/App.css
    └── package.json
```

---

## 2. Install prerequisites (one-time)

You need three things on your laptop: **Python 3.10+**, **Node.js 18+**,
and the **Tesseract OCR engine** (a separate program pytesseract calls
into — it's not a Python package by itself).

### Windows
1. Python: https://www.python.org/downloads/ (tick "Add to PATH" during install)
2. Node.js LTS: https://nodejs.org/
3. Tesseract: download the installer from
   https://github.com/UB-Mannheim/tesseract/wiki and install to the
   default path (`C:\Program Files\Tesseract-OCR`). After installing, add
   that folder to your PATH, **or** add these two lines near the top of
   `backend/ocr_engine.py`:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```

### macOS
```bash
brew install python node tesseract
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip nodejs npm tesseract-ocr
```

Verify Tesseract is on your PATH:
```bash
tesseract --version
```

---

## 3. Open the project in VS Code

1. Unzip the `PackSure` folder anywhere on your laptop.
2. Open VS Code → **File → Open Folder…** → select the `PackSure` folder.
3. Install the VS Code extensions **Python** (Microsoft) and **ES7+ React
   snippets** if prompted — not required, just helpful.
4. Open a terminal in VS Code: **Terminal → New Terminal**. You'll run the
   backend and frontend in two separate terminals (use the split-terminal
   button, or open two).

---

## 4. Set up & run the backend (Terminal 1)

```bash
cd backend
python3 -m venv venv

# activate the virtual environment
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows (cmd/PowerShell)

pip install -r requirements.txt

# generate 3 ready-to-test label images (no dataset needed)
python generate_sample_labels.py

# start the API server
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```
Leave this terminal running. Sanity check in a browser:
`http://127.0.0.1:5000/api/health` should return `{"status": "ok"}`.

---

## 5. Set up & run the frontend (Terminal 2 — new terminal)

```bash
cd frontend
npm install
npm run dev
```

VS Code will print a local URL, typically `http://localhost:5173/`.
Ctrl+click it (or paste into your browser) to open the app.

---

## 6. Try it

1. In the browser app, click the upload box and select one of:
   - `backend/sample_images/label_1_compliant.png` → should show **Compliant**
   - `backend/sample_images/label_2_missing_mrp_batch.png` → **Non-Compliant**
     (missing MRP + batch number)
   - `backend/sample_images/label_3_missing_care_batch.png` → **Non-Compliant**
     (missing customer care + batch number)
2. Click **Run Compliance Check**. You'll see the verdict, the extracted
   fields table, the specific issues found, and a **Download PDF Report**
   button — this is the "Digital Report" from your workflow diagram.
3. Try your own photos of real packaged products (a snack packet, a
   detergent box, etc.) — take the photo in good light, fairly flat, and
   filling most of the frame for best OCR accuracy.

---

## 7. (Optional) Add a real Kaggle dataset for product cross-checking

Your Technical Approach slide includes a "Product & Batch Database" that
cross-checks scanned products against trusted records. To power that with
real data:

1. Download **BigBasket Entire Product List** from Kaggle:
   https://www.kaggle.com/datasets/surajjha101/bigbasket-entire-product-list-28k-datapoints
   (free Kaggle account needed — click **Download**, ~28,000 Indian retail
   products with brand, category and price, a good stand-in for the
   "Product & Batch Database" reference table).
2. Unzip it and place `BigBasket Products.csv` inside `backend/data/`.
3. From the `backend` folder (venv activated):
   ```bash
   python seed_products.py
   ```
   This loads all rows into the `product_reference` table in `packsure.db`.

For testing the **OCR itself** against real (not synthetic) package
photos, two more useful datasets:
- Kaggle **"Grocery Store Dataset"** (search that name on Kaggle) — real
  smartphone photos of packaged grocery items.
- Hugging Face **`Anamta98/flipkart`** dataset — Indian product images
  already annotated with MRP/expiry/net-content, useful for measuring how
  often your regex patterns correctly parse real labels, so you can tune
  `rules.py`.

Neither is required to demo the working prototype — the synthetic sample
labels already exercise the full pipeline correctly.

---

## 8. Moving from SQLite to PostgreSQL (matches your slide exactly)

The prototype uses SQLite so it runs with zero setup. To switch to
PostgreSQL for a closer match to your submitted architecture:

```bash
pip install psycopg2-binary
```

In `backend/database.py`, change:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DEFAULT_SQLITE_PATH}"
```
to:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://USER:PASSWORD@localhost:5432/packsure"
```
No other code changes are needed — the models and queries are unchanged.

---

## 9. What to say in your demo

- **Package Scanning → OCR:** `ocr_engine.py` runs the exact OpenCV steps
  named on your slide (resize/normalize, denoise, CLAHE contrast
  enhancement, adaptive threshold) before handing the image to Tesseract.
- **Information Identification:** `extractor.py` uses regex/NLP heuristics
  to pull MRP, net quantity, mfg date, batch number, FSSAI licence,
  manufacturer and customer care details — the "Structured Data Output"
  box in your diagram.
- **Compliance & Verification:** `rule_engine.py` checks each field
  against `rules.py`, which encodes Rule 6 of the Legal Metrology
  (Packaged Commodities) Rules, 2011.
- **Explainable Review:** low OCR confidence automatically forces a
  "Needs Review" verdict instead of a false Compliant/Non-Compliant.
- **Result & Report:** the PDF generated by `report_generator.py` is your
  "Digital Report — Download/Share/Store" block.

## 10. Known limitations to mention honestly if asked

- Font-size/placement compliance (Rule 7) is not yet measured in pixels —
  `rules.FONT_SIZE_SLABS` sketches the data structure for it but the
  image-to-millimeter calibration (barcode-based, as described in your
  Feasibility slide) isn't implemented yet.
- The Rule Database is a Python file for the demo, not yet an admin-editable
  table — trivial to move once PostgreSQL is wired in (step 8).
- Manufacturer/commodity-name extraction uses simple heuristics, not a
  trained NLP model — works well on clean labels, less well on cluttered
  ones. A natural next step (v2) is a small NER model fine-tuned on the
  Food Packaging OCR dataset (Mendeley) or the Flipkart dataset mentioned above.
