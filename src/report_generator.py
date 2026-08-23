"""Render a recommendation engine result as a downloadable PDF report."""

import io
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

GREEN_DARK = colors.HexColor("#1f4a3a")
GREEN_LIGHT = colors.HexColor("#dbe9c6")
GREEN_LIGHT_2 = colors.HexColor("#eaf2dc")
TEXT_MUTED = colors.HexColor("#5b6b5e")
BORDER = colors.HexColor("#e1e6d8")

CATEGORY_LABELS = {"diet": "Diet", "lifestyle": "Lifestyle", "home_care": "Home Care"}


def build_report_pdf(user_input: Dict[str, Any], result: Dict[str, Any]) -> bytes:
    """Build a PDF summarizing one recommendation run and return its bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title=f"Prakriti-Aware Recommendation Report - {result.get('user_id', '')}",
    )
    styles = _build_styles()
    story = []

    story.extend(_header_block(styles, user_input, result))
    story.append(Spacer(1, 10 * mm))
    story.extend(_profile_block(styles, user_input, result))
    story.append(Spacer(1, 8 * mm))

    if result.get("referral_warning"):
        story.extend(_notice_block(styles, "Referral Notice", result["referral_warning"]))
        story.append(Spacer(1, 6 * mm))

    grouped = result.get("recommendations_by_category", {})
    for category in ["diet", "lifestyle", "home_care"]:
        items = grouped.get(category, [])
        story.extend(_category_block(styles, category, items))
        story.append(Spacer(1, 6 * mm))

    story.append(Spacer(1, 4 * mm))
    story.extend(_notice_block(styles, "Safety Note", result.get("safety_note", "")))

    doc.build(story)
    return buffer.getvalue()


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName="Times-Bold",
            textColor=GREEN_DARK,
            fontSize=22,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            textColor=TEXT_MUTED,
            fontSize=10,
        )
    )
    styles.add(
        ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            textColor=colors.white,
            backColor=GREEN_DARK,
            fontSize=12,
            leading=16,
            leftIndent=8,
            spaceBefore=0,
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            "CardTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            textColor=GREEN_DARK,
            fontSize=11.5,
        )
    )
    styles.add(
        ParagraphStyle(
            "CardBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
        )
    )
    styles.add(
        ParagraphStyle(
            "CardMeta",
            parent=styles["Normal"],
            fontSize=8.5,
            textColor=TEXT_MUTED,
            leading=11,
        )
    )
    styles.add(
        ParagraphStyle(
            "NoticeBody",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#4a4030"),
            leading=12,
        )
    )
    return styles


def _header_block(styles, user_input, result):
    generated_for = result.get("user_id", "-")
    return [
        Paragraph("Prakriti-Aware Recommendation Report", styles["ReportTitle"]),
        Paragraph(
            f"Generated for User ID: {generated_for} &nbsp;|&nbsp; "
            f"Language: {user_input.get('user_context', {}).get('preferred_language', 'English')}",
            styles["ReportSubtitle"],
        ),
        Spacer(1, 4 * mm),
        HRFlowable(width="100%", thickness=1.2, color=GREEN_LIGHT, spaceBefore=2, spaceAfter=2),
    ]


def _profile_block(styles, user_input, result):
    skin_result = user_input.get("skin_result", {})
    prakriti_result = user_input.get("prakriti_result", {})
    scores = prakriti_result.get("prakriti_scores", {})

    score_line = " | ".join(f"{k.title()} {round(float(v) * 100)}%" for k, v in scores.items())

    rows = [
        ["Skin Condition", skin_result.get("predicted_condition", "-")],
        ["Severity", str(skin_result.get("severity", "-")).title()],
        ["Skin Confidence", f"{float(skin_result.get('confidence', 0)) * 100:.0f}%"],
        ["Dominant / Secondary Prakriti", f"{prakriti_result.get('dominant_prakriti', '-')} / {prakriti_result.get('secondary_prakriti', '-')}"],
        ["Prakriti Scores", score_line or "-"],
        ["Overall Confidence", str(result.get("overall_confidence_level", "-")).title()],
    ]

    table = Table(rows, colWidths=[55 * mm, 105 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT_2),
                ("TEXTCOLOR", (0, 0), (0, -1), GREEN_DARK),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    return [
        Paragraph("Analysis Summary", styles["Heading3"]),
        Paragraph(result.get("recommendation_summary", ""), styles["CardBody"]),
        Spacer(1, 3 * mm),
        table,
    ]


def _notice_block(styles, title, text):
    if not text:
        return []
    table = Table([[Paragraph(f"<b>{title}:</b> {text}", styles["NoticeBody"])]], colWidths=[160 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbeecb")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#eed9a0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return [table]


def _category_block(styles, category, items):
    label = CATEGORY_LABELS.get(category, category.title())
    heading_table = Table([[Paragraph(f"{label} ({len(items)})", styles["SectionHeading"])]], colWidths=[160 * mm])
    heading_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), GREEN_DARK),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    if not items:
        return [heading_table, Spacer(1, 3 * mm), Paragraph("No recommendations in this category.", styles["CardMeta"])]

    cards = []
    for item in items:
        matched = item.get("matched_factors", {})
        matched_text = f"{matched.get('prakriti', '-')}, {matched.get('condition', '-')}"
        card_content = [
            Paragraph(item.get("title", ""), styles["CardTitle"]),
            Paragraph(item.get("text", ""), styles["CardBody"]),
            Spacer(1, 1.5 * mm),
            Paragraph(f"Score: {item.get('score', '-')} | Matched: {matched_text}", styles["CardMeta"]),
            Paragraph(item.get("reason", ""), styles["CardMeta"]),
        ]
        card_table = Table([[card_content]], colWidths=[160 * mm])
        card_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        cards.append(card_table)
        cards.append(Spacer(1, 3 * mm))

    # Keep the section heading glued to its first card so the heading never
    # orphans alone at the bottom of a page with its content on the next.
    head_and_first = KeepTogether([heading_table, Spacer(1, 3 * mm), cards[0]])
    return [head_and_first, *cards[1:]]
