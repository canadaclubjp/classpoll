import os
import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__, template_folder="../templates")

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///classpoll.db"
    )
    # Fix Heroku/Fly.io postgres:// -> postgresql://
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgres://"):
        app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
            "SQLALCHEMY_DATABASE_URI"
        ].replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["ADMIN_TOKEN"] = os.environ.get("ADMIN_TOKEN", "changeme")

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes_student import student_bp
    from .routes_admin import admin_bp

    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Create tables (for SQLite dev / first run)
    with app.app_context():
        db.create_all()

    @app.cli.command("purge-expired")
    def purge_expired():
        """Delete all polls (and cascaded rows) whose expiry has passed."""
        from .models import Poll

        all_polls = Poll.query.all()
        expired = [p for p in all_polls if p.is_expired()]
        count = len(expired)
        for poll in expired:
            db.session.delete(poll)
        db.session.commit()
        click.echo(f"Purged {count} expired poll(s).")

    return app
