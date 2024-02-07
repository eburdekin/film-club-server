#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS

# from flask_jwt_extended import JWTManager, jwt_required, create_access_token

app = Flask(__name__)
# need to make this private
app.secret_key = "ErrD76SEpKMDMcq71y4WfqnsZRDogwU3yZs6dKr0S2M4tHaA0KksY585UWR3psX"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///filmclub.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

bcrypt = Bcrypt(app)
jwt = JWTManager(app)


db = SQLAlchemy()
migrate = Migrate(app, db)
db.init_app(app)

ma = Marshmallow(app)

api = Api(app)
CORS(app)
