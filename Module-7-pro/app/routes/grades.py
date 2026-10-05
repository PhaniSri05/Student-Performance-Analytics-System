from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app import db
from app.models import Grade, Student, Course

grades_api = Blueprint(
    "grades_api",
    __name__,
    url_prefix="/api/grades"
)


def grade_to_dict(grade):
    return {
        "id": grade.id,
        "student_id": grade.student_id,
        "course_id": grade.course_id,
        "score": grade.score,
        "date": grade.date.isoformat()
    }


@grades_api.route("", methods=["GET"])
@jwt_required()
def get_grades():

    grades = Grade.query.all()

    return jsonify([
        grade_to_dict(grade)
        for grade in grades
    ]), 200


@grades_api.route("", methods=["POST"])
@jwt_required()
def create_grade():

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    student_id = data.get("student_id")
    course_id = data.get("course_id")
    score = data.get("score")

    if student_id is None or course_id is None or score is None:
        return jsonify({
            "message": "student_id, course_id and score are required"
        }), 400

    if not 0 <= float(score) <= 100:
        return jsonify({
            "message": "Score must be between 0 and 100"
        }), 400

    student = db.session.get(Student, student_id)
    course = db.session.get(Course, course_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    grade = Grade(
        student_id=student_id,
        course_id=course_id,
        score=float(score)
    )

    db.session.add(grade)
    db.session.commit()

    return jsonify({
        "message": "Grade created successfully",
        "grade": grade_to_dict(grade)
    }), 201


@grades_api.route("/<int:grade_id>", methods=["GET"])
@jwt_required()
def get_grade(grade_id):

    grade = db.session.get(Grade, grade_id)

    if not grade:
        return jsonify({
            "message": "Grade not found"
        }), 404

    return jsonify(
        grade_to_dict(grade)
    ), 200


@grades_api.route("/<int:grade_id>", methods=["PUT"])
@jwt_required()
def update_grade(grade_id):

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    grade = db.session.get(Grade, grade_id)

    if not grade:
        return jsonify({
            "message": "Grade not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    student_id = data.get("student_id")
    course_id = data.get("course_id")
    score = data.get("score")

    if student_id is None or course_id is None or score is None:
        return jsonify({
            "message": "student_id, course_id and score are required"
        }), 400

    if not 0 <= float(score) <= 100:
        return jsonify({
            "message": "Score must be between 0 and 100"
        }), 400

    if not db.session.get(Student, student_id):
        return jsonify({
            "message": "Student not found"
        }), 404

    if not db.session.get(Course, course_id):
        return jsonify({
            "message": "Course not found"
        }), 404

    grade.student_id = student_id
    grade.course_id = course_id
    grade.score = float(score)

    db.session.commit()

    return jsonify({
        "message": "Grade updated successfully",
        "grade": grade_to_dict(grade)
    }), 200


@grades_api.route("/<int:grade_id>", methods=["PATCH"])
@jwt_required()
def patch_grade(grade_id):

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    grade = db.session.get(Grade, grade_id)

    if not grade:
        return jsonify({
            "message": "Grade not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    if "student_id" in data:
        if not db.session.get(Student, data["student_id"]):
            return jsonify({
                "message": "Student not found"
            }), 404
        grade.student_id = data["student_id"]

    if "course_id" in data:
        if not db.session.get(Course, data["course_id"]):
            return jsonify({
                "message": "Course not found"
            }), 404
        grade.course_id = data["course_id"]

    if "score" in data:
        if not 0 <= float(data["score"]) <= 100:
            return jsonify({
                "message": "Score must be between 0 and 100"
            }), 400
        grade.score = float(data["score"])

    db.session.commit()

    return jsonify({
        "message": "Grade partially updated",
        "grade": grade_to_dict(grade)
    }), 200


@grades_api.route("/<int:grade_id>", methods=["DELETE"])
@jwt_required()
def delete_grade(grade_id):

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    grade = db.session.get(Grade, grade_id)

    if not grade:
        return jsonify({
            "message": "Grade not found"
        }), 404

    db.session.delete(grade)
    db.session.commit()

    return jsonify({
        "message": "Grade deleted successfully"
    }), 200