# #!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from marshmallow import Schema, fields, validate, ValidationError

# Local imports
from models import db, Movie, User, Club, ScreeningRoom, Post, Rating
from schemas import (
    MovieSchema,
    UserSchema,
    ClubSchema,
    ScreeningRoomSchema,
    PostSchema,
    RatingSchema,
    ClubPostSchema,
)
from config import app, api


# API Routes


@app.route("/")
def index():
    return "<h1>Film Club Server</h1>"


# @app.before_request
# def check_if_logged_in():
#     open_access_list = ["movies", "clubs", "screening_rooms"]

#     if (request.endpoint) not in open_access_list and (not session.get("user_id")):
#         return {"error": "401 Unauthorized"}, 401


# class SignupResource(Resource):
#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument("username", type=str, required=True)
#         parser.add_argument("email", type=str, required=True)
#         parser.add_argument("password", type=str, required=True)
#         # You may include other fields like profile picture, bio, etc., as needed
#         data = parser.parse_args()

#         username = data["username"]
#         email = data["email"]
#         password = data["password"]

#         # Check if the username or email already exists
#         if User.query.filter_by(username=username).first() is not None:
#             return {"msg": "Username already exists"}, 400
#         if User.query.filter_by(email=email).first() is not None:
#             return {"msg": "Email already exists"}, 400

#         # Create a new user
#         new_user = User(username=username, email=email)
#         new_user._password_hash = password  # Set password using hashing method

#         # Add the new user to the database
#         db.session.add(new_user)
#         db.session.commit()

#         # Optionally, you can generate an access token and return it upon signup
#         access_token = create_access_token(identity=new_user.id)

#         return {"msg": "User created successfully", "access_token": access_token}, 201


# class LoginResource(Resource):
#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument("username", type=str, required=True)
#         parser.add_argument("password", type=str, required=True)
#         data = parser.parse_args()

#         username = data["username"]
#         password = data["password"]

#         user = User.query.filter_by(username=username).first()
#         if not user or not user.authenticate(password):
#             return {"msg": "Bad username or password"}, 401

#         access_token = create_access_token(identity=user.id)
#         return {"access_token": access_token}, 200


# class ProtectedResource(Resource):
#     @jwt_required()
#     def get(self):
#         current_user_id = get_jwt_identity()
#         return {"logged_in_as": current_user_id}, 200


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
        # Validate incoming data
        try:
            validated_data = ClubPostSchema().load(data)
        except ValidationError as e:
            return make_response({"error": e.messages}, 400)

        # Process the validated data
        club_schema = ClubSchema()
        try:
            new_club = club_schema.load(validated_data)
            db.session.add(new_club)
            db.session.commit()
            return club_schema.dump(new_club), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)

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


# api.add_resource(SignupResource, "/signup")
# api.add_resource(LoginResource, "/login")
# api.add_resource(ProtectedResource, "/protected")
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
