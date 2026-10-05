from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Course

courses_web = Blueprint("courses_web", __name__)


@courses_web.route("/courses")
def courses_page():
    courses = Course.query.all()
    return render_template("courses/list.html", courses=courses)


@courses_web.route("/courses/add", methods=["GET", "POST"])
def add_course():

    if request.method == "POST":

        name = request.form.get("name")
        code = request.form.get("code")

        if not name or not code:
            flash("Course name and code are required.")
            return redirect(url_for("courses_web.add_course"))

        existing_course = Course.query.filter_by(code=code).first()

        if existing_course:
            flash("Course code already exists.")
            return redirect(url_for("courses_web.add_course"))

        course = Course(name=name, code=code)

        db.session.add(course)
        db.session.commit()

        flash("Course added successfully!")

        return redirect(url_for("courses_web.courses_page"))

    return render_template("courses/add.html")


@courses_web.route("/courses/<int:course_id>")
def view_course(course_id):

    course = Course.query.get_or_404(course_id)

    return render_template(
        "courses/view.html",
        course=course
    )


@courses_web.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
def edit_course(course_id):

    course = Course.query.get_or_404(course_id)

    if request.method == "POST":

        name = request.form.get("name")
        code = request.form.get("code")

        if not name or not code:
            flash("Course name and code are required.")
            return redirect(
                url_for(
                    "courses_web.edit_course",
                    course_id=course_id
                )
            )

        existing_course = Course.query.filter(
            Course.code == code,
            Course.id != course_id
        ).first()

        if existing_course:
            flash("Course code already exists.")
            return redirect(
                url_for(
                    "courses_web.edit_course",
                    course_id=course_id
                )
            )

        course.name = name
        course.code = code

        db.session.commit()

        flash("Course updated successfully!")

        return redirect(url_for("courses_web.courses_page"))

    return render_template(
        "courses/edit.html",
        course=course
    )


@courses_web.route("/courses/<int:course_id>/delete", methods=["POST"])
def delete_course(course_id):

    course = Course.query.get_or_404(course_id)

    db.session.delete(course)
    db.session.commit()

    flash("Course deleted successfully!")

    return redirect(url_for("courses_web.courses_page"))