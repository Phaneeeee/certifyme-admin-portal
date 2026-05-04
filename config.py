import os
import tempfile


DATA_DIR = os.path.join(tempfile.gettempdir(), "qatar_foundation_admin")
os.makedirs(DATA_DIR, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-this-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(DATA_DIR, "admin_portal.db"),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
