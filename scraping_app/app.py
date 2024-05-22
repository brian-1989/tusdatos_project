from config import Config
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt
)
from http import HTTPStatus
from models import db, Process, User
from sqlalchemy import and_

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Configuración del JWT
jwt = JWTManager(app)

blacklist = set()

# Crear las tablas si no están creadas en la base de datos
@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()

# Proceso del Login
@app.route("/api/v1/login", methods=["POST"])
def login():
    try:
        username = request.json.get("username")
        password = request.json.get("password")
        user = User.query.filter(
            and_(username==username, password==password)
        ).all()
        if len(user) == 0:
            return jsonify(
                {"message": "Bad username or password"}), HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=username)
        user[0].token = access_token
        db.session.commit()
        return jsonify(access_token=access_token), HTTPStatus.CREATED
    except Exception as error:
        return jsonify({"error": str(error)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        db.session.close()

@app.route("/api/v1/logout", methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify(message="Access token revoked"), 200

# Obetener toda la información del Scraping
@app.route("/api/v1/get_scraping", methods=["GET"])
@jwt_required()
def get_scraping():
    jti = get_jwt()['jti']
    if jti in blacklist:
        message = "Unauthorized. The session token has expired or is invalid."
        return jsonify(
            message=message),HTTPStatus.UNAUTHORIZED
    try:
        process = Process.query.all()
        result = []
        for proces in process:
            result.append(
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
                }
            )
        return jsonify(result)
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    finally:
        db.session.close()

if __name__ == '__main__':
    app.run(debug=True, port=5001)