#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, User, Movie, Club, ScreeningRoom

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///filmclub.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Film Club Server</h1>"


class Users(Resource):
    def get(self):
        users = [user.to_dict() for user in User.query.all()]
        return make_response(jsonify(users), 200)


api.add_resource(Users, "/users")


class Movies(Resource):
    def get(self):
        movies = [movie.to_dict() for movie in Movie.query.all()]
        return make_response(jsonify(movies), 200)


api.add_resource(Movies, "/movies")


class Clubs(Resource):
    def get(self):
        clubs = [club.to_dict() for club in Club.query.all()]
        return make_response(jsonify(clubs), 200)


api.add_resource(Clubs, "/clubs")


class ScreeningRooms(Resource):
    def get(self):
        rooms = [room.to_dict() for room in ScreeningRoom.query.all()]
        return make_response(jsonify(rooms), 200)


api.add_resource(ScreeningRooms, "/screening_rooms")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
