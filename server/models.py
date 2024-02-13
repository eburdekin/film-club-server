from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt
import pytz

club_members = db.Table(
    "club_members",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("club_id", db.Integer, db.ForeignKey("clubs.id"), primary_key=True),
)

# user_roles = db.Table(
#     "user_roles",
#     db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
#     db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
# )

movie_genre = db.Table(
    "movie_genre",
    db.Column("movie_id", db.Integer, db.ForeignKey("movies.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genres.id"), primary_key=True),
)


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.String)
    poster_image = db.Column(db.String)
    popularity = db.Column(db.Integer)
    genres = db.relationship("Genre", secondary="movie_genre", backref="movies")
    screening_rooms = db.relationship("ScreeningRoom", backref="movie")

    def __init__(
        self,
        title,
        release_date=None,
        poster_image=None,
        genres=None,
        popularity=None,
    ):
        self.title = title
        self.release_date = release_date
        self.poster_image = poster_image
        self.genres = genres or []
        self.popularity = popularity

    def __repr__(self):
        return f"<Movie {self.title}, id # {self.id}>"

    @staticmethod
    def calculate_average_rating(movie_id):
        # Retrieve all screening rooms associated with the given movie
        screening_rooms = ScreeningRoom.query.filter_by(movie_id=movie_id).all()

        total_ratings = 0
        total_count = 0

        # Calculate the total ratings for the movie
        for room in screening_rooms:
            ratings = Rating.query.filter_by(screening_room_id=room.id).all()
            for rating in ratings:
                total_ratings += rating.rating
                total_count += 1

        # Calculate the average rating
        if total_count > 0:
            average_rating = total_ratings / total_count
        else:
            average_rating = 0

        return average_rating


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"<Genre {self.name}, id # {self.id}>"


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    _password_hash = db.Column(db.String)
    profile_picture = db.Column(db.String)
    bio = db.Column(db.String)

    # Define relationship to posts and ratings
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    ratings = db.relationship("Rating", backref="user", lazy="dynamic")

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    role = db.relationship("Role", backref="user", uselist=False)

    # Define relationship to clubs
    # clubs = db.relationship(
    #     "Club", secondary="club_members", backref=db.backref("members", lazy="dynamic")
    # )
    # clubs = db.relationship(
    #     "Club", secondary=club_members, backref=db.backref("members", lazy="dynamic")
    # )

    # Authentication

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode("utf-8"))
        self._password_hash = password_hash.decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode("utf-8"))

    def __init__(self, username, email, role_id=1):
        self.username = username
        self.email = email
        self.role_id = role_id

    def __repr__(self):
        return f"<User {self.username}, id # {self.id}>"


class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    # owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # owner = db.relationship("User", backref="clubs_owned")
    members = db.relationship("User", secondary="club_members", backref="clubs")

    screening_rooms = db.relationship("ScreeningRoom", backref="club")

    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        # self.owner_id = owner_id

    def __repr__(self):
        return f"<Club {self.name}, id # {self.id}>"


class ScreeningRoom(db.Model):
    __tablename__ = "screening_rooms"

    id = db.Column(db.Integer, primary_key=True)
    # name = db.Column(db.String)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"))

    ## need to validate club and movie IDs exist

    posts = db.relationship("Post", backref="screening_room", lazy="dynamic")

    ratings = db.relationship("Rating", backref="screening_room", lazy="dynamic")

    def __init__(
        self,
        # name,
        club_id,
        movie_id,
    ):
        # self.name = name
        self.club_id = club_id
        self.movie_id = movie_id

    def __repr__(self):
        return f"<Screening Room id # {self.id}>"


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    screening_room_id = db.Column(db.Integer, db.ForeignKey("screening_rooms.id"))
    timestamp = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, content, author_id, screening_room_id):
        self.content = content
        self.author_id = author_id
        self.screening_room_id = screening_room_id

    def __repr__(self):
        return f"<Post id # {self.id}>"

    # @property
    # def timestamp_pst(self):
    #     return self.timestamp.astimezone(pst).strftime("%Y-%m-%d %H:%M:%S %Z")


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

    # @property
    # def timestamp_pst(self):
    #     return self.timestamp.astimezone(pst).strftime("%Y-%m-%d %H:%M:%S %Z")
