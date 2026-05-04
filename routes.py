import re

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

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
