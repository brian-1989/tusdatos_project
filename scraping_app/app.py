from config import Config
from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from views import views

app = Flask(__name__)
app.config.from_object(Config)

# Registrar el Blueprint
app.register_blueprint(views)

# Initialize the DB
db.init_app(app)

# Initialize the JWT
jwt = JWTManager(app)

# Create tables if not already created in the database


@app.before_request
def create_tables():
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
