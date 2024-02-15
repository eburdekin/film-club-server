from models import db, Movie, Genre, User, Role, Club, ScreeningRoom, Post, Rating
from config import ma

from marshmallow import Schema, fields, validate, ValidationError

# Marshmallow schemas


class MovieSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Movie
        load_instance = True

    id = ma.auto_field()
    title = ma.auto_field()
    release_date = ma.auto_field()
    poster_image = ma.auto_field()
    popularity = ma.auto_field()
    genres = fields.Nested(
        "GenreSchema", many=True, only=("name",), cascade="all,delete-orphan"
    )
    screening_rooms = fields.Nested(
        "ScreeningRoomSchema",
        many=True,
        only=("id", "club"),
        cascade="all,delete-orphan",
    )


class GenreSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Genre
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    bio = ma.auto_field()
    location = ma.auto_field()
    clubs = fields.Nested("ClubSchema", many=True)
    posts = fields.Nested(
        "PostSchema", many=True, exclude=("author",), cascade="all,delete-orphan"
    )
    ratings = fields.Nested(
        "RatingSchema", many=True, exclude=("author",), cascade="all,delete-orphan"
    )
    role = fields.Nested(
        "RoleSchema",
        # exclude=("author",),
    )


class RoleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Role
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()


class ClubSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Club
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    screening_rooms = fields.Nested(
        "ScreeningRoomSchema",
        many=True,
        only=("id", "movie"),
        cascade="all,delete-orphan",
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
    # name = ma.auto_field()
    club_id = ma.auto_field()
    movie_id = ma.auto_field()
    club = fields.Nested("ClubSchema", only=("id", "name"))
    movie = fields.Nested("MovieSchema", only=("id", "title", "poster_image"))
    posts = fields.Nested("PostSchema", many=True, cascade="all,delete-orphan")
    ratings = fields.Nested("RatingSchema", many=True, cascade="all,delete-orphan")


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
        only=("id",),
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
        only=("id",),
    )
    timestamp = ma.auto_field()
    movie = fields.Nested(
        "MovieSchema", attribute="screening_room.movie", only=("id", "title")
    )


# Marshmallow validation


class ClubPostSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(
            min=1, max=50, error="Club name length must be between 1 and 50 characters"
        ),
        error_messages={"required": "Club name is required"},
    )
    description = fields.String(
        required=True,
        validate=validate.Length(
            min=1,
            max=150,
            error="Club description length must be between 1 and 150 characters",
        ),
        error_messages={"required": "Club description is required"},
    )


class ScreeningRoomPostSchema(Schema):
    # name = fields.String(
    #     required=True,
    #     validate=validate.Length(
    #         min=1,
    #         max=50,
    #         error="Screening room name length must be between 1 and 50 characters",
    #     ),
    #     error_messages={"required": "Screening room name is required"},
    # )
    club_id = fields.Integer(
        required=True,
        error_messages={"required": "Club ID is required"},
    )
    movie_id = fields.Integer(
        required=True,
        error_messages={"required": "Movie ID is required"},
    )


class PostPostSchema(Schema):
    content = fields.String(
        required=True,
        validate=validate.Length(
            min=1,
            max=200,
            error="Post content length must be between 1 and 200 characters",
        ),
        error_messages={"required": "Post content is required"},
    )
    author_id = fields.Integer(
        required=True,
        error_messages={"required": "Author ID is required"},
    )
    screening_room_id = fields.Integer(
        required=True,
        error_messages={"required": "Screening room ID is required"},
    )


class RatingPostSchema(Schema):
    rating = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=5, error="Rating must be between 1 and 5"),
        error_messages={"required": "Rating is required"},
    )
    author_id = fields.Integer(
        required=True,
        error_messages={"required": "Author ID is required"},
    )
    screening_room_id = fields.Integer(
        required=True,
        error_messages={"required": "Screening room ID is required"},
    )
