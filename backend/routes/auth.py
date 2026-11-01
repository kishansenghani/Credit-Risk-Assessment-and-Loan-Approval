from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from database import db
import datetime

auth_bp = Blueprint("auth", __name__)

# ---------------------------------------------------------------------------
# Simple User model (inline for convenience – move to models.py if you grow)
# ---------------------------------------------------------------------------
from flask_sqlalchemy import SQLAlchemy

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user")   # "user" | "admin"
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
        }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/login  — authenticate a user and return a basic token."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # NOTE: Replace this demo token with JWT (flask-jwt-extended) in production
    token = f"demo-token-{user.id}-{user.role}"

    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    """POST /api/register  — create a new user account."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "user")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created", "user": user.to_dict()}), 201
