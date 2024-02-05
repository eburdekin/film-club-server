from models import db, Movie, User, Club, ScreeningRoom, Post, Rating
from config import app, api, ma

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
    public = ma.auto_field()
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
    public = fields.Boolean(required=True)