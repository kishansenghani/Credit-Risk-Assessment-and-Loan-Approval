from flask import Blueprint, request, jsonify
from routes.predict import LoanApplication
from database import db
from sqlalchemy import func

applications_bp = Blueprint("applications", __name__)

# ---------------------------------------------------------------------------
# Admin – list all loan applications (paginated, filtered)
# ---------------------------------------------------------------------------

@applications_bp.route("/applications", methods=["GET"])
def get_applications():
    """GET /api/applications — return all loan applications with optional filters."""
    page          = request.args.get("page", 1, type=int)
    per_page      = request.args.get("per_page", 20, type=int)
    status_filter = request.args.get("status")           # "Approved" | "Rejected"
    risk_filter   = request.args.get("risk_band")        # "Low" | "Medium" | "High"
    search        = request.args.get("search", "").strip()

    query = LoanApplication.query

    if status_filter:
        query = query.filter(LoanApplication.prediction == status_filter)

    if risk_filter:
        query = query.filter(LoanApplication.risk_band == risk_filter)

    if search:
        query = query.filter(LoanApplication.applicant_name.ilike(f"%{search}%"))

    paginated = query.order_by(LoanApplication.submitted_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "applications": [a.to_dict() for a in paginated.items],
        "total":        paginated.total,
        "pages":        paginated.pages,
        "current_page": page,
    }), 200


@applications_bp.route("/applications/<int:app_id>", methods=["GET"])
def get_application(app_id):
    """GET /api/applications/<id> — single application detail."""
    app_record = LoanApplication.query.get_or_404(app_id)
    return jsonify(app_record.to_dict()), 200


@applications_bp.route("/applications/<int:app_id>", methods=["DELETE"])
def delete_application(app_id):
    """DELETE /api/applications/<id> — remove an application (admin)."""
    app_record = LoanApplication.query.get_or_404(app_id)
    db.session.delete(app_record)
    db.session.commit()
    return jsonify({"message": f"Application {app_id} deleted"}), 200


# ---------------------------------------------------------------------------
# /api/analytics — rich breakdown charts for AdminDashboard
# ---------------------------------------------------------------------------

@applications_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """
    GET /api/analytics — returns:
      - overall KPIs
      - approval_by_property_area  (Urban/Semiurban/Rural)
      - approval_by_education      (Graduate / Not Graduate)
      - risk_band_distribution     (Low / Medium / High counts)
      - monthly_trend              (last 6 months application counts)
    """
    total    = LoanApplication.query.count()
    approved = LoanApplication.query.filter_by(prediction="Approved").count()
    rejected = LoanApplication.query.filter_by(prediction="Rejected").count()

    # ── Avg loan amounts ─────────────────────────────────────────────────────
    avg_approved = db.session.query(
        func.avg(LoanApplication.loan_amount)
    ).filter_by(prediction="Approved").scalar() or 0

    avg_rejected = db.session.query(
        func.avg(LoanApplication.loan_amount)
    ).filter_by(prediction="Rejected").scalar() or 0

    # ── Approval by Property Area ────────────────────────────────────────────
    area_rows = (
        db.session.query(
            LoanApplication.property_area,
            LoanApplication.prediction,
            func.count(LoanApplication.id).label("cnt"),
        )
        .group_by(LoanApplication.property_area, LoanApplication.prediction)
        .all()
    )
    area_map = {}
    for area, pred, cnt in area_rows:
        area = area or "Unknown"
        if area not in area_map:
            area_map[area] = {"area": area, "Approved": 0, "Rejected": 0}
        area_map[area][pred] = cnt
    approval_by_area = list(area_map.values())

    # ── Approval by Education ────────────────────────────────────────────────
    edu_rows = (
        db.session.query(
            LoanApplication.education,
            LoanApplication.prediction,
            func.count(LoanApplication.id).label("cnt"),
        )
        .group_by(LoanApplication.education, LoanApplication.prediction)
        .all()
    )
    edu_map = {}
    for edu, pred, cnt in edu_rows:
        edu = edu or "Unknown"
        if edu not in edu_map:
            edu_map[edu] = {"education": edu, "Approved": 0, "Rejected": 0}
        edu_map[edu][pred] = cnt
    approval_by_education = list(edu_map.values())

    # ── Risk Band Distribution ───────────────────────────────────────────────
    risk_rows = (
        db.session.query(
            LoanApplication.risk_band,
            func.count(LoanApplication.id).label("cnt"),
        )
        .group_by(LoanApplication.risk_band)
        .all()
    )
    risk_band_distribution = [
        {"risk_band": rb or "Unknown", "count": cnt}
        for rb, cnt in risk_rows
    ]

    # ── Monthly trend (last 6 months) ────────────────────────────────────────
    import datetime
    six_months_ago = datetime.datetime.utcnow() - datetime.timedelta(days=180)
    monthly_rows = (
        db.session.query(
            func.strftime("%Y-%m", LoanApplication.submitted_at).label("month"),
            func.count(LoanApplication.id).label("cnt"),
        )
        .filter(LoanApplication.submitted_at >= six_months_ago)
        .group_by("month")
        .order_by("month")
        .all()
    )
    monthly_trend = [{"month": m, "applications": cnt} for m, cnt in monthly_rows]

    return jsonify({
        "kpis": {
            "total":             total,
            "approved":          approved,
            "rejected":          rejected,
            "approval_rate":     round(approved / total * 100, 1) if total else 0,
            "avg_loan_approved": round(float(avg_approved), 2),
            "avg_loan_rejected": round(float(avg_rejected), 2),
        },
        "approval_by_area":      approval_by_area,
        "approval_by_education": approval_by_education,
        "risk_band_distribution": risk_band_distribution,
        "monthly_trend":         monthly_trend,
    }), 200
