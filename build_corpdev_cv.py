#!/usr/bin/env python3
"""
build_corpdev_cv.py — Generates tailored 1-page executive CV for OpenAI
Role: Corporate Development, Deal Lead
Location: San Francisco, CA (SF HQ, Hybrid 3 days/week)
Strategic Angle: Venture investing as qualifying background; AI-native deal ops (sourcing intelligence, diligence, decision memos).
Linear Ticket: MIN-209
"""

import os
import sys
import io
import pypdf
import pymupdf  # PyMuPDF / fitz
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.pdfgen import canvas
from reportlab import rl_config

# Enforce deterministic byte-for-byte ReportLab PDF rendering
rl_config.invariant = 1

class InvariantCanvas(canvas.Canvas):
    """Custom ReportLab Canvas enforcing byte-level reproducible output."""
    def __init__(self, *args, **kwargs):
        kwargs['invariant'] = 1
        kwargs['pageCompression'] = 1
        super().__init__(*args, **kwargs)

def verify_layout_and_collisions(pdf_path):
    """
    Programmatically verifies:
    1. Single-page constraint (len == 1)
    2. Page boundary containment (all text blocks inside printable page rectangle)
    3. Pairwise text collisions between distinct text blocks
    """
    reader = pypdf.PdfReader(pdf_path)
    page_count = len(reader.pages)
    if page_count != 1:
        raise ValueError(f"CV is {page_count} pages; must be exactly 1 page!")
    
    doc_fitz = pymupdf.open(pdf_path)
    page = doc_fitz[0]
    page_rect = page.rect
    blocks = page.get_text("blocks")
    
    # Check text block containment
    out_of_bounds = []
    text_blocks = [b for b in blocks if b[4].strip()]
    for i, b in enumerate(text_blocks):
        # b: (x0, y0, x1, y1, text, block_no, block_type)
        if b[0] < 0 or b[1] < 0 or b[2] > page_rect.width + 1 or b[3] > page_rect.height + 1:
            out_of_bounds.append((i, b[4][:30], b[:4]))
            
    # Check pairwise vertical overlaps
    overlaps = []
    for i in range(len(text_blocks)):
        for j in range(i + 1, len(text_blocks)):
            b1 = text_blocks[i]
            b2 = text_blocks[j]
            # Check horizontal overlap
            h_overlap = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0]))
            # Check vertical overlap
            v_overlap = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
            # Consider overlap if significant area intersects
            if h_overlap > 15 and v_overlap > 3.0:
                overlaps.append({
                    "b1": b1[4][:30].strip(),
                    "b2": b2[4][:30].strip(),
                    "h_overlap": round(h_overlap, 1),
                    "v_overlap": round(v_overlap, 1)
                })
                
    doc_fitz.close()
    return {
        "page_count": page_count,
        "total_text_blocks": len(text_blocks),
        "text_overlap_count": len(overlaps),
        "out_of_bounds_count": len(out_of_bounds),
        "overlaps": overlaps,
        "out_of_bounds": out_of_bounds
    }

def build_pdf(output_pdf="cv-pavel-cherkashin-corpdev.pdf", output_png="cv-pavel-cherkashin-corpdev-hd.png"):
    pdf_dir = os.path.dirname(os.path.abspath(output_pdf))
    if pdf_dir:
        os.makedirs(pdf_dir, exist_ok=True)
    
    # Letter is 612 x 792 pt
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=34,
        rightMargin=34,
        topMargin=22,
        bottomMargin=18,
    )
    
    usable_width = 612 - 68  # 544 pt
    
    # Palette tailored to OpenAI Corporate Development & Deal Execution
    c_primary = colors.HexColor("#0F172A")    # Deep Slate
    c_oai = colors.HexColor("#10A37F")        # OpenAI Emerald Green
    c_navy = colors.HexColor("#1E3A8A")       # Deep Strategic Navy
    c_body = colors.HexColor("#1E293B")       # Dark Charcoal
    c_muted = colors.HexColor("#475569")      # Muted Slate
    c_bg = colors.HexColor("#F8FAFC")         # Clean Light Slate
    c_border = colors.HexColor("#CBD5E1")     # Light border
    
    base_styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18.0,
        leading=20.0,
        textColor=c_primary,
        spaceAfter=1.5
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.0,
        leading=11.0,
        textColor=c_oai,
        spaceAfter=2.0
    )
    
    contact_style = ParagraphStyle(
        'DocContact',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=8.0,
        leading=10.0,
        textColor=c_muted,
        spaceAfter=2.8
    )
    
    hero_style = ParagraphStyle(
        'HeroText',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.6,
        textColor=c_primary,
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.7,
        leading=11.0,
        textColor=c_navy,
        spaceBefore=2.8,
        spaceAfter=1.6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.6,
        leading=10.0,
        textColor=c_body,
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.8,
        textColor=c_body,
        leftIndent=8,
        firstLineIndent=-8,
    )

    story = []
    
    # 1. Header
    story.append(Paragraph("PAVEL CHERKASHIN", title_style))
    story.append(Paragraph("Corporate Development, Deal Lead &bull; M&amp;A &amp; Strategic Investments &bull; AI-Native Deal Ops &bull; Operator &amp; Investor", subtitle_style))
    story.append(Paragraph("San Francisco, CA (SF HQ, Hybrid 3 days/wk) &nbsp;|&nbsp; pavel@mindrock.capital &nbsp;|&nbsp; linkedin.com/in/pavelcherkashin &nbsp;|&nbsp; github.com/minutta", contact_style))
    
    # 2. Hero Callout Box
    hero_p = Paragraph(
        "<b>Executive Thesis:</b> <i>\"Accelerating OpenAI's strategic inorganic growth through high-conviction M&amp;A, transformative ecosystem partnerships, and AI-native deal operations. 20+ year transaction track record combining frontier venture investing ($100M+ deployed in AI and deep tech), corporate deal leadership (Adobe, Microsoft; architected landmark 1.5M+ seat transaction), and AI systems architecture. Pioneer of autonomous deal ops: deploying multi-agent networks to transform sourcing intelligence, synthetic diligence, automated decision memos, and post-merger integration into an asymmetric competitive moat.\"</i>",
        hero_style
    )
    hero_table = Table([[hero_p]], colWidths=[usable_width])
    hero_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg),
        ('BOX', (0,0), (-1,-1), 0.75, c_border),
        ('LINELEFT', (0,0), (-1,-1), 3.0, c_oai),
        ('TOPPADDING', (0,0), (-1,-1), 2.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.8),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(hero_table)
    story.append(Spacer(1, 2.0))
    
    # 3. Strategic Focus: Corporate Development Mandate & Deal Architecture
    story.append(Paragraph("STRATEGIC FOCUS: INORGANIC GROWTH &amp; AI-NATIVE DEAL OPERATIONS", section_title_style))
    thesis_text = (
        "OpenAI's Corporate Development team drives high-priority inorganic bets that expand research frontiers, secure critical infrastructure, and build enduring market leadership. As Deal Lead, I combine the rigorous transactional discipline of top-tier venture investing with hands-on technical fluency: evaluating proprietary model architectures, compute economics, and technical talent density. By embedding AI-native deal ops into every stage—sourcing radars, automated technical diligence, multi-scenario valuation models, and programmatic integration tracking—I compress transaction cycle times while eliminating execution risk across complex multi-party negotiations."
    )
    story.append(Paragraph(thesis_text, body_style))
    story.append(Spacer(1, 2.0))
    
    # 4. The 6-Month Deal Lead Acceleration Arc
    story.append(Paragraph("THE 6-MONTH CORPORATE DEVELOPMENT EXECUTION ARC", section_title_style))
    
    arc_data = [
        [
            Paragraph("<b>Months 1–2</b><br/><font color='#10A37F'><b>Sourcing &amp; Pipeline</b></font>", ParagraphStyle('H1', parent=body_style, fontName='Helvetica-Bold', fontSize=7.4, leading=9.0)),
            Paragraph("<b>Thematic M&amp;A Strategy &amp; AI-Powered Sourcing:</b> Establish priority acquisition themes across foundational tooling, agent infrastructure, and vertical AI. Deploy autonomous sourcing radars scanning GitHub repos, research preprints, and venture pipelines to identify high-potential acquihire and tech targets before they enter competitive auction processes. Calibrate valuation heuristics with Finance and Legal.", body_style)
        ],
        [
            Paragraph("<b>Months 3–4</b><br/><font color='#10A37F'><b>Deal Execution</b></font>", ParagraphStyle('H2', parent=body_style, fontName='Helvetica-Bold', fontSize=7.4, leading=9.0)),
            Paragraph("<b>Transaction Structuring &amp; Synthetic Diligence:</b> Lead end-to-end execution on 2–3 priority transactions (M&amp;A, minority investments, compute-for-equity pacts). Implement synthetic due diligence pipelines automating code quality audits, IP provenance checks, and retention scenario modeling. Author crisp, data-backed Investment Committee memos and drive cross-functional consensus.", body_style)
        ],
        [
            Paragraph("<b>Months 5–6</b><br/><font color='#10A37F'><b>Integration &amp; Scale</b></font>", ParagraphStyle('H3', parent=body_style, fontName='Helvetica-Bold', fontSize=7.4, leading=9.0)),
            Paragraph("<b>Seamless Integration Telemetry &amp; Scaled Deal Ops:</b> Partner with Engineering and Product to execute 100-day post-close integration playbooks, tracking technical milestones and retention telemetry. Institutionalize autonomous deal ops infrastructure across the Corp Dev organization, enabling scalable, simultaneous execution across multiple concurrent transactions.", body_style)
        ],
    ]
    arc_table = Table(arc_data, colWidths=[90, usable_width - 90])
    arc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(arc_table)
    story.append(Spacer(1, 2.0))
    
    # 5. Core Capabilities Grid
    story.append(Paragraph("CORE TRANSACTIONAL &amp; DEAL LEADERSHIP CAPABILITIES", section_title_style))
    cap_data = [
        [
            Paragraph("&bull; <b>End-to-End M&amp;A &amp; Deal Execution:</b> Full transaction ownership from origination, financial modeling, and diligence to definitive agreements, regulatory navigation, and closing.", bullet_style),
            Paragraph("&bull; <b>AI-Native Deal Operations:</b> Architect of multi-agent intelligence networks for automated deal scouting, synthetic diligence, automated decision memos, and integration tracking.", bullet_style),
        ],
        [
            Paragraph("&bull; <b>Venture Capital &amp; Founder Network:</b> Deep Silicon Valley and global VC network ($100M+ deployed); trusted relationships with top founders, investors, and technical innovators.", bullet_style),
            Paragraph("&bull; <b>Cross-Functional Alignment:</b> Proven ability to unify Research, Product, Engineering, Legal, and Finance around high-stakes, time-sensitive inorganic transactions.", bullet_style),
        ]
    ]
    cap_table = Table(cap_data, colWidths=[usable_width/2.0, usable_width/2.0])
    cap_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.0),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(cap_table)
    story.append(Spacer(1, 2.0))
    
    # 6. Selected Career Track Record
    story.append(Paragraph("SELECTED CAREER TRACK RECORD &amp; STRATEGIC DEAL LEADERSHIP", section_title_style))
    
    story.append(Paragraph("<b>Managing Partner &amp; Venture Capital Investor</b> &mdash; <i>Mindrock Capital / Vestor.In</i> (2016–Present)", ParagraphStyle('Exp1', parent=body_style, fontName='Helvetica-Bold', fontSize=7.7, leading=9.5)))
    story.append(Paragraph("&bull; <b>$100M+ Capital Deployed:</b> Led investments into frontier AI, deep-tech platforms, and high-performance computing infrastructure. Structured innovative venture notes, equity co-investments, and cross-border SPVs.<br/>&bull; <b>Autonomous AI Deal Engine:</b> Built and deployed autonomous multi-agent pipelines automating market screening, thesis validation, cap-table modeling, and continuous investment telemetry.", bullet_style))
    story.append(Spacer(1, 1.5))
    
    story.append(Paragraph("<b>Regional Director &amp; Enterprise Licensing Executive</b> &mdash; <i>Adobe Systems / Enterprise Operations</i>", ParagraphStyle('Exp2', parent=body_style, fontName='Helvetica-Bold', fontSize=7.7, leading=9.5)))
    story.append(Paragraph("&bull; <b>Historic 1.5M+ Seat Agreement:</b> Conceived, negotiated, and executed the <b>largest single enterprise agreement in Adobe's corporate history</b> (1.5M+ licenses). Designed custom multi-tier revenue-sharing frameworks, complex legal structuring, and institutional delivery mechanisms setting a corporate precedent.", bullet_style))
    story.append(Spacer(1, 1.5))

    story.append(Paragraph("<b>Technology Entrepreneur &amp; Corporate Development</b> &mdash; <i>Actis Systems / Microsoft Partner Network</i>", ParagraphStyle('Exp3', parent=body_style, fontName='Helvetica-Bold', fontSize=7.7, leading=9.5)))
    story.append(Paragraph("&bull; Founded, scaled, and negotiated acquisitions for leading digital infrastructure firms. Led cross-border joint ventures, technology licensing alliances, and strategic corporate partnerships across US and international markets.", bullet_style))
    story.append(Spacer(1, 1.5))
    
    story.append(Paragraph("<b>Venture Author &amp; Global Mentor</b> &mdash; <i>Founder Institute Alumnus (2014) &amp; Academic Textbook Author</i>", ParagraphStyle('Exp4', parent=body_style, fontName='Helvetica-Bold', fontSize=7.7, leading=9.5)))
    story.append(Paragraph("&bull; Authored authoritative university textbook on venture capital and enterprise creation. Mentored 5,000+ technology founders and operators; established active deal-sourcing pipelines across global venture ecosystems.", bullet_style))
    story.append(Spacer(1, 2.5))
    
    # 7. Education & Global Footprint
    story.append(Paragraph("EDUCATION, QUANTITATIVE FOUNDATION &amp; CREDENTIALS", section_title_style))
    edu_text = (
        "&bull; <b>Quantitative Foundation &amp; Systems:</b> Applied Mathematics &amp; Computer Science, Russian State University of Oil &amp; Gas.<br/>"
        "&bull; <b>Global Capital Network:</b> Founder Institute Silicon Valley Alumnus (2014); established relationships across US, European, and Asian VC and family offices.<br/>"
        "&bull; <b>Executive Communication:</b> Fluent English, native Russian; veteran negotiator across diverse regulatory, antitrust, and legal frameworks."
    )
    story.append(Paragraph(edu_text, bullet_style))
    
    doc.build(story, canvasmaker=InvariantCanvas)
    
    # Programmatic Layout & Collision Verification
    report = verify_layout_and_collisions(output_pdf)
    print(f"Programmatic verification: page_count={report['page_count']}, text_blocks={report['total_text_blocks']}, collisions={report['text_overlap_count']}, out_of_bounds={report['out_of_bounds_count']}")
    
    if report['page_count'] != 1:
        raise ValueError(f"CV is {report['page_count']} pages; must be exactly 1 page!")
    if report['text_overlap_count'] != 0:
        raise ValueError(f"Found {report['text_overlap_count']} text collisions: {report['overlaps']}")
    if report['out_of_bounds_count'] != 0:
        raise ValueError(f"Found {report['out_of_bounds_count']} blocks out of bounds!")
        
    print(f"Successfully generated 1-page CV: {output_pdf}")
    
    # Export 300 DPI HD PNG
    if output_png:
        doc_fitz = pymupdf.open(output_pdf)
        page = doc_fitz[0]
        zoom = 300 / 72  # 300 DPI
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        img.save(output_png, dpi=(300, 300))
        png_size = os.path.getsize(output_png)
        print(f"Successfully generated 300 DPI HD PNG: {output_png} ({png_size} bytes, ~{png_size / (1024*1024):.2f} MB)")
        doc_fitz.close()
    
    return output_pdf, output_png

if __name__ == "__main__":
    out_pdf = sys.argv[1] if len(sys.argv) > 1 else "cv-pavel-cherkashin-corpdev.pdf"
    out_png = sys.argv[2] if len(sys.argv) > 2 else "cv-pavel-cherkashin-corpdev-hd.png"
    build_pdf(out_pdf, out_png)
