import re
import secrets
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from models import Admin, db


api = Blueprint("api", __name__, url_prefix="/api")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def request_data():
    return request.get_json(silent=True) or request.form.to_dict()


def error(message, status=400):
    return jsonify({"status": "error", "error": message}), status


@api.route("/signup", methods=["POST"])
def signup():
    data = request_data()
    full_name = (data.get("full_name") or data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or data.get("confirmPassword") or ""

    if not full_name or not email or not password or not confirm_password:
        return error("All fields are required")
    if not EMAIL_RE.match(email):
        return error("Please enter a valid email address")
    if len(password) < 8:
        return error("Password must be at least 8 characters")
    if password != confirm_password:
        return error("Passwords do not match")
    if Admin.query.filter_by(email=email).first():
        return error("Account already exists", 409)

    admin = Admin(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(admin)
    db.session.commit()

    return jsonify({"status": "success", "message": "Account created successfully"}), 201


@api.route("/login", methods=["POST"])
def login():
    data = request_data()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    remember = bool(data.get("remember"))

    admin = Admin.query.filter_by(email=email).first()
    if not admin or not check_password_hash(admin.password_hash, password):
        return error("Invalid email or password", 401)

    login_user(admin, remember=remember)
    return jsonify({"status": "success", "admin": admin.to_dict()}), 200


@api.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return jsonify({"status": "success", "message": "Signed out successfully"}), 200


@api.route("/me", methods=["GET"])
def me():
    if not current_user.is_authenticated:
        return error("Authentication required", 401)
    return jsonify({"status": "success", "admin": current_user.to_dict()}), 200


@api.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request_data()
    email = (data.get("email") or "").strip().lower()
    admin = Admin.query.filter_by(email=email).first() if EMAIL_RE.match(email) else None

    if admin:
        token = secrets.token_urlsafe(32)
        admin.reset_token = token
        admin.reset_token_expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
        db.session.commit()
        print(f"Password reset link: http://localhost:5000/reset-password/{token}")

    return jsonify(
        {
            "status": "success",
            "message": "If that email exists, a password reset link has been generated.",
        }
    ), 200


@api.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    data = request_data()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or data.get("confirmPassword") or ""

    admin = Admin.query.filter_by(reset_token=token).first()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if not admin or not admin.reset_token_expires_at or admin.reset_token_expires_at < now:
        return error("Reset link is invalid or expired", 400)
    if len(password) < 8:
        return error("Password must be at least 8 characters")
    if password != confirm_password:
        return error("Passwords do not match")

    admin.password_hash = generate_password_hash(password)
    admin.reset_token = None
    admin.reset_token_expires_at = None
    db.session.commit()

    return jsonify({"status": "success", "message": "Password updated successfully"}), 200
