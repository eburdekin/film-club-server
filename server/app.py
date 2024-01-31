#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

# from flask_jwt_extended import JWTManager, jwt_required, create_access_token

from models import db, User, Movie, Club, ScreeningRoom, Post, Rating

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


# @app.before_request
# def check_if_logged_in():
#     open_access_list = ["movies", "clubs", "screening_rooms"]

#     if (request.endpoint) not in open_access_list and (not session.get("user_id")):
#         return {"error": "401 Unauthorized"}, 401


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

    # @jwt_required
    # def post(self):
    #     pass


api.add_resource(Clubs, "/clubs")


class ScreeningRooms(Resource):
    def get(self):
        rooms = [room.to_dict() for room in ScreeningRoom.query.all()]
        return make_response(jsonify(rooms), 200)


api.add_resource(ScreeningRooms, "/screening_rooms")


class Posts(Resource):
    def get(self):
        posts = [post.to_dict() for post in Post.query.all()]
        return make_response(jsonify(posts), 200)


api.add_resource(Posts, "/posts")


class Ratings(Resource):
    def get(self):
        ratings = [rating.to_dict() for rating in Rating.query.all()]
        return make_response(jsonify(ratings), 200)


api.add_resource(Ratings, "/ratings")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
