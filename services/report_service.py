import os
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config import Config

class ReportService:
    @staticmethod
    def generate_pdf(inspection_data: dict, output_path: str) -> str:
        """
        Generates a professional PDF Quality Assessment Report using ReportLab.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        primary_color = colors.HexColor("#15803D")    # Dark Green
        secondary_color = colors.HexColor("#1E293B")  # Slate 800
        accent_color = colors.HexColor("#10B981")     # Emerald
        muted_color = colors.HexColor("#64748B")      # Slate 500
        card_bg = colors.HexColor("#F8FAFC")          # Light Slate
        
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=primary_color,
            spaceAfter=4,
            leading=26
        )
        
        section_style = ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=secondary_color,
            spaceBefore=10,
            spaceAfter=6
        )
        
        normal_style = ParagraphStyle(
            "NormalText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=secondary_color,
            leading=13
        )
        
        bold_style = ParagraphStyle(
            "BoldText",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=secondary_color,
            leading=13
        )
        
        disclaimer_style = ParagraphStyle(
            "DisclaimerText",
            parent=styles["Italic"],
            fontName="Helvetica-Oblique",
            fontSize=8,
            textColor=colors.HexColor("#475569"),
            leading=11
        )

        elements = []
        
        # Header banner table
        header_data = [
            [
                Paragraph("<b>OnionVision AI</b><br/><font size=8 color='#15803D'>Intelligent Post-Harvest Quality Assessment Certificate</font>", title_style),
                Paragraph(f"<b>REPORT ID:</b> {inspection_data['report_id']}<br/><b>Date:</b> {inspection_data.get('created_at', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))}<br/><b>AI Engine:</b> {'Real YOLO Model' if inspection_data.get('ai_mode') == 'real' else 'Demo Simulation'}", normal_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[3.8 * inch, 3.4 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(header_table)
        elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=8, spaceAfter=14))
        
        # Executive Quality Summary Score Card
        score = inspection_data.get("quality_score", 0.0)
        grade = inspection_data.get("preliminary_grade", "URS")
        total_onions = inspection_data.get("total_onions", 0)
        confidence = int(inspection_data.get("average_confidence", 0.0) * 100)
        
        score_data = [
            [
                Paragraph(f"<font size=10 color='#64748B'>PRELIMINARY GRADE</font><br/><b><font size=20 color='#15803D'>{grade}</font></b>", normal_style),
                Paragraph(f"<font size=10 color='#64748B'>QUALITY SCORE</font><br/><b><font size=20 color='#0284C7'>{score} / 100</font></b>", normal_style),
                Paragraph(f"<font size=10 color='#64748B'>TOTAL BULBS</font><br/><b><font size=20 color='#1E293B'>{total_onions}</font></b>", normal_style),
                Paragraph(f"<font size=10 color='#64748B'>AI CONFIDENCE</font><br/><b><font size=20 color='#10B981'>{confidence}%</font></b>", normal_style),
            ]
        ]
        score_table = Table(score_data, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.8 * inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), card_bg),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 14))
        
        # Categorical Breakdown Table
        elements.append(Paragraph("Category & Defect Analysis", section_style))
        
        breakdown_rows = [
            ["Defect Category", "Scoring Weight", "Count", "Percentage", "Commercial Status"]
        ]
        
        categories = [
            ("Good / Healthy Quality", "100 pts", inspection_data.get("good_count", 0), f"{inspection_data.get('good_percentage', 0.0)}%", "Commercial Grade A"),
            ("Damaged / Bruised", "50 pts", inspection_data.get("damaged_count", 0), f"{inspection_data.get('damaged_percentage', 0.0)}%", "Minor Surface Defect"),
            ("Rotten / Moldy", "0 pts", inspection_data.get("rotten_count", 0), f"{inspection_data.get('rotten_percentage', 0.0)}%", "Severe Rejection Defect"),
            ("Sprouted", "40 pts", inspection_data.get("sprouted_count", 0), f"{inspection_data.get('sprouted_percentage', 0.0)}%", "Storage Spoilage")
        ]
        
        for name, weight, count, pct, note in categories:
            breakdown_rows.append([name, weight, str(count), pct, note])
            
        cat_table = Table(breakdown_rows, colWidths=[2.2 * inch, 1.2 * inch, 1.0 * inch, 1.2 * inch, 1.6 * inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#065F46")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,0), (-1,0), 6),
            ('ALIGN', (1,0), (3,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, card_bg]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8.5),
            ('TOPPADDING', (0,1), (-1,-1), 5),
            ('BOTTOMPADDING', (0,1), (-1,-1), 5),
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 14))
        
        # Inspection Visuals (Original & Annotated side-by-side)
        elements.append(Paragraph("Visual Inspection Evidence", section_style))
        
        orig_img_path = inspection_data.get("original_image_path")
        annot_img_path = inspection_data.get("annotated_image_path")
        
        img_cells = []
        if orig_img_path and os.path.exists(orig_img_path):
            img_cells.append([
                Paragraph("<b>Original Uploaded Image</b>", bold_style),
                Paragraph("<b>AI Annotated Bounding Boxes</b>", bold_style)
            ])
            try:
                rl_orig = RLImage(orig_img_path, width=3.4 * inch, height=2.3 * inch)
                rl_annot = RLImage(annot_img_path if (annot_img_path and os.path.exists(annot_img_path)) else orig_img_path, width=3.4 * inch, height=2.3 * inch)
                img_cells.append([rl_orig, rl_annot])
                
                img_table = Table(img_cells, colWidths=[3.6 * inch, 3.6 * inch])
                img_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ]))
                elements.append(img_table)
            except Exception as e:
                elements.append(Paragraph(f"Image preview unavailable: {str(e)}", normal_style))
        
        elements.append(Spacer(1, 14))
        
        # Methodology & Disclaimer section
        elements.append(Paragraph("Assessment Methodology & Scoring Formula", section_style))
        methodology_text = (
            "The Preliminary Quality Score is computed using an objective weighted algorithm: "
            "<b>Quality Score = (Good × 100 + Damaged × 50 + Sprouted × 40 + Rotten × 0) / Total</b>. "
            "Grades are defined as: Grade A (≥90) Premium Export; Grade B (75–89) Domestic Good; Grade C (60–74) Commercial/Processing; "
            "URS (&lt;60) Under Review / High Spoilage."
        )
        elements.append(Paragraph(methodology_text, normal_style))
        elements.append(Spacer(1, 8))
        
        # Official Disclaimer Box
        disclaimer_box = [
            [
                Paragraph(
                    "<b>IMPORTANT LEGAL & REGULATORY DISCLAIMER:</b><br/>"
                    "This digital assessment report is generated via an AI-assisted computer vision model designed for preliminary post-harvest screening and sorting. "
                    "It is NOT an official governmental agricultural certification (such as AGMARK or FSSAI). Real procurement, export clearance, or commercial transactions "
                    "should involve official physical verification.",
                    disclaimer_style
                )
            ]
        ]
        disclaimer_table = Table(disclaimer_box, colWidths=[7.2 * inch])
        disclaimer_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FCA5A5")),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(disclaimer_table)
        
        # Build document
        doc.build(elements)
        return output_path
