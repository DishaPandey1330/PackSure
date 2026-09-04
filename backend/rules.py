"""
rules.py
---------
Rule Database for PackSure.

Encodes the mandatory declarations required on pre-packaged commodities
under the Legal Metrology (Packaged Commodities) Rules, 2011 (Rule 6).

In the full architecture (see Technical Approach slide) this lives in
PostgreSQL as an editable "Rule Database" table so it can be updated
without touching code. For this working prototype it is a plain Python
list of dicts so the whole thing runs with zero external DB setup.
To move it into PostgreSQL later, see database.py -> seed_rules_from_module().
"""

MANDATORY_RULES = [
    {
        "field": "manufacturer",
        "label": "Name & Address of Manufacturer/Packer/Importer",
        "required": True,
        "description": "Rule 6(1)(a) - identity and address of the person who manufactured/packed/imported the commodity.",
    },
    {
        "field": "commodity_name",
        "label": "Common / Generic Name of Commodity",
        "required": True,
        "description": "Rule 6(1)(b) - the generic name of the packaged commodity.",
    },
    {
        "field": "net_quantity",
        "label": "Net Quantity (Standard Unit)",
        "required": True,
        "regex": r"(?:net\s*(?:qty|quantity|vol|volume|wt|weight)?[:\s]*)?(\d+(?:\.\d+)?)\s*(g|gm|gms|kg|ml|m1|l|litre|liters?|pcs|units?)\b",
        "description": "Rule 6(1)(c) - net quantity in standard units (g/kg/ml/l).",
    },
    {
        "field": "mfg_date",
        "label": "Month & Year of Manufacture/Packing/Import",
        "required": True,
        "regex": r"(?:mfd|mfg|pkd|packed|date)?[:\s,]*\b(\d{1,2}[/.-]\d{2,4}|\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})\b",
        "description": "Rule 6(1)(e) - month and year the commodity was manufactured or packed.",
    },
    {
        "field": "mrp",
        "label": "Retail Sale Price (MRP incl. of all taxes)",
        "required": True,
        "regex": r"(?:m\.?r\.?p\.?|price|retail\s*price|rs\.?|inr|₹|\u20b9)[:\s\n]*(?:incl\.?\s*of\s*all\s*taxes)?[:\s\n]*(?:rs\.?|inr|₹|\u20b9)?\s*(\d+(?:[.,]\d{1,2})?)",
        "description": "Rule 6(1)(f) - maximum retail price inclusive of all taxes.",
    },
    {
        "field": "customer_care",
        "label": "Consumer Care Details (Address/Phone/Email)",
        "required": True,
        "regex": r"(?:call|tel|phone|contact|mobile|care|email|feedback)?[:\s]*(\+?\d[\d\-\s]{8,14}\d|1800\d{6,8}|[\w.+-]+@[\w-]+\.[\w.-]+)",
        "description": "Rule 6(1)(g) - name, address, telephone/email for consumer complaints.",
    },
    {
        "field": "email",
        "label": "Consumer Care Email Address",
        "required": False,
        "description": "Email address for consumer feedback.",
    },
    {
        "field": "phone_number",
        "label": "Consumer Care Helpline / Toll-Free Number",
        "required": False,
        "description": "Telephone or Toll-Free number for consumer complaints.",
    },
    {
        "field": "batch_no",
        "label": "Batch / Lot / Code Number",
        "required": True,
        "regex": r"(?:batch|lot|b\.?\s*no\.?|b\.?\s*code|code\s*no\.?|lot\s*no\.?)[:\s]*([a-z0-9/,\-]+)|\b([a-z]\d{3,}[a-z0-9,]*)\b",
        "description": "Rule 6(1)(d) - batch, lot or code number allowing traceability.",
    },
    {
        "field": "best_before",
        "label": "Best Before / Use By Date",
        "required": False,
        "regex": r"(?:best before|use by|exp(?:iry)?|use before)[:\s]*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}|\d{1,2}[/.-]\d{2,4}|\d{1,2}\s*months?)",
        "description": "Required for food items under FSS Act; flagged as advisory here.",
    },
]

# Minimum readable font height (mm) vs. package area slab, simplified from
# Rule 7 (Second Schedule) — used by the OpenCV placement/size check stub.
FONT_SIZE_SLABS = [
    {"max_area_cm2": 100, "min_height_mm": 1.0},
    {"max_area_cm2": 500, "min_height_mm": 2.0},
    {"max_area_cm2": float("inf"), "min_height_mm": 4.0},
]
