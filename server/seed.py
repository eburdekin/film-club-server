#!/usr/bin/env python3

from app import app
from models import db, User, Movie, Club, ScreeningRoom

# import requests for tMDB API call
import requests

TMDB_API_KEY = "97bca4f9bdb5d0ab61dcd0519c4eec58"

with app.app_context():
    # Delete existing data
    print("Deleting existing data...")
    User.query.delete()
    Movie.query.delete()
    Club.query.delete()
    ScreeningRoom.query.delete()

    print("Seeding user data...")
    user1 = User(username="burdaq", email="eileenburdekin@proton.me")

    db.session.add(user1)

    print("Seeding movie data...")
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

    # Extract and insert movie data into the database
    for movie_data in data.get("results", []):
        movie = Movie(
            title=movie_data.get("title"),
            release_date=movie_data.get("release_date"),
            poster_image=movie_data.get("poster_path"),
            # Extract other relevant fields as needed
        )
        db.session.add(movie)

    print("Seeding film club data...")
    club1 = Club(name="club1", description="hihihi")

    db.session.add(club1)

    print("Seeding screening room data...")
    screening_room1 = ScreeningRoom(name="screenroom1", club_id=1, movie_id=1)
    screening_room2 = ScreeningRoom(name="screenroom2", club_id=1, movie_id=2)

    screening_rooms = [screening_room1, screening_room2]

    db.session.add_all(screening_rooms)

    print("Assigning users to clubs...")
    user1.clubs.append(club1)

    db.session.commit()
