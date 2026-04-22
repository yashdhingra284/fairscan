from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime

def generate_bias_report_pdf(report: dict) -> bytes:

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title", parent=styles["Normal"],
        fontSize=24, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1e40af"),
        alignment=TA_CENTER, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#64748b"),
        alignment=TA_CENTER, spaceAfter=20
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Normal"],
        fontSize=14, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=16, spaceAfter=8
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#334155"),
        spaceAfter=6, leading=16
    )

    elements = []

    # ── Header ───────────────────────────────────────────────────
    elements.append(Paragraph("FairScan", title_style))
    elements.append(Paragraph("AI Bias Audit Report", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    elements.append(Spacer(1, 12))

    # ── Report Meta ──────────────────────────────────────────────
    meta_data = [
        ["Report ID", str(report.get("report_id", "N/A"))],
        ["Dataset ID", str(report.get("dataset_id", "N/A"))],
        ["Sensitive Attribute", report.get("sensitive_attribute", "N/A").capitalize()],
        ["Generated At", datetime.now().strftime("%B %d, %Y at %I:%M %p")],
        ["Overall Bias Level", report.get("overall_bias_level", "N/A")],
    ]

    bias_level = report.get("overall_bias_level", "Low")
    bias_color = (
        colors.HexColor("#16a34a") if bias_level == "Low"
        else colors.HexColor("#d97706") if bias_level == "Medium"
        else colors.HexColor("#dc2626")
    )

    meta_table = Table(meta_data, colWidths=[2 * inch, 4.5 * inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (1, 4), (1, 4), bias_color),
        ("FONTNAME", (1, 4), (1, 4), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))

    # ── Fairness Metrics ─────────────────────────────────────────
    elements.append(Paragraph("Fairness Metrics", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    elements.append(Spacer(1, 8))

    di = report.get("disparate_impact_score", 0)
    sp = report.get("statistical_parity_score", 0)
    eo = report.get("equal_opportunity_score", 0)

    def metric_status(value, threshold, higher_is_better=True):
        if higher_is_better:
            return "FAIR" if value >= threshold else "BIASED"
        else:
            return "FAIR" if value <= threshold else "BIASED"

    metrics_data = [
        ["Metric", "Score", "Threshold", "Status"],
        ["Disparate Impact", f"{di:.4f}", "≥ 0.80", metric_status(di, 0.8)],
        ["Statistical Parity", f"{sp:.4f}", "≤ 0.10", metric_status(sp, 0.1, False)],
        ["Equal Opportunity", f"{eo:.4f}", "≤ 0.10", metric_status(eo, 0.1, False)],
    ]

    metrics_table = Table(metrics_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TEXTCOLOR", (3, 1), (3, 1), colors.HexColor("#16a34a") if di >= 0.8 else colors.HexColor("#dc2626")),
        ("TEXTCOLOR", (3, 2), (3, 2), colors.HexColor("#16a34a") if sp <= 0.1 else colors.HexColor("#dc2626")),
        ("TEXTCOLOR", (3, 3), (3, 3), colors.HexColor("#16a34a") if eo <= 0.1 else colors.HexColor("#dc2626")),
        ("FONTNAME", (3, 1), (3, -1), "Helvetica-Bold"),
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 20))

    # ── Group Positive Rates ─────────────────────────────────────
    group_rates = report.get("group_positive_rates", {})
    if group_rates:
        elements.append(Paragraph("Positive Outcome Rates by Group", section_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
        elements.append(Spacer(1, 8))

        group_data = [["Group", "Positive Rate", "Percentage"]]
        for group, rate in group_rates.items():
            group_data.append([group.capitalize(), f"{rate:.4f}", f"{rate * 100:.1f}%"])

        group_table = Table(group_data, colWidths=[2.5 * inch, 2 * inch, 2 * inch])
        group_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ]))
        elements.append(group_table)
        elements.append(Spacer(1, 20))

    # ── Recommendations ──────────────────────────────────────────
    elements.append(Paragraph("Recommendations", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(report.get("recommendations", "No recommendations available."), body_style))
    elements.append(Spacer(1, 20))

    # ── Footer ───────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "Generated by FairScan — AI Bias Auditor | Hack2Skill Solution Challenge 2026",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                       textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()