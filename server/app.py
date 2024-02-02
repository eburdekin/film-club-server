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

    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    bio = ma.auto_field()
    clubs = fields.Nested("ClubSchema", many=True)
    posts = fields.Nested(
        "PostSchema",
        many=True,
        exclude=("author",),
    )
    ratings = fields.Nested(
        "RatingSchema",
        many=True,
        exclude=("author",),
    )


class ClubSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Club
        load_instance = True

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


class ScreeningRoomSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ScreeningRoom
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    club_id = ma.auto_field()
    movie_id = ma.auto_field()
    club = fields.Nested("ClubSchema", only=("id", "name"))
    movie = fields.Nested("MovieSchema", only=("id", "title"))


class PostSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Post
        load_instance = True

    id = ma.auto_field()
    content = ma.auto_field()
    author_id = ma.auto_field()
    author = fields.Nested(
        "UserSchema",
        only=(
            "id",
            "username",
        ),
    )
    screening_room_id = ma.auto_field()
    screening_room = fields.Nested(
        "ScreeningRoomSchema",
        only=(
            "id",
            "name",
        ),
    )
    timestamp = ma.auto_field()
    movie = fields.Nested(
        "MovieSchema", attribute="screening_room.movie", only=("id", "title")
    )


class RatingSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Rating
        load_instance = True

    id = ma.auto_field()
    rating = ma.auto_field()
    author_id = ma.auto_field()
    author = fields.Nested(
        "UserSchema",
        only=(
            "id",
            "username",
        ),
    )
    screening_room_id = ma.auto_field()
    screening_room = fields.Nested(
        "ScreeningRoomSchema",
        only=(
            "id",
            "name",
        ),
    )
    timestamp = ma.auto_field()
    movie = fields.Nested(
        "MovieSchema", attribute="screening_room.movie", only=("id", "title")
    )


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
        movies = Movie.query.all()
        movie_schema = MovieSchema(many=True)
        movies_data = movie_schema.dump(movies)
        return make_response(jsonify(movies_data), 200)

    ### make admin only
    def post(self):
        data = request.json
        movie_schema = MovieSchema()
        try:
            new_movie = movie_schema.load(data)
            db.session.add(new_movie)
            db.session.commit()
            return movie_schema.dump(new_movie), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)


class MoviesById(Resource):
    def get(self, id):
        movie = Movie.query.filter_by(id=id).first()
        if not movie:
            return make_response({"error": "Movie not found"}, 404)
        movie_schema = MovieSchema()
        movie_data = movie_schema.dump(movie)
        return make_response(jsonify(movie_data), 200)

    ### make admin only
    def patch(self, id):
        # Update an existing movie
        movie = Movie.query.get(id)
        if not movie:
            return make_response({"error": "Movie not found"}, 404)
        data = request.json
        movie_schema = MovieSchema()
        try:
            updated_movie = movie_schema.load(data, instance=movie, partial=True)
            db.session.commit()
            return movie_schema.dump(updated_movie), 200
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)

    ### make admin only
    def delete(self, id):
        # Delete an existing movie
        movie = Movie.query.get(id)
        if not movie:
            return make_response({"error": "Movie not found"}, 404)
        db.session.delete(movie)
        db.session.commit()
        return {"message": "Movie deleted successfully"}, 200


class Users(Resource):
    def get(self):
        users = User.query.all()
        user_schema = UserSchema(many=True)
        users_data = user_schema.dump(users)
        return make_response(jsonify(users_data), 200)

    def post(self):
        data = request.json
        user_schema = UserSchema()
        try:
            new_user = user_schema.load(data)
            db.session.add(new_user)
            db.session.commit()
            return user_schema.dump(new_user), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)


class UsersById(Resource):
    def get(self, id):
        user = User.query.filter_by(id=id).first()
        if user is None:
            return make_response({"error": "User not found"}, 404)
        user_schema = UserSchema(exclude=("clubs.screening_rooms", "clubs.members"))
        user_data = user_schema.dump(user)
        return make_response(jsonify(user_data), 200)

    def patch(self, id):
        user = User.query.get(id)
        if not user:
            return make_response({"error": "User not found"}, 404)
        data = request.json
        user_schema = UserSchema()
        try:
            updated_user = user_schema.load(data, instance=user, partial=True)
            db.session.commit()
            return user_schema.dump(updated_user), 200
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)

    def delete(self, id):
        user = User.query.get(id)
        if not user:
            return make_response({"error": "User not found"}, 404)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}, 200


class Clubs(Resource):
    def get(self):
        clubs = Club.query.all()
        club_schema = ClubSchema(many=True)
        clubs_data = club_schema.dump(clubs)
        return make_response(jsonify(clubs_data), 200)

    ### user who posts new club needs to be set as owner
    def post(self):
        data = request.json
        club_schema = ClubSchema()
        try:
            new_club = club_schema.load(data)
            db.session.add(new_club)
            db.session.commit()
            return club_schema.dump(new_club), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)

    # @jwt_required
    # def post(self):
    #     pass


class ClubsById(Resource):
    def get(self, id):
        club = Club.query.filter_by(id=id).first()
        if club is None:
            return make_response({"error": "Club not found"}, 404)
        # return make_response(club.to_dict(), 200)
        club_schema = ClubSchema()
        club_data = club_schema.dump(club)
        return make_response(jsonify(club_data), 200)

    ### make club owner only
    def patch(self, id):
        club = Club.query.get(id)
        if not club:
            return make_response({"error": "Club not found"}, 404)
        data = request.json
        club_schema = ClubSchema()
        try:
            updated_club = club_schema.load(data, instance=club, partial=True)
            db.session.commit()
            return club_schema.dump(updated_club), 200
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)

    ### make club owner only
    def delete(self, id):
        club = Club.query.get(id)
        if not club:
            return make_response({"error": "Club not found"}, 404)
        db.session.delete(club)
        db.session.commit()
        return {"message": "Club deleted successfully"}, 200


class ScreeningRooms(Resource):
    def get(self):
        rooms = ScreeningRoom.query.all()
        room_schema = ScreeningRoomSchema(many=True)
        rooms_data = room_schema.dump(rooms)
        return make_response(jsonify(rooms_data), 200)

    ### make club owner only
    def post(self):
        data = request.json
        room_schema = ScreeningRoomSchema()
        try:
            new_room = room_schema.load(data)
            db.session.add(new_room)
            db.session.commit()
            return room_schema.dump(new_room), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)


class ScreeningRoomsById(Resource):
    def get(self, id):
        room = ScreeningRoom.query.filter_by(id=id).first()
        if room is None:
            return make_response({"error": "Screening room not found"}, 404)
        # return make_response(club.to_dict(), 200)
        room_schema = ScreeningRoomSchema()
        room_data = room_schema.dump(room)
        return make_response(jsonify(room_data), 200)

    ### make club owner only
    def patch(self, id):
        room = ScreeningRoom.query.get(id)
        if not room:
            return make_response({"error": "Screening room not found"}, 404)
        data = request.json
        room_schema = ScreeningRoomSchema()
        try:
            updated_room = room_schema.load(data, instance=room, partial=True)
            db.session.commit()
            return room_schema.dump(updated_room), 200
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)

    ### make club owner only
    def delete(self, id):
        room = ScreeningRoom.query.get(id)
        if not room:
            return make_response({"error": "Screening room not found"}, 404)
        db.session.delete(room)
        db.session.commit()
        return {"message": "Screening room deleted successfully"}, 200


class Posts(Resource):
    def get(self):
        posts = Post.query.all()
        post_schema = PostSchema(many=True)
        posts_data = post_schema.dump(posts)
        return make_response(jsonify(posts_data), 200)

    def post(self):
        data = request.json
        post_schema = PostSchema()
        try:
            new_post = post_schema.load(data)
            db.session.add(new_post)
            db.session.commit()
            return post_schema.dump(new_post), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)


class PostsById(Resource):
    def get(self, id):
        post = Post.query.filter_by(id=id).first()
        if post is None:
            return make_response({"error": "Post not found"}, 404)
        post_schema = PostSchema()
        post_data = post_schema.dump(post)
        return make_response(jsonify(post_data), 200)

    def patch(self, id):
        post = Post.query.get(id)
        if not post:
            return make_response({"error": "Post not found"}, 404)
        data = request.json
        post_schema = PostSchema()
        try:
            updated_post = post_schema.load(data, instance=post, partial=True)
            db.session.commit()
            return post_schema.dump(updated_post), 200
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)

    def delete(self, id):
        post = Post.query.get(id)
        if not post:
            return make_response({"error": "Post not found"}, 404)
        db.session.delete(post)
        db.session.commit()
        return {"message": "Post deleted successfully"}, 200


class Ratings(Resource):
    def get(self):
        ratings = Rating.query.all()
        rating_schema = RatingSchema(many=True)
        ratings_data = rating_schema.dump(ratings)
        return make_response(jsonify(ratings_data), 200)

    def post(self):
        data = request.json
        rating_schema = RatingSchema()
        try:
            new_rating = rating_schema.load(data)
            db.session.add(new_rating)
            db.session.commit()
            return rating_schema.dump(new_rating), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)


class RatingsById(Resource):
    def get(self, id):
        rating = Rating.query.filter_by(id=id).first()
        if rating is None:
            return make_response({"error": "Rating not found"}, 404)
        rating_schema = RatingSchema()
        rating_data = rating_schema.dump(rating)
        return make_response(jsonify(rating_data), 200)

    def patch(self, id):
        rating = Rating.query.get(id)
        if not rating:
            return make_response({"error": "Rating not found"}, 404)
        data = request.json
        rating_schema = RatingSchema()
        try:
            updated_rating = rating_schema.load(data, instance=rating, partial=True)
            db.session.commit()
            return rating_schema.dump(updated_rating), 200
        except Exception as e:
            db.session.rollback()
            return make_response({"error": e.__str__()}, 400)

    def delete(self, id):
        rating = Rating.query.get(id)
        if not rating:
            return make_response({"error": "Rating not found"}, 404)
        db.session.delete(rating)
        db.session.commit()
        return {"message": "Rating deleted successfully"}, 200


api.add_resource(Movies, "/movies")
api.add_resource(MoviesById, "/movies/<int:id>")
api.add_resource(Users, "/users")
api.add_resource(UsersById, "/users/<int:id>")
api.add_resource(Clubs, "/clubs")
api.add_resource(ClubsById, "/clubs/<int:id>")
api.add_resource(ScreeningRooms, "/rooms")
api.add_resource(ScreeningRoomsById, "/rooms/<int:id>")
api.add_resource(Posts, "/posts")
api.add_resource(PostsById, "/posts/<int:id>")
api.add_resource(Ratings, "/ratings")
api.add_resource(RatingsById, "/ratings/<int:id>")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
