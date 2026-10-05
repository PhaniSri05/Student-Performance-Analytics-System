from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app import db
from app.models import Student, User

students_api = Blueprint(
    "students_api",
    __name__,
    url_prefix="/api/students"
)


def student_to_dict(student):
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email
    }


@students_api.route("", methods=["POST"])
@jwt_required()
def create_student():

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

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({
            "message": "Name and email are required"
        }), 400

    existing_student = Student.query.filter_by(
        email=email
    ).first()

    if existing_student:
        return jsonify({
            "message": "Student email already exists"
        }), 409

    student = Student(
        name=name,
        email=email
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({
        "message": "Student created successfully",
        "student": student_to_dict(student)
    }), 201


@students_api.route("/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):

    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    claims = get_jwt()
    identity = get_jwt_identity()

    if claims.get("role") == "student":

        user = User.query.get(int(identity))

        if not user or student.email != user.email:
            return jsonify({
                "message": "You can only view your own student data"
            }), 403

    return jsonify(
        student_to_dict(student)
    ), 200


@students_api.route("/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id):

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({
            "message": "Name and email are required"
        }), 400

    student.name = name
    student.email = email

    db.session.commit()

    return jsonify({
        "message": "Student updated successfully",
        "student": student_to_dict(student)
    }), 200


@students_api.route("/<int:student_id>", methods=["PATCH"])
@jwt_required()
def patch_student(student_id):

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    if "name" in data:
        student.name = data["name"]

    if "email" in data:
        student.email = data["email"]

    db.session.commit()

    return jsonify({
        "message": "Student partially updated",
        "student": student_to_dict(student)
    }), 200


@students_api.route("/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    student = db.session.get(Student, student_id)

    if not student:
        return jsonify({
            "message": "Student not found"
        }), 404

    db.session.delete(student)
    db.session.commit()

    return jsonify({
        "message": "Student deleted successfully"
    }), 200

@students_api.route("", methods=["GET"])
@jwt_required()
def get_students():

    claims = get_jwt()
    identity = get_jwt_identity()

    if claims.get("role") == "student":

        user = User.query.get(int(identity))

        if not user:
            return jsonify({"message": "User not found"}), 404

        student = Student.query.filter_by(email=user.email).first()

        if not student:
            return jsonify({"message": "Student profile not found"}), 404

        return jsonify([student_to_dict(student)]), 200

    students = Student.query.all()

    return jsonify([
        student_to_dict(student)
        for student in students
    ]), 200