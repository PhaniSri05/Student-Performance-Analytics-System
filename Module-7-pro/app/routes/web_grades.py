from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import db
from app.models import Grade, Student, Course


grades_web = Blueprint("grades_web", __name__)


@grades_web.route("/grades")
def grades_page():

    grades = Grade.query.all()

    return render_template(
        "grades/list.html",
        grades=grades
    )


@grades_web.route("/grades/add", methods=["GET", "POST"])
def add_grade():

    students = Student.query.all()
    courses = Course.query.all()

    if request.method == "POST":

        student_id = request.form.get("student_id")
        course_id = request.form.get("course_id")
        score = request.form.get("score")

        if not student_id or not course_id or score is None:
            flash("All fields are required.")
            return redirect(url_for("grades_web.add_grade"))

        try:
            score = float(score)
        except ValueError:
            flash("Score must be a number.")
            return redirect(url_for("grades_web.add_grade"))

        if score < 0 or score > 100:
            flash("Score must be between 0 and 100.")
            return redirect(url_for("grades_web.add_grade"))

        student = Student.query.get(student_id)
        course = Course.query.get(course_id)

        if not student:
            flash("Student not found.")
            return redirect(url_for("grades_web.add_grade"))

        if not course:
            flash("Course not found.")
            return redirect(url_for("grades_web.add_grade"))

        grade = Grade(
            student_id=student.id,
            course_id=course.id,
            score=score
        )

        db.session.add(grade)
        db.session.commit()

        flash("Grade added successfully!")

        return redirect(url_for("grades_web.grades_page"))

    return render_template(
        "grades/add.html",
        students=students,
        courses=courses
    )


@grades_web.route("/grades/<int:grade_id>/edit", methods=["GET", "POST"])
def edit_grade(grade_id):

    grade = Grade.query.get_or_404(grade_id)

    students = Student.query.all()
    courses = Course.query.all()

    if request.method == "POST":

        student_id = request.form.get("student_id")
        course_id = request.form.get("course_id")
        score = request.form.get("score")

        if not student_id or not course_id or score is None:
            flash("All fields are required.")
            return redirect(
                url_for("grades_web.edit_grade", grade_id=grade_id)
            )

        try:
            score = float(score)
        except ValueError:
            flash("Score must be a number.")
            return redirect(
                url_for("grades_web.edit_grade", grade_id=grade_id)
            )

        if score < 0 or score > 100:
            flash("Score must be between 0 and 100.")
            return redirect(
                url_for("grades_web.edit_grade", grade_id=grade_id)
            )

        student = Student.query.get(student_id)
        course = Course.query.get(course_id)

        if not student or not course:
            flash("Invalid student or course.")
            return redirect(
                url_for("grades_web.edit_grade", grade_id=grade_id)
            )

        grade.student_id = student.id
        grade.course_id = course.id
        grade.score = score

        db.session.commit()

        flash("Grade updated successfully!")

        return redirect(url_for("grades_web.grades_page"))

    return render_template(
        "grades/edit.html",
        grade=grade,
        students=students,
        courses=courses
    )


@grades_web.route("/grades/<int:grade_id>/delete", methods=["POST"])
def delete_grade(grade_id):

    grade = Grade.query.get_or_404(grade_id)

    db.session.delete(grade)
    db.session.commit()

    flash("Grade deleted successfully!")

    return redirect(url_for("grades_web.grades_page"))