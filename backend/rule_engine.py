"""
rule_engine.py
--------------
Compliance Check (Rule Engine) + Result generation stage.

Compares the structured fields extracted by extractor.py against
rules.MANDATORY_RULES and produces a Compliant / Non-Compliant /
Needs Review verdict with an evidence trail (issue list) — matching
the 'Compliance Result & Report' block of the workflow diagram.
"""
from rules import MANDATORY_RULES

OCR_CONFIDENCE_REVIEW_THRESHOLD = 55.0  # below this -> force "Needs Review"


def check_compliance(fields: dict, ocr_confidence: float) -> dict:
    issues = []
    checked = []

    for rule in MANDATORY_RULES:
        f = rule["field"]
        value = fields.get(f)
        present = bool(value)

        status = "pass" if present else ("fail" if rule["required"] else "warn")
        if not present and rule["required"]:
            issues.append({
                "field": f,
                "label": rule["label"],
                "severity": "high",
                "message": f"{rule['label']} not found on the label.",
            })
        elif not present and not rule["required"]:
            issues.append({
                "field": f,
                "label": rule["label"],
                "severity": "low",
                "message": f"{rule['label']} not detected (advisory).",
            })

        checked.append({
            "field": f,
            "label": rule["label"],
            "value": value,
            "status": status,
            "required": rule["required"],
        })

    high_severity_issues = [i for i in issues if i["severity"] == "high"]

    if ocr_confidence < OCR_CONFIDENCE_REVIEW_THRESHOLD:
        verdict = "Needs Review"
        review_reason = f"OCR confidence low ({ocr_confidence}%) — extracted text may be unreliable."
    elif high_severity_issues:
        verdict = "Non-Compliant"
        review_reason = None
    else:
        verdict = "Compliant"
        review_reason = None

    return {
        "verdict": verdict,
        "review_reason": review_reason,
        "issues": issues,
        "checked_fields": checked,
        "ocr_confidence": ocr_confidence,
        "issue_count": len(high_severity_issues),
    }
