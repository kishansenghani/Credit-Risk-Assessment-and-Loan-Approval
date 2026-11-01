import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
from database import db



def create_app():
    app = Flask(__name__)

    # ── Config ──────────────────────────────────────────────────────────────
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(base_dir, 'database.db')}")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # ── Extensions ──────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # ── Blueprints ──────────────────────────────────────────────────────────
    from routes.auth import auth_bp
    from routes.predict import predict_bp
    from routes.applications import applications_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(applications_bp, url_prefix="/api")

    # ── DB init + demo seed ─────────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_demo_users()

    return app


def _seed_demo_users():
    """
    Create hardcoded demo accounts if they don't already exist.
    Credentials:
      - admin / admin123  (role: admin)
      - user  / user123   (role: user)
    """
    from routes.auth import User
    from werkzeug.security import generate_password_hash

    DEMO_USERS = [
        {"username": "admin", "password": "admin123", "role": "admin"},
        {"username": "user",  "password": "user123",  "role": "user"},
    ]

    for u in DEMO_USERS:
        if not User.query.filter_by(username=u["username"]).first():
            db.session.add(
                User(
                    username=u["username"],
                    password_hash=generate_password_hash(u["password"]),
                    role=u["role"],
                )
            )
    db.session.commit()


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
