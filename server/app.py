# #!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from functools import wraps
from marshmallow import Schema, fields, validate, ValidationError

# Local imports
from models import db, Movie, Role, User, Club, ScreeningRoom, Post, Rating
from schemas import (
    MovieSchema,
    UserSchema,
    RoleSchema,
    ClubSchema,
    ScreeningRoomSchema,
    PostSchema,
    RatingSchema,
    ClubPostSchema,
    ScreeningRoomPostSchema,
    RatingPostSchema,
    PostPostSchema,
)
from config import app, api


# Control access via user roles


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id:
            if not user_has_role(user_id, "admin"):
                return {"message": "Unauthorized access"}, 401
            return f(*args, **kwargs)
        return {"message": "User not logged in"}, 401

    return decorated_function


def mod_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id:
            if not user_has_role(user_id, "admin") and not user_has_role(
                user_id, "mod"
            ):
                return {"message": "Unauthorized access"}, 401
            return f(*args, **kwargs)
        return {"message": "User not logged in"}, 401

    return decorated_function


def user_has_role(user_id, role_name):
    user = User.query.filter_by(id=user_id).first()
    if user and user.role and user.role.name == role_name:
        return True
    return False


# @app.before_request
# def check_if_logged_in():
#     open_access_list = ["signup", "login", "check_session", "movies", "clubs"]

#     if (request.endpoint) not in open_access_list and (not session.get("user_id")):
#         # if (request.endpoint) not in open_access_list:
#         return {"error": "401 Unauthorized"}, 401


# User authentication, user role assignment


class AssignRoleResource(Resource):
    # @admin_required --- currently breaks if this is added
    def post(self):
        data = request.get_json()
        user_id = data.get("user_id")
        role_id = data.get("role_id")

        if not user_id or not role_id:
            return {"message": "User ID and Role ID are required"}, 400

        user = User.query.get(user_id)
        role = Role.query.get(role_id)

        if not user or not role:
            return {"message": "User or Role not found"}, 404

        user.role = role
        db.session.commit()

        return {"message": f"Role {role.name} assigned to user {user.username}"}, 200


class SignupResource(Resource):
    def post(self):
        request_json = request.get_json()

        username = request_json.get("username")
        email = request_json.get("email")
        password = request_json.get("password")

        # Check if the username or email already exists
        if User.query.filter_by(username=username).first() is not None:
            return {"msg": "Username already exists"}, 400
        if User.query.filter_by(email=email).first() is not None:
            return {"msg": "Email already exists"}, 400

        # Create a new user
        new_user = User(username=username, email=email)
        new_user.password_hash = password  # Set password using hashing method

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.id
        # Optionally, you can generate an access token and return it upon signup
        # access_token = create_access_token(identity=new_user.id)

        return {"msg": "User created successfully"}, 201


class LoginResource(Resource):
    def post(self):
        request_json = request.get_json()

        username = request_json.get("username")
        password = request_json.get("password")

        user = User.query.filter_by(username=username).first()
        if not user or not user.authenticate(password):
            return {"msg": "Bad username or password"}, 401

        # access_token = create_access_token(identity=user.id)
        # session["user_id"] = user.id
        user_schema = UserSchema()
        serialized_user = user_schema.dump(user)

        user_id = user.id

        session["user_id"] = user_id

        return serialized_user, 200


class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get("user_id")).first()
        if user:
            user_schema = UserSchema()
            serialized_user = user_schema.dump(user)
            return serialized_user
        else:
            return {"message": "401: Not Authorized"}, 401


class Logout(Resource):
    def delete(self):
        session.clear()
        return {"message": "204: No Content"}, 204


api.add_resource(AssignRoleResource, "/assign_role")
api.add_resource(SignupResource, "/signup")
api.add_resource(LoginResource, "/login")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Logout, "/logout")

# API Routes


@app.route("/")
def index():
    return "<h1>Film Club Server</h1>"


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
    @admin_required
    def get(self):
        users = User.query.all()
        user_schema = UserSchema(many=True)
        users_data = user_schema.dump(users)
        return make_response(jsonify(users_data), 200)

    # signup is what posts new users -- don't need below
    # def post(self):
    #     data = request.json
    #     user_schema = UserSchema()
    #     try:
    #         new_user = user_schema.load(data)
    #         db.session.add(new_user)
    #         db.session.commit()
    #         return user_schema.dump(new_user), 201
    #     except Exception as e:
    #         db.session.rollback()
    #         return make_response({"error": e.__str__()}, 400)


class UsersById(Resource):
    @admin_required
    def get(self, id):
        user = User.query.filter_by(id=id).first()
        if user is None:
            return make_response({"error": "User not found"}, 404)
        user_schema = UserSchema(exclude=("clubs.screening_rooms", "clubs.members"))
        user_data = user_schema.dump(user)
        return make_response(jsonify(user_data), 200)

    # def patch(self, id):
    #     # need to be changed for roles?
    #     user = User.query.get(id)
    #     if not user:
    #         return make_response({"error": "User not found"}, 404)
    #     data = request.json
    #     user_schema = UserSchema()
    #     try:
    #         updated_user = user_schema.load(data, instance=user, partial=True)
    #         db.session.commit()
    #         return user_schema.dump(updated_user), 200
    #     except Exception as e:
    #         db.session.rollback()
    #         return make_response({"error": e.__str__()}, 400)

    # @admin_required
    # def patch(self, id):
    #     user = User.query.get(id)
    #     if not user:
    #         return jsonify({"error": "User not found"}), 404

    #     data = request.json
    #     # Ensure that only the allowed fields are updated
    #     allowed_fields = ["username", "email", "role"]
    #     for field in allowed_fields:
    #         if field in data:
    #             setattr(user, field, data[field])

    #     try:
    #         db.session.commit()
    #         user_schema = UserSchema()
    #         updated_user = user_schema.dump(user)
    #         return jsonify(updated_user), 200
    #     except Exception as e:
    #         db.session.rollback()
    #         return jsonify({"error": str(e)}), 400

    @admin_required
    def delete(self, id):
        user = User.query.get(id)
        if not user:
            return make_response({"error": "User not found"}, 404)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}, 200


class Roles(Resource):

    @admin_required
    def get(self):
        roles = Role.query.all()
        role_schema = RoleSchema(many=True)
        roles_data = role_schema.dump(roles)
        return make_response(jsonify(roles_data), 200)

    # def post(self):
    #     data = request.json
    #     role_schema = RoleSchema()
    #     try:
    #         new_role = role_schema.load(data)
    #         db.session.add(new_role)
    #         db.session.commit()
    #         return role_schema.dump(new_role), 201
    #     except Exception as e:
    #         db.session.rollback()
    #         return make_response({"error": e.__str__()}, 400)


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
    # @user_required
    def get(self):
        rooms = ScreeningRoom.query.all()
        room_schema = ScreeningRoomSchema(many=True)
        rooms_data = room_schema.dump(rooms)
        return make_response(jsonify(rooms_data), 200)

    ### make club owner only
    def post(self):
        data = request.json
        try:
            validated_data = ScreeningRoomPostSchema().load(data)
        except ValidationError as e:
            return make_response({"error": e.messages}, 400)

        screening_room_schema = ScreeningRoomSchema()
        try:
            new_screening_room = screening_room_schema.load(validated_data)
            db.session.add(new_screening_room)
            db.session.commit()
            return screening_room_schema.dump(new_screening_room), 201
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 400)


class ScreeningRoomsById(Resource):
    # @user_required --- not working with frontend properly
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
    # @user_required
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
    # @user_required
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
    # @user_required
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
    # @user_required
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
api.add_resource(Roles, "/roles")
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
