from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    jwt.init_app(app)

    from app.models import User, Student, Course, Grade

    with app.app_context():
        db.create_all()

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.students import students_api
    app.register_blueprint(students_api)

    from app.routes.courses import courses_api
    app.register_blueprint(courses_api)

    from app.routes.grades import grades_api
    app.register_blueprint(grades_api)

    from app.routes.web_students import students_web
    app.register_blueprint(students_web)

    from app.routes.web_courses import courses_web
    app.register_blueprint(courses_web)

    from app.routes.web_grades import grades_web
    app.register_blueprint(grades_web)

    from app.routes.analytics import analytics_bp
    app.register_blueprint(analytics_bp)

    from flask import render_template

    @app.route("/")
    def home():
        return render_template("dashboard.html")

    return app