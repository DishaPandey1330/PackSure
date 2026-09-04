"""
report_generator.py
--------------------
Result & Report stage: renders the compliance verdict + evidence into a
downloadable PDF, matching the 'Digital Report / Download / Share /
Store' block of the workflow diagram.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

VERDICT_COLORS = {
    "Compliant": colors.HexColor("#1a9850"),
    "Non-Compliant": colors.HexColor("#d73027"),
    "Needs Review": colors.HexColor("#e6ab02"),
}


def generate_report(result: dict, fields: dict, filename: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, f"{os.path.splitext(filename)[0]}_report.pdf")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], textColor=colors.HexColor("#1f3864"))
    verdict_style = ParagraphStyle(
        "Verdict", parent=styles["Heading1"],
        textColor=VERDICT_COLORS.get(result["verdict"], colors.black),
    )

    doc = SimpleDocTemplate(report_path, pagesize=A4, topMargin=25 * mm)
    story = [
        Paragraph("PackSure — Legal Metrology Compliance Report", title_style),
        Spacer(1, 6),
        Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}", styles["Normal"]),
        Paragraph(f"Source file: {filename}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(f"Verdict: {result['verdict']}", verdict_style),
    ]
    if result.get("review_reason"):
        story.append(Paragraph(result["review_reason"], styles["Normal"]))
    story.append(Spacer(1, 10))

    # Extracted fields table
    story.append(Paragraph("Extracted Label Details", styles["Heading2"]))
    field_rows = [["Field", "Value", "Status"]]
    for c in result["checked_fields"]:
        field_rows.append([c["label"], c["value"] or "—", c["status"].upper()])
    t = Table(field_rows, colWidths=[180, 220, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3864")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # Issues
    story.append(Paragraph("Issues Found", styles["Heading2"]))
    if result["issues"]:
        issue_rows = [["Field", "Severity", "Message"]]
        for i in result["issues"]:
            issue_rows.append([i["label"], i["severity"].upper(), i["message"]])
        ti = Table(issue_rows, colWidths=[150, 70, 260])
        ti.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d73027")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(ti)
    else:
        story.append(Paragraph("No issues detected.", styles["Normal"]))

    story.append(Spacer(1, 14))
    story.append(Paragraph(f"OCR confidence: {result['ocr_confidence']}%", styles["Normal"]))

    doc.build(story)
    return report_path
