from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Student

students_web = Blueprint("students_web", __name__)


@students_web.route("/students")
def students_page():
    students = Student.query.all()
    return render_template("students/list.html", students=students)


@students_web.route("/students/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")

        if not name or not email:
            flash("Name and email are required.")
            return redirect(url_for("students_web.add_student"))

        existing_student = Student.query.filter_by(email=email).first()

        if existing_student:
            flash("Student email already exists.")
            return redirect(url_for("students_web.add_student"))

        student = Student(name=name, email=email)

        db.session.add(student)
        db.session.commit()

        flash("Student added successfully!")

        return redirect(url_for("students_web.students_page"))

    return render_template("students/add.html")


@students_web.route("/students/<int:student_id>")
def view_student(student_id):

    student = Student.query.get_or_404(student_id)

    return render_template(
        "students/view.html",
        student=student
    )


@students_web.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):

    student = Student.query.get_or_404(student_id)

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")

        if not name or not email:
            flash("Name and email are required.")
            return redirect(
                url_for(
                    "students_web.edit_student",
                    student_id=student_id
                )
            )

        existing_student = Student.query.filter(
            Student.email == email,
            Student.id != student_id
        ).first()

        if existing_student:
            flash("Student email already exists.")
            return redirect(
                url_for(
                    "students_web.edit_student",
                    student_id=student_id
                )
            )

        student.name = name
        student.email = email

        db.session.commit()

        flash("Student updated successfully!")

        return redirect(url_for("students_web.students_page"))

    return render_template(
        "students/edit.html",
        student=student
    )


@students_web.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):

    student = Student.query.get_or_404(student_id)

    db.session.delete(student)
    db.session.commit()

    flash("Student deleted successfully!")

    return redirect(url_for("students_web.students_page"))