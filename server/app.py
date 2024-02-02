#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS

# from flask_jwt_extended import JWTManager, jwt_required, create_access_token

from models import db, Movie, User, Club, ScreeningRoom, Post, Rating

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///filmclub.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

ma = Marshmallow(app)

api = Api(app)
CORS(app)

# Schemas


class MovieSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie
        load_instance = True

    id = ma.auto_field()
    title = ma.auto_field()
    release_date = ma.auto_field()
    poster_image = ma.auto_field()
    genres = ma.auto_field()
    director = ma.auto_field()
    cast = ma.auto_field()
    summary = ma.auto_field()
    trailer_link = ma.auto_field()
    streaming_availability = ma.auto_field()


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
        # include_relationships = True

    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    bio = ma.auto_field()
    clubs = fields.Nested("ClubSchema", many=True)
    posts = fields.Nested("PostSchema", many=True, exclude=("author", "author_id"))
    ratings = fields.Nested("RatingSchema", many=True, exclude=("author", "author_id"))

    # how to add relationships?


class ClubSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Club
        load_instance = True
        # include_relationships = True

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    privacy_setting = ma.auto_field()
    screening_rooms = fields.Nested(
        "ScreeningRoomSchema", many=True, only=("id", "name", "movie")
    )
    members = fields.Nested(
        "UserSchema",
        many=True,
        only=(
            "id",
            "username",
        ),
    )

    # how to add relationships?


class ScreeningRoomSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ScreeningRoom
        load_instance = True
        # include_relationships = True

    id = ma.auto_field()
    name = ma.auto_field()
    # club_id = ma.auto_field()
    # movie_id = ma.auto_field()
    club = fields.Nested("ClubSchema", only=("id", "name"))
    movie = fields.Nested("MovieSchema", only=("id", "title"))


class PostSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Post
        load_instance = True
        # include_relationships = True

    id = ma.auto_field()
    content = ma.auto_field()
    author_id = ma.auto_field()
    author = fields.Nested("UserSchema", only=("username",))
    screening_room_id = ma.auto_field()
    timestamp = ma.auto_field()


class RatingSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Rating
        load_instance = True
        # include_relationships = True

    id = ma.auto_field()
    rating = ma.auto_field()
    author_id = ma.auto_field()
    author = fields.Nested("UserSchema", only=("username",))
    screening_room_id = ma.auto_field()
    timestamp = ma.auto_field()


# API Routes


@app.route("/")
def index():
    return "<h1>Film Club Server</h1>"


# @app.before_request
# def check_if_logged_in():
#     open_access_list = ["movies", "clubs", "screening_rooms"]

#     if (request.endpoint) not in open_access_list and (not session.get("user_id")):
#         return {"error": "401 Unauthorized"}, 401


class Movies(Resource):
    def get(self):
        # movies = [movie.to_dict() for movie in Movie.query.all()]
        # return make_response(jsonify(movies), 200)
        movies = Movie.query.all()
        movie_schema = MovieSchema(many=True)
        movies_data = movie_schema.dump(movies)
        return make_response(jsonify(movies_data), 200)


api.add_resource(Movies, "/movies")


class Users(Resource):
    def get(self):
        # users = [user.to_dict() for user in User.query.all()]
        # return make_response(jsonify(users), 200)
        users = User.query.all()
        user_schema = UserSchema(many=True)
        users_data = user_schema.dump(users)
        return make_response(jsonify(users_data), 200)


api.add_resource(Users, "/users")


class Clubs(Resource):
    def get(self):
        # clubs = [club.to_dict() for club in Club.query.all()]
        # return make_response(jsonify(clubs), 200)
        clubs = Club.query.all()
        club_schema = ClubSchema(many=True)
        clubs_data = club_schema.dump(clubs)
        return make_response(jsonify(clubs_data), 200)

    # @jwt_required
    # def post(self):
    #     pass


api.add_resource(Clubs, "/clubs")


class ClubsById(Resource):
    def get(self, id):
        club = Club.query.filter_by(id=id).first()
        if club is None:
            return make_response({"error": "Club not found"}, 404)
        return make_response(club.to_dict(), 200)


api.add_resource(ClubsById, "/clubs/<int:id>")


class ScreeningRooms(Resource):
    def get(self):
        # rooms = [room.to_dict() for room in ScreeningRoom.query.all()]
        # return make_response(jsonify(rooms), 200)
        rooms = ScreeningRoom.query.all()
        room_schema = ScreeningRoomSchema(many=True)
        rooms_data = room_schema.dump(rooms)
        return make_response(jsonify(rooms_data), 200)


api.add_resource(ScreeningRooms, "/rooms")


class Posts(Resource):
    def get(self):
        # posts = [post.to_dict() for post in Post.query.all()]
        # return make_response(jsonify(posts), 200)
        posts = Post.query.all()
        post_schema = PostSchema(many=True)
        posts_data = post_schema.dump(posts)
        return make_response(jsonify(posts_data), 200)


api.add_resource(Posts, "/posts")


class Ratings(Resource):
    def get(self):
        # ratings = [rating.to_dict() for rating in Rating.query.all()]
        # return make_response(jsonify(ratings), 200)
        ratings = Rating.query.all()
        rating_schema = RatingSchema(many=True)
        ratings_data = rating_schema.dump(ratings)
        return make_response(jsonify(ratings_data), 200)


api.add_resource(Ratings, "/ratings")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
