from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    reset_token = db.Column(db.String(255), nullable=True, index=True)
    reset_token_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    opportunities = db.relationship(
        "Opportunity",
        backref="creator",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
        }


class Opportunity(db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.String(80), nullable=False)
    start_date = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    future_opportunities = db.Column(db.Text, nullable=False)
    max_applicants = db.Column(db.Integer, nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration,
            "start_date": self.start_date,
            "description": self.description,
            "skills": [skill.strip() for skill in self.skills.split(",") if skill.strip()],
            "category": self.category,
            "future_opportunities": self.future_opportunities,
            "max_applicants": self.max_applicants,
        }
