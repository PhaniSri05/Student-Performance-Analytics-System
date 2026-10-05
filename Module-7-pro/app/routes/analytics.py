from flask import Blueprint, render_template, request, redirect, send_file
import pandas as pd
import numpy as np

from app.models import Grade, Student, Course
import os
from werkzeug.utils import secure_filename
from flask import send_file
from app import db

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(REPORTS_DIR, exist_ok=True)

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
def analytics():

    grades = Grade.query.all()

    data = []

    for grade in grades:
        data.append({
            "student": grade.student.name,
            "course": grade.course.name,
            "score": grade.score
        })

    df = pd.DataFrame(data)

    if df.empty:
        return render_template(
            "analytics.html",
            empty=True
        )

    # Optional course filter
    selected_course = request.args.get("course")

    if selected_course:
        df = df[df["course"] == selected_course]

    # Basic statistics
    average = round(df["score"].mean(), 2)
    median = round(df["score"].median(), 2)
    std_dev = round(np.std(df["score"]), 2)

    # Course averages
    course_averages = (
        df.groupby("course")["score"]
        .mean()
        .round(2)
        .to_dict()
    )

    # Student rankings
    rankings = (
        df.groupby("student")["score"]
        .mean()
        .sort_values(ascending=False)
        .round(2)
        .to_dict()
    )

    courses = Course.query.all()

    return render_template(
        "analytics.html",
        empty=False,
        average=average,
        median=median,
        std_dev=std_dev,
        course_averages=course_averages,
        rankings=rankings,
        courses=courses,
        selected_course=selected_course
    )

@analytics_bp.route("/grades/upload", methods=["GET", "POST"])
def upload_grades():

    if request.method == "POST":

        file = request.files.get("file")

        if not file or file.filename == "":
            return "No file selected", 400

        filename = secure_filename(file.filename)

        if not filename.lower().endswith(".csv"):
            return "Only CSV files are allowed", 400

        filepath = os.path.join("uploads", filename)

        file.save(filepath)

        try:
            df = pd.read_csv(filepath)

            required_columns = {
                "student_id",
                "course_id",
                "score"
            }

            if not required_columns.issubset(df.columns):
                return (
                    "CSV must contain student_id, course_id and score",
                    400
                )

            for _, row in df.iterrows():

                student = Student.query.get(int(row["student_id"]))
                course = Course.query.get(int(row["course_id"]))

                if not student or not course:
                    continue

                score = float(row["score"])

                if score < 0 or score > 100:
                    continue

                grade = Grade(
                    student_id=student.id,
                    course_id=course.id,
                    score=score
                )

                db.session.add(grade)

            db.session.commit()

            return redirect("/grades")

        except Exception as e:

            db.session.rollback()

            return f"Upload failed: {str(e)}", 400

    return render_template("grades/upload.html")

@analytics_bp.route("/grades/export/csv")
def export_csv():

    grades = Grade.query.all()

    data = []

    for grade in grades:
        data.append({
            "student_id": grade.student_id,
            "student_name": grade.student.name,
            "course_id": grade.course_id,
            "course_name": grade.course.name,
            "score": grade.score,
            "date": grade.date
        })

    df = pd.DataFrame(data)

    filepath = os.path.join(REPORTS_DIR, "grades_report.csv")

    df.to_csv(filepath, index=False)

    return send_file(
        filepath,
        as_attachment=True,
        download_name="grades_report.csv"
    )


@analytics_bp.route("/grades/export/excel")
def export_excel():

    grades = Grade.query.all()

    data = []

    for grade in grades:
        data.append({
            "student_id": grade.student_id,
            "student_name": grade.student.name,
            "course_id": grade.course_id,
            "course_name": grade.course.name,
            "score": grade.score,
            "date": grade.date
        })

    df = pd.DataFrame(data)

    filepath = os.path.join(REPORTS_DIR, "grades_report.xlsx")

    df.to_excel(filepath, index=False)

    return send_file(
        filepath,
        as_attachment=True,
        download_name="grades_report.xlsx"
    )