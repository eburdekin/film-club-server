from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

club_members = db.Table(
    "club_members",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("club_id", db.Integer, db.ForeignKey("clubs.id"), primary_key=True),
)


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.String)
    poster_image = db.Column(db.String)
    genres = db.Column(db.String)
    director = db.Column(db.String)
    cast = db.Column(db.String)
    summary = db.Column(db.String)
    trailer_link = db.Column(db.String)
    streaming_availability = db.Column(db.String)
    screening_rooms = db.relationship("ScreeningRoom", backref="movie")

    def __init__(
        self,
        title,
        release_date=None,
        poster_image=None,
        genres=None,
        director=None,
        cast=None,
        summary=None,
        trailer_link=None,
        streaming_availability=None,
    ):
        self.title = title
        self.release_date = release_date
        self.poster_image = poster_image
        self.genres = genres
        self.director = director
        self.cast = cast
        self.summary = summary
        self.trailer_link = trailer_link
        self.streaming_availability = streaming_availability

    def __repr__(self):
        return f"<Movie {self.title}, id # {self.id}>"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    # _password_hash = db.Column(db.String)
    profile_picture = db.Column(db.String)
    bio = db.Column(db.String)

    # Define relationship to posts and ratings
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    ratings = db.relationship("Rating", backref="user", lazy="dynamic")

    # serialize_rules = ("-posts.user", "-ratings.user")

    # Define relationship to clubs
    # clubs = db.relationship(
    #     "Club", secondary="club_members", backref=db.backref("members", lazy="dynamic")
    # )
    # clubs = db.relationship(
    #     "Club", secondary=club_members, backref=db.backref("members", lazy="dynamic")
    # )
    # Authentication

    # @hybrid_property
    # def password_hash(self):
    #     raise AttributeError("Password hashes may not be viewed.")

    # @password_hash.setter
    # def password_hash(self, password):
    #     password_hash = bcrypt.generate_password_hash(password.encode("utf-8"))
    #     self._password_hash = password_hash.decode("utf-8")

    # def authenticate(self, password):
    #     return bcrypt.check_password_hash(self._password_hash, password.encode("utf-8"))

    def __init__(self, username, email, profile_picture=None, bio=None):
        self.username = username
        self.email = email
        # self.password_hash = password
        self.profile_picture = profile_picture
        self.bio = bio

    def __repr__(self):
        return f"<User {self.username}, id # {self.id}>"


class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    privacy_setting = db.Column(db.String)
    # owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # owner = db.relationship("User", backref="clubs_owned")
    members = db.relationship("User", secondary="club_members", backref="clubs")

    screening_rooms = db.relationship("ScreeningRoom", backref="club")

    # Add other relevant fields as needed, e.g., creation_date, privacy_settings, etc.
    # serialize_rules = ("-screening_rooms.club", "-members.clubs")

    def __init__(self, name, description=None, owner_id=None):
        self.name = name
        self.description = description
        self.owner_id = owner_id

    def __repr__(self):
        return f"<Club {self.name}, id # {self.id}>"


class ScreeningRoom(db.Model):
    __tablename__ = "screening_rooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"))

    # movie = db.relationship("Movie", backref="screening_room")  # Define relationship

    posts = db.relationship("Post", backref="screening_room", lazy="dynamic")

    ratings = db.relationship("Rating", backref="screening_room", lazy="dynamic")

    # serialize_rules = ("-movie.screening_rooms",)

    def __init__(
        self,
        name,
        club_id,
        movie_id,
    ):
        self.name = name
        self.club_id = club_id
        self.movie_id = movie_id

    def __repr__(self):
        return f"<Screening Room {self.name}, id # {self.id}>"


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    screening_room_id = db.Column(db.Integer, db.ForeignKey("screening_rooms.id"))
    timestamp = db.Column(db.DateTime, default=db.func.now())

    # serialize_only = ("content", "timestamp")

    def __init__(self, content, author_id, screening_room_id):
        self.content = content
        self.author_id = author_id
        self.screening_room_id = screening_room_id

    def __repr__(self):
        return f"<Post id # {self.id}>"


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    screening_room_id = db.Column(db.Integer, db.ForeignKey("screening_rooms.id"))
    rating = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, author_id, screening_room_id, rating):
        self.author_id = author_id
        self.screening_room_id = screening_room_id
        self.rating = rating

    def __repr__(self):
        return f"<Rating id # {self.id}>"
