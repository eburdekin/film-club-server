#!/usr/bin/env python3

from config import app, db
from models import User, Role, Movie, Club, ScreeningRoom, Post, Rating

# import requests for tMDB API call
import requests

TMDB_API_KEY = "97bca4f9bdb5d0ab61dcd0519c4eec58"

with app.app_context():
    # Delete existing data
    print("Deleting existing data...")
    # User.query.delete()
    # Role.query.delete()
    # Movie.query.delete()
    Role.query.delete()
    Club.query.delete()
    ScreeningRoom.query.delete()
    # Post.query.delete()
    # Rating.query.delete()

    # print("Seeding movie data...")

    # page = 1
    # total_pages = min(50, float("inf"))  # Set the total_pages to a maximum of 500

    # while page <= total_pages:
    #     url = f"https://api.themoviedb.org/3/discover/movie"
    #     params = {
    #         "api_key": TMDB_API_KEY,
    #         "language": "en-US",
    #         "sort_by": "popularity.desc",
    #         "include_adult": "false",
    #         "include_video": "false",
    #         "page": page,
    #     }
    #     response = requests.get(url, params=params)

    #     if response.status_code == 200:
    #         data = response.json()
    #         total_pages = min(
    #             data.get("total_pages", 0), 50
    #         )  # Update total_pages with a maximum of 500

    #         # Extract and insert movie data into the database
    #         for movie_data in data.get("results", []):
    #             movie = Movie(
    #                 title=movie_data.get("title"),
    #                 release_date=movie_data.get("release_date"),
    #                 poster_image=movie_data.get("poster_path"),
    #                 # Extract other relevant fields as needed
    #             )
    #             db.session.add(movie)

    #         db.session.commit()  # Committing after each page ensures data integrity

    #         print(f"Processed page {page}/{total_pages}")
    #         page += 1
    #     else:
    #         print(f"Failed to retrieve data from page {page}")
    #         break

    print("Seeding user roles...")
    role1 = Role(name="user")
    role2 = Role(name="mod")
    role3 = Role(name="admin")

    roles = [role1, role2, role3]

    db.session.add_all(roles)

    print("Seeding film club data...")
    club1 = Club(
        name="Criterion Classics",
        description="We watch Criterion movies.",
    )
    club2 = Club(name="Foreign Cinema", description="We love subtitles.")

    clubs = [club1, club2]

    db.session.add_all(clubs)

    print("Seeding screening room data...")
    screening_room1 = ScreeningRoom(name="screenroom1", club_id=1, movie_id=1)
    screening_room2 = ScreeningRoom(name="screenroom2", club_id=1, movie_id=2)

    screening_rooms = [screening_room1, screening_room2]

    db.session.add_all(screening_rooms)

    db.session.commit()
