"""
database.py
------------
Data & Rule Repository (Product & Batch Database + scan history).

Uses SQLite through SQLAlchemy so the project runs on a laptop with
zero setup. The Technical Approach slide specifies PostgreSQL for
production — to switch, just change SQLALCHEMY_DATABASE_URI below to
e.g. "postgresql://user:pass@localhost:5432/packsure" and `pip install
psycopg2-binary`. No other code changes are required.
"""
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Optional: point this at data/bigbasket_products.csv (Kaggle "BigBasket
# Entire Product List") to seed a real Manufacturer/Product reference
# table for the cross-check step. See README for the download link.
DEFAULT_SQLITE_PATH = os.path.join(os.path.dirname(__file__), "packsure.db")


class ScanRecord(db.Model):
    __tablename__ = "scan_history"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    verdict = db.Column(db.String(20))
    issue_count = db.Column(db.Integer)
    ocr_confidence = db.Column(db.Float)
    commodity_name = db.Column(db.String(255))
    manufacturer = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProductReference(db.Model):
    """Trusted product/manufacturer records used by the
    'Product & Batch Verification' cross-check step. Seed this from the
    Kaggle BigBasket dataset (see scripts/seed_products.py)."""
    __tablename__ = "product_reference"
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), index=True)
    brand = db.Column(db.String(255))
    category = db.Column(db.String(255))
    market_price = db.Column(db.Float, nullable=True)


def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DEFAULT_SQLITE_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
