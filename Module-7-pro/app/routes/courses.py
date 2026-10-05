from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models import Course

courses_api = Blueprint(
    "courses_api",
    __name__,
    url_prefix="/api/courses"
)


def course_to_dict(course):
    return {
        "id": course.id,
        "name": course.name,
        "code": course.code
    }


@courses_api.route("", methods=["GET"])
@jwt_required()
def get_courses():
    courses = Course.query.all()

    return jsonify([
        course_to_dict(course)
        for course in courses
    ]), 200


@courses_api.route("", methods=["POST"])
@jwt_required()
def create_course():

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
    code = data.get("code")

    if not name or not code:
        return jsonify({
            "message": "Name and code are required"
        }), 400

    existing_course = Course.query.filter_by(
        code=code
    ).first()

    if existing_course:
        return jsonify({
            "message": "Course code already exists"
        }), 409

    course = Course(
        name=name,
        code=code
    )

    db.session.add(course)
    db.session.commit()

    return jsonify({
        "message": "Course created successfully",
        "course": course_to_dict(course)
    }), 201


@courses_api.route("/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course(course_id):

    course = db.session.get(Course, course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    return jsonify(
        course_to_dict(course)
    ), 200


@courses_api.route("/<int:course_id>", methods=["PUT"])
@jwt_required()
def update_course(course_id):

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    course = db.session.get(Course, course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    code = data.get("code")

    if not name or not code:
        return jsonify({
            "message": "Name and code are required"
        }), 400

    course.name = name
    course.code = code

    db.session.commit()

    return jsonify({
        "message": "Course updated successfully",
        "course": course_to_dict(course)
    }), 200


@courses_api.route("/<int:course_id>", methods=["PATCH"])
@jwt_required()
def patch_course(course_id):

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    course = db.session.get(Course, course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON data is required"
        }), 400

    if "name" in data:
        course.name = data["name"]

    if "code" in data:
        course.code = data["code"]

    db.session.commit()

    return jsonify({
        "message": "Course partially updated",
        "course": course_to_dict(course)
    }), 200


@courses_api.route("/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    course = db.session.get(Course, course_id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    db.session.delete(course)
    db.session.commit()

    return jsonify({
        "message": "Course deleted successfully"
    }), 200