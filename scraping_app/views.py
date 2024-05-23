from flask import jsonify, request, Blueprint
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt
)
from http import HTTPStatus
from models import db, Process, User
from sqlalchemy import and_

views = Blueprint("views", __name__)

# create set of revoked tokens
blacklist = set()

# Login Process


@views.route("/api/v1/login", methods=["POST"])
def login():
    try:
        request_username = request.json.get("username")
        request_password = request.json.get("password")
        user = User.query.filter(
            and_(User.username == request_username,
                 User.password == request_password)
        ).first()
        if not user:
            error = "Bad username or password"
            return jsonify(
                {"message": error}), HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=request_username)
        user.token = access_token
        db.session.commit()
        return jsonify(access_token=access_token), HTTPStatus.CREATED
    except Exception as error:
        return jsonify({"error": str(error)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        db.session.close()

# Logout Process


@views.route("/api/v1/logout", methods=['DELETE'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()['jti']
        blacklist.add(jti)
        return jsonify(message="Access token revoked"), HTTPStatus.OK
    except Exception as error:
        return jsonify({"error": str(error)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        db.session.close()

# Get all the Scraping information


@views.route("/api/v1/get_scraping", methods=["GET"])
@jwt_required()
def get_scraping():
    # Validate token session
    jti = get_jwt()['jti']
    if jti in blacklist:
        message = "Unauthorized. The session token has expired or is invalid."
        return jsonify(
            message=message), HTTPStatus.UNAUTHORIZED
    try:
        process = Process.query.all()
        results = [
            {
                "id": proces.id,
                "date_of_entry": proces.date_of_entry,
                "process_number": proces.process_number,
                "action_infraction": proces.action_infraction,
                "details": [
                    {
                        "incident_number": detail.incident_number,
                        "date": detail.date,
                        "offended_actors": detail.offended_actors,
                        "defendants": detail.defendants,
                    } for detail in proces.details
                ]
            } for proces in process
        ]
        return jsonify(results), HTTPStatus.OK
    except Exception as error:
        return jsonify({"error": str(error)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        db.session.close()


@views.route("/api/v1/create_user", methods=["POST"])
@jwt_required()
def create_user():
    # Validate token session
    jti = get_jwt()['jti']
    if jti in blacklist:
        message = "Unauthorized. The session token has expired or is invalid."
        return jsonify(
            message=message), HTTPStatus.UNAUTHORIZED
    try:
        request_username = request.json.get("username")
        request_password = request.json.get("password")
        user = User.query.filter(
            and_(User.username == request_username,
                 User.password == request_password)
        ).first()
        if user:
            return jsonify(
                {"message": "The user already exists"}), HTTPStatus.CONFLICT
        add_user = User(username=request_username, password=request_password)
        db.session.add(add_user)
        db.session.commit()
        success = "The user has been successfully created"
        return jsonify(
            message=success), HTTPStatus.CREATED
    except Exception as error:
        return jsonify({"error": str(error)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        db.session.close()
