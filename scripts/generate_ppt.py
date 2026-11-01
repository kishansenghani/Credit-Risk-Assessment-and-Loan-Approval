import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="Loan_Risk_Analysis_Presentation.pptx"):
    prs = Presentation()
    # 16:9 widescreen slides
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Professional color palette (Fintech Dark/Modern Navy theme)
    COLOR_BG = RGBColor(15, 23, 42)         # #0f172a (Deep Slate/Navy)
    COLOR_CARD = RGBColor(30, 41, 59)       # #1e293b (Slate Card)
    COLOR_ACCENT = RGBColor(99, 102, 241)   # #6366f1 (Indigo/Purple Accent)
    COLOR_CYAN = RGBColor(6, 182, 212)      # #06b6d4 (Cyan Highlight)
    COLOR_GREEN = RGBColor(16, 185, 129)    # #10b981 (Success/Approved Green)
    COLOR_TEXT = RGBColor(241, 245, 249)     # #f1f5f9 (Off-white)
    COLOR_MUTED = RGBColor(148, 163, 184)   # #94a3b8 (Muted Gray)

    def set_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category="LOANIQ — DATA SCIENCE & MACHINE LEARNING PROJECT"):
        # Category / breadcrumb
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_CYAN

        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(28)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_TEXT

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_background(s1)

    # Accent decorative box
    deco = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.2), Inches(3.2), Inches(0.4))
    deco.fill.solid()
    deco.fill.fore_color.rgb = RGBColor(49, 46, 129)
    deco.line.color.rgb = COLOR_ACCENT
    deco_tf = deco.text_frame
    deco_p = deco_tf.paragraphs[0]
    deco_p.alignment = PP_ALIGN.CENTER
    deco_p.text = "COLLEGE CAPSTONE PROJECT"
    deco_p.font.size = Pt(11)
    deco_p.font.bold = True
    deco_p.font.color.rgb = RGBColor(199, 210, 254)

    # Main Project Title
    tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Loan Risk Analysis (LoanIQ)"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "AI-Powered Credit Risk Assessment & Loan Approval with Explainable AI (SHAP)"
    p1_sub.font.size = Pt(20)
    p1_sub.font.color.rgb = COLOR_CYAN
    p1_sub.space_before = Pt(12)

    # Presenter Details Card
    card_info = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.3))
    card_info.fill.solid()
    card_info.fill.fore_color.rgb = COLOR_CARD
    card_info.line.color.rgb = RGBColor(51, 65, 85)

    tb_info = s1.shapes.add_textbox(Inches(1.2), Inches(4.5), Inches(10.9), Inches(1.9))
    tf_info = tb_info.text_frame
    tf_info.word_wrap = True

    p_name_lbl = tf_info.paragraphs[0]
    p_name_lbl.text = "Presented By:"
    p_name_lbl.font.size = Pt(13)
    p_name_lbl.font.color.rgb = COLOR_MUTED

    p_name = tf_info.add_paragraph()
    p_name.text = "[Your Name / Student Name]"
    p_name.font.size = Pt(22)
    p_name.font.bold = True
    p_name.font.color.rgb = COLOR_TEXT
    p_name.space_before = Pt(4)

    p_meta = tf_info.add_paragraph()
    p_meta.text = "Roll No: [Your Roll Number]   |   Degree: B.Tech / B.E. / M.Sc. in Computer Science / Data Science\nCollege: [Your College / University Name]   |   Academic Year: 2026-2027"
    p_meta.font.size = Pt(13)
    p_meta.font.color.rgb = COLOR_MUTED
    p_meta.space_before = Pt(6)

    # =========================================================================
    # SLIDE 2: Project Overview
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_background(s2)
    add_header(s2, "Project Overview: Problem, Solution & Value")

    cards_data_s2 = [
        ("The Industry Problem", 
         ["Manual loan evaluation takes days to weeks with human bias and operational inefficiency.",
          "High Non-Performing Assets (NPAs) caused by subjective credit underwriting.",
          "Existing AI models are 'Black Boxes' that fail to explain why a loan is rejected."],
         RGBColor(239, 68, 68)), # Red Accent
        ("Our Solution: LoanIQ", 
         ["Automated real-time credit decision system driven by machine learning.",
          "Feature engineering: computes Debt-to-Income (DTI) & Loan-to-Income (LTI) ratios.",
          "SMOTE balancing to accurately distinguish high-risk minority defaults."],
         COLOR_ACCENT),
        ("Key Innovations & Impact", 
         ["Explainable AI (SHAP): Provides Top 3 decision drivers + full feature importance.",
          "3-Tier Risk Bands: Segregates applicants into Low, Medium, and High Risk.",
          "Achieved 82.93% Accuracy, 87.21% Precision, and 88.24% Recall on holdout test set."],
         COLOR_GREEN),
    ]

    left_start = Inches(0.8)
    card_width = Inches(3.64)
    gap = Inches(0.4)

    for i, (title, points, accent_col) in enumerate(cards_data_s2):
        pos_x = left_start + i * (card_width + gap)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pos_x, Inches(1.7), card_width, Inches(5.1))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = accent_col

        tb = s2.shapes.add_textbox(pos_x + Inches(0.25), Inches(1.9), card_width - Inches(0.5), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(18)
        p_t.font.bold = True
        p_t.font.color.rgb = accent_col

        for pt_text in points:
            p_pt = tf.add_paragraph()
            p_pt.text = "• " + pt_text
            p_pt.font.size = Pt(13)
            p_pt.font.color.rgb = COLOR_TEXT
            p_pt.space_before = Pt(12)

    # =========================================================================
    # SLIDE 3: How to Use this Project
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_background(s3)
    add_header(s3, "How to Use This Project (Applicant & Admin Workflows)")

    # Box 1: Applicant Workflow (Left)
    card_user = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(5.66), Inches(5.1))
    card_user.fill.solid()
    card_user.fill.fore_color.rgb = COLOR_CARD
    card_user.line.color.rgb = COLOR_CYAN

    tb_u = s3.shapes.add_textbox(Inches(1.05), Inches(1.9), Inches(5.16), Inches(4.7))
    tf_u = tb_u.text_frame
    tf_u.word_wrap = True

    pu_title = tf_u.paragraphs[0]
    pu_title.text = "👤 Applicant / Borrower Workflow"
    pu_title.font.size = Pt(18)
    pu_title.font.bold = True
    pu_title.font.color.rgb = COLOR_CYAN

    user_steps = [
        ("1. Secure Login / Register", "Borrowers sign in or create an account with encrypted credentials."),
        ("2. Enter Financial & Demographic Data", "Fill out 12 key parameters including Income, Co-applicant Income, Loan Term, and Credit History."),
        ("3. Instant AI Credit Decision", "Within milliseconds, view Approved / Rejected verdict with AI Confidence score."),
        ("4. Transparent Risk Band & SHAP Explanations", "View 🟢 Low, 🟡 Medium, or 🔴 High Risk badge, along with Top 3 reasons explaining why."),
    ]
    for step_h, step_b in user_steps:
        p_h = tf_u.add_paragraph()
        p_h.text = "• " + step_h
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_TEXT
        p_h.space_before = Pt(10)

        p_b = tf_u.add_paragraph()
        p_b.text = "   " + step_b
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = COLOR_MUTED
        p_b.space_before = Pt(2)

    # Box 2: Admin / Loan Officer Workflow (Right)
    card_admin = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.86), Inches(1.7), Inches(5.66), Inches(5.1))
    card_admin.fill.solid()
    card_admin.fill.fore_color.rgb = COLOR_CARD
    card_admin.line.color.rgb = COLOR_ACCENT

    tb_a = s3.shapes.add_textbox(Inches(7.11), Inches(1.9), Inches(5.16), Inches(4.7))
    tf_a = tb_a.text_frame
    tf_a.word_wrap = True

    pa_title = tf_a.paragraphs[0]
    pa_title.text = "🛡️ Loan Officer / Admin Workflow"
    pa_title.font.size = Pt(18)
    pa_title.font.bold = True
    pa_title.font.color.rgb = COLOR_ACCENT

    admin_steps = [
        ("1. Executive Analytics Dashboard", "Review high-level KPIs: Total Applications, Approval Rate, and Average Approved vs. Rejected Loan Amount."),
        ("2. Real-Time Portfolio Visualizations", "Monitor interactive Recharts: Approval by Property Area (Urban/Semiurban/Rural), Education, and Monthly Trends."),
        ("3. Application Management Table", "Filter by approval status, risk band, or live search by applicant name with pagination."),
        ("4. Application Drilldown Modal", "Inspect full feature vector and individual SHAP waterfall values for auditing and regulatory compliance."),
    ]
    for step_h, step_b in admin_steps:
        p_h = tf_a.add_paragraph()
        p_h.text = "• " + step_h
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_TEXT
        p_h.space_before = Pt(10)

        p_b = tf_a.add_paragraph()
        p_b.text = "   " + step_b
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = COLOR_MUTED
        p_b.space_before = Pt(2)

    # =========================================================================
    # SLIDE 4: Tech Stack
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_background(s4)
    add_header(s4, "System Architecture & Technology Stack")

    tech_pillars = [
        ("Frontend Layer", "User & Admin Interfaces",
         ["React 18 (Component-driven SPA)",
          "Vite (Lightning-fast dev tooling)",
          "Recharts (Interactive Charts)",
          "Axios (JWT/Bearer Interceptors)",
          "Responsive Dark Theme (CSS3)"],
         COLOR_CYAN),
        ("Backend Layer", "REST API & Business Logic",
         ["Python 3.13 + Flask 3",
          "Application Factory & Blueprints",
          "Flask-SQLAlchemy (ORM)",
          "Flask-CORS (Cross-Origin Access)",
          "Werkzeug Password Hashing"],
         COLOR_ACCENT),
        ("Database Layer", "Relational Persistence",
         ["SQLite Database Engine",
          "Users Table (Authentication & RBAC)",
          "Loan Applications Table",
          "Audit Trail (Timestamps & Status)",
          "JSON serialization for SHAP logs"],
         RGBColor(245, 158, 11)), # Amber
        ("Machine Learning & XAI", "Core Intelligence Engine",
         ["XGBoost Classifier (Tuned)",
          "Scikit-Learn (Pipelines, GridSearch)",
          "SMOTE (Class Balancing)",
          "SHAP (TreeExplainer Attribution)",
          "Pandas, NumPy, Joblib serialization"],
         COLOR_GREEN),
    ]

    t_start = Inches(0.8)
    t_width = Inches(2.7)
    t_gap = Inches(0.3)

    for i, (layer_name, sub, items, col) in enumerate(tech_pillars):
        t_x = t_start + i * (t_width + t_gap)
        c = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, t_x, Inches(1.7), t_width, Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD
        c.line.color.rgb = col

        tb = s4.shapes.add_textbox(t_x + Inches(0.15), Inches(1.85), t_width - Inches(0.3), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p_l = tf.paragraphs[0]
        p_l.text = layer_name
        p_l.font.size = Pt(17)
        p_l.font.bold = True
        p_l.font.color.rgb = col

        p_s = tf.add_paragraph()
        p_s.text = sub
        p_s.font.size = Pt(11)
        p_s.font.color.rgb = COLOR_MUTED
        p_s.space_before = Pt(2)

        for it in items:
            p_i = tf.add_paragraph()
            p_i.text = "• " + it
            p_i.font.size = Pt(12)
            p_i.font.color.rgb = COLOR_TEXT
            p_i.space_before = Pt(10)

    # =========================================================================
    # SLIDE 5: Future Scope
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_background(s5)
    add_header(s5, "Future Enhancements & Scalability Roadmap")

    future_items = [
        ("1. Real-Time Credit Bureau Integration", 
         "Integrate REST APIs with national credit bureaus (e.g., CIBIL, Experian, Equifax) for instant, live credit history pulling instead of user self-reporting.",
         COLOR_CYAN),
        ("2. Alternative Data & NLP Bank Statement Analysis", 
         "Incorporate Open Banking / Account Aggregators (RBI AA ecosystem) to automatically analyze UPI transactions, tax filings (GST/ITR), and cash-flow statements.",
         COLOR_ACCENT),
        ("3. Continuous MLOps & Model Retraining", 
         "Deploy an automated MLOps pipeline using MLflow and Airflow for continuous concept drift detection, data drift monitoring, and scheduled retraining.",
         COLOR_GREEN),
        ("4. Enterprise Security & Dynamic Counterfactuals", 
         "Implement JWT / OAuth2 with Two-Factor Authentication (2FA) and provide applicants with counterfactual explanations (e.g., 'If your DTI reduces by 10%, your loan will be approved').",
         RGBColor(245, 158, 11)),
    ]

    for i, (h, desc, col) in enumerate(future_items):
        y_pos = Inches(1.7) + i * Inches(1.28)
        card_f = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y_pos, Inches(11.7), Inches(1.15))
        card_f.fill.solid()
        card_f.fill.fore_color.rgb = COLOR_CARD
        card_f.line.color.rgb = col

        tb_f = s5.shapes.add_textbox(Inches(1.05), y_pos + Inches(0.12), Inches(11.2), Inches(0.9))
        tf_f = tb_f.text_frame
        tf_f.word_wrap = True

        p_fh = tf_f.paragraphs[0]
        p_fh.text = h
        p_fh.font.size = Pt(16)
        p_fh.font.bold = True
        p_fh.font.color.rgb = col

        p_fd = tf_f.add_paragraph()
        p_fd.text = desc
        p_fd.font.size = Pt(12)
        p_fd.font.color.rgb = COLOR_TEXT
        p_fd.space_before = Pt(3)

    # =========================================================================
    # SLIDE 6: Thank You
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_background(s6)

    tb6 = s6.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.3), Inches(4.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    p6_t = tf6.paragraphs[0]
    p6_t.alignment = PP_ALIGN.CENTER
    p6_t.text = "Thank You!"
    p6_t.font.size = Pt(56)
    p6_t.font.bold = True
    p6_t.font.color.rgb = COLOR_TEXT

    p6_tag = tf6.add_paragraph()
    p6_tag.alignment = PP_ALIGN.CENTER
    p6_tag.text = "“Empowering Financial Lending with Fair, Fast, and Explainable AI”"
    p6_tag.font.size = Pt(20)
    p6_tag.font.italic = True
    p6_tag.font.color.rgb = COLOR_CYAN
    p6_tag.space_before = Pt(14)

    p6_qa = tf6.add_paragraph()
    p6_qa.alignment = PP_ALIGN.CENTER
    p6_qa.text = "Questions & Answers (Q&A)"
    p6_qa.font.size = Pt(24)
    p6_qa.font.bold = True
    p6_qa.font.color.rgb = COLOR_ACCENT
    p6_qa.space_before = Pt(24)

    p6_contact = tf6.add_paragraph()
    p6_contact.alignment = PP_ALIGN.CENTER
    p6_contact.text = "Open for Discussion & Evaluation\nProject Repository: Loan_Risk_Analysis"
    p6_contact.font.size = Pt(13)
    p6_contact.font.color.rgb = COLOR_MUTED
    p6_contact.space_before = Pt(12)

    prs.save(output_path)
    print(f"Presentation generated successfully: {output_path}")

if __name__ == "__main__":
    out = "e:/Loan_Risk_Analysis/Loan_Risk_Analysis_Presentation.pptx"
    create_deck(out)

