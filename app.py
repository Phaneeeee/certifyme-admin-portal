from flask import Flask, send_from_directory
from flask_login import LoginManager

from config import Config
from models import Admin, db
from routes import api


login_manager = LoginManager()


def create_app():
    app = Flask(__name__, static_folder="sky", static_url_path="")
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(api)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Admin, int(user_id))

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "admin.html")

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
