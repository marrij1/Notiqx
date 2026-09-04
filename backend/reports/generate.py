from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)

from supabase_client import supabase_auth, supabase_db


router = APIRouter(
    prefix="/engagements",
    tags=["Reports"]
)

security = HTTPBearer()


@router.get("/{engagement_id}/report")
async def generate_report(
    engagement_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    # --------------------------------------------------
    # 1. Verify JWT
    # --------------------------------------------------

    try:
        user_response = supabase_auth.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token."
            )

        user_id = user_response.user.id
        tester_email = user_response.user.email or "PentFlow Tester"

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    # --------------------------------------------------
    # 2. Get engagement
    # --------------------------------------------------

    try:
        engagement_response = (
            supabase_db
            .table("engagements")
            .select("*")
            .eq("id", engagement_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found."
        )

    if not engagement_response.data:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found."
        )

    engagement = engagement_response.data

    # --------------------------------------------------
    # 3. Get findings
    # --------------------------------------------------

    findings_response = (
        supabase_db
        .table("findings")
        .select("*")
        .eq("engagement_id", engagement_id)
        .order("created_at", desc=False)
        .execute()
    )

    findings = findings_response.data or []

    # --------------------------------------------------
    # 4. Get evidence for each finding
    # --------------------------------------------------

    evidence_by_finding = {}

    for finding in findings:
        evidence_response = (
            supabase_db
            .table("evidence")
            .select("*")
            .eq("finding_id", finding["id"])
            .order("created_at", desc=False)
            .execute()
        )

        evidence_by_finding[finding["id"]] = evidence_response.data or []

    # --------------------------------------------------
    # 5. Create PDF
    # --------------------------------------------------

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"{engagement['name']} - Notiqx Report",
        author="Notiqx"
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=26,
        leading=32,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        spaceBefore=10,
        spaceAfter=10
    )

    subheading_style = ParagraphStyle(
        "ReportSubHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        spaceBefore=8,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7
    )

    code_style = ParagraphStyle(
        "ReportCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        leftIndent=8,
        rightIndent=8,
        spaceBefore=5,
        spaceAfter=8
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11
    )

    story = []

    # --------------------------------------------------
    # Cover page
    # --------------------------------------------------

    story.append(Spacer(1, 55 * mm))

    story.append(
        Paragraph("Penetration Testing Report", title_style)
    )

    story.append(
        Paragraph(
            f"<b>{engagement['name']}</b>",
            ParagraphStyle(
                "EngagementTitle",
                parent=title_style,
                fontSize=20
            )
        )
    )

    story.append(Spacer(1, 15 * mm))

    cover_data = [
        ["Client", engagement.get("client_name") or "N/A"],
        ["Tester", tester_email],
        [
            "Date Range",
            f"{engagement.get('start_date') or 'N/A'}"
            f" → {engagement.get('end_date') or 'N/A'}"
        ],
        ["Status", engagement.get("status", "N/A").title()],
    ]

    cover_table = Table(
        cover_data,
        colWidths=[40 * mm, 110 * mm]
    )

    cover_table.setStyle(
        TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ])
    )

    story.append(cover_table)
    story.append(Spacer(1, 35 * mm))

    story.append(
        Paragraph(
            "<b>CONFIDENTIAL</b><br/>"
            "This report contains confidential security assessment "
            "information intended only for authorized recipients.",
            ParagraphStyle(
                "Confidential",
                parent=body_style,
                alignment=TA_CENTER,
                fontSize=9
            )
        )
    )

    story.append(PageBreak())

    # --------------------------------------------------
    # Table of Contents
    # --------------------------------------------------

    story.append(
        Paragraph("Table of Contents", heading_style)
    )

    toc_data = [
        ["Section", "Content"],
        ["1", "Executive Summary"],
    ]

    for index, finding in enumerate(findings, start=2):
        toc_data.append([
            str(index),
            finding.get("title", "Untitled Finding")
        ])

    toc_data.append([
        str(len(findings) + 2),
        "Scope and Methodology"
    ])

    toc_table = Table(
        toc_data,
        colWidths=[20 * mm, 130 * mm],
        repeatRows=1
    )

    toc_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(toc_table)
    story.append(PageBreak())

    # --------------------------------------------------
    # Executive Summary
    # --------------------------------------------------

    story.append(
        Paragraph("Executive Summary", heading_style)
    )

    total_findings = len(findings)

    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "informational": 0
    }

    for finding in findings:
        severity = finding.get("severity", "").lower()

        if severity in severity_counts:
            severity_counts[severity] += 1

    if severity_counts["critical"] > 0:
        overall_risk = "Critical"
    elif severity_counts["high"] > 0:
        overall_risk = "High"
    elif severity_counts["medium"] > 0:
        overall_risk = "Medium"
    elif severity_counts["low"] > 0:
        overall_risk = "Low"
    else:
        overall_risk = "Informational"

    story.append(
        Paragraph(
            f"This penetration testing engagement identified "
            f"<b>{total_findings}</b> finding(s). "
            f"The overall risk rating is <b>{overall_risk}</b>.",
            body_style
        )
    )

    severity_table_data = [
        ["Severity", "Count"],
        ["Critical", str(severity_counts["critical"])],
        ["High", str(severity_counts["high"])],
        ["Medium", str(severity_counts["medium"])],
        ["Low", str(severity_counts["low"])],
        ["Informational", str(severity_counts["informational"])],
    ]

    severity_table = Table(
        severity_table_data,
        colWidths=[70 * mm, 30 * mm]
    )

    severity_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 1), (1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(severity_table)

    # --------------------------------------------------
    # Findings
    # --------------------------------------------------

    for index, finding in enumerate(findings, start=1):

        story.append(PageBreak())

        story.append(
            Paragraph(
                f"{index}. {finding.get('title', 'Untitled Finding')}",
                heading_style
            )
        )

        details = [
            ["Severity", finding.get("severity", "N/A").title()],
            ["Status", finding.get("status", "N/A").title()],
            [
                "Vulnerability Type",
                finding.get("vulnerability_type") or "N/A"
            ],
            [
                "Affected URL",
                finding.get("affected_url") or "N/A"
            ],
            [
                "Affected Parameter",
                finding.get("affected_parameter") or "N/A"
            ],
        ]

        if finding.get("cvss_score") is not None:
            details.append([
                "CVSS Score",
                str(finding["cvss_score"])
            ])

        if finding.get("cwe_id"):
            details.append([
                "CWE",
                finding["cwe_id"]
            ])

        details_table = Table(
            details,
            colWidths=[45 * mm, 115 * mm]
        )

        details_table.setStyle(
            TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )

        story.append(details_table)

        sections = [
            ("Description", finding.get("description")),
            ("Impact", finding.get("impact")),
            ("Steps to Reproduce", finding.get("steps_to_reproduce")),
            ("Recommendation", finding.get("recommendation")),
        ]

        for section_title, content in sections:
            if content:
                story.append(
                    Paragraph(section_title, subheading_style)
                )
                story.append(
                    Paragraph(
                        str(content).replace("\n", "<br/>"),
                        body_style
                    )
                )

        # Evidence
        story.append(
            Paragraph("Evidence", subheading_style)
        )

        evidence_items = evidence_by_finding.get(
            finding["id"],
            []
        )

        if not evidence_items:
            story.append(
                Paragraph(
                    "No evidence attached.",
                    body_style
                )
            )

        for evidence in evidence_items:
            evidence_type = evidence.get(
                "evidence_type",
                "unknown"
            )

            evidence_title = evidence.get(
                "title"
            ) or evidence_type.replace("_", " ").title()

            story.append(
                Paragraph(
                    f"<b>{evidence_title}</b>",
                    small_style
                )
            )

            if evidence_type == "screenshot":
                story.append(
                    Paragraph(
                        "Screenshot evidence is stored securely "
                        "in Supabase Storage.",
                        body_style
                    )
                )

            elif evidence.get("content"):
                content = str(evidence["content"])

                # Prevent ReportLab markup from interpreting
                # evidence as HTML.
                content = (
                    content
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br/>")
                )

                if evidence_type in [
                    "http_request",
                    "curl_command",
                    "code_snippet",
                    "tool_output"
                ]:
                    story.append(
                        Paragraph(
                            content,
                            code_style
                        )
                    )
                else:
                    story.append(
                        Paragraph(
                            content,
                            body_style
                        )
                    )

    # --------------------------------------------------
    # Scope and Methodology
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Scope and Methodology",
            heading_style
        )
    )

    story.append(
        Paragraph(
            "<b>Scope</b>",
            subheading_style
        )
    )

    scope = engagement.get("scope") or "No scope information provided."

    story.append(
        Paragraph(
            str(scope).replace("\n", "<br/>"),
            body_style
        )
    )

    story.append(
        Paragraph(
            "<b>Methodology</b>",
            subheading_style
        )
    )

    story.append(
        Paragraph(
            "The assessment was performed using manual security "
            "testing techniques and supporting security testing "
            "tools. Findings and supporting evidence were "
            "documented during the engagement.",
            body_style
        )
    )

    # --------------------------------------------------
    # Build PDF
    # --------------------------------------------------

    document.build(story)

    pdf_buffer.seek(0)

    filename = (
        f"{engagement.get('name', 'PentFlow-Report')}"
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        + ".pdf"
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )