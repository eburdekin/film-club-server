#!/usr/bin/env python3

from config import app, db
from models import User, Role, Movie, Genre, Club, ScreeningRoom, Post, Rating

# import requests for tMDB API call
import requests

from faker import Faker
import random
from random import randint


TMDB_API_KEY = "97bca4f9bdb5d0ab61dcd0519c4eec58"

fake = Faker()

with app.app_context():
    # print("Deleting existing data...")
    # User.query.delete()
    # Role.query.delete()
    # Movie.query.delete()
    # Genre.query.delete()
    # Club.query.delete()
    # ScreeningRoom.query.delete()
    # Post.query.delete()
    # Rating.query.delete()

    print("Seeding user roles...")
    role1 = Role(name="user")
    role2 = Role(name="mod")
    role3 = Role(name="admin")

    roles = [role1, role2, role3]

    db.session.add_all(roles)

    print("Seeding users...")
    # Define a list to store user details for signup
    users_to_signup = []

    # Generate user details using Faker and append to the list
    for _ in range(15):
        username = fake.user_name()
        email = fake.email()
        # Set password the same as username
        password = username
        users_to_signup.append(
            {"username": username, "email": email, "password": password}
        )

    # Iterate over each user details and simulate signup
    for user_details in users_to_signup:
        # Extract user details
        username = user_details["username"]
        email = user_details["email"]
        password = user_details["password"]

        # Check if the username or email already exists
        if User.query.filter_by(username=username).first() is not None:
            print(f"Username '{username}' already exists, skipping signup.")
            continue
        if User.query.filter_by(email=email).first() is not None:
            print(f"Email '{email}' already exists, skipping signup.")
            continue

        # Create a new user object
        new_user = User(username=username, email=email)
        new_user.password_hash = password  # Set password using hashing method

        # Add the new user to the database
        db.session.add(new_user)

    print("Seeding genres...")
    genre1 = Genre(id=28, name="Action")
    genre2 = Genre(id=12, name="Adventure")
    genre3 = Genre(id=16, name="Animation")
    genre4 = Genre(id=35, name="Comedy")
    genre5 = Genre(id=80, name="Crime")
    genre6 = Genre(id=99, name="Documentary")
    genre7 = Genre(id=18, name="Drama")
    genre8 = Genre(id=10751, name="Family")
    genre9 = Genre(id=14, name="Fantasy")
    genre10 = Genre(id=36, name="History")
    genre11 = Genre(id=27, name="Horror")
    genre12 = Genre(id=10402, name="Music")
    genre13 = Genre(id=9648, name="Mystery")
    genre14 = Genre(id=10749, name="Romance")
    genre15 = Genre(id=878, name="Science Fiction")
    genre16 = Genre(id=10770, name="TV Movie")
    genre17 = Genre(id=53, name="Thriller")
    genre18 = Genre(id=10752, name="War")
    genre19 = Genre(id=37, name="Western")

    genres = [
        genre1,
        genre2,
        genre3,
        genre4,
        genre5,
        genre6,
        genre7,
        genre8,
        genre9,
        genre10,
        genre11,
        genre12,
        genre13,
        genre14,
        genre15,
        genre16,
        genre17,
        genre18,
        genre19,
    ]

    db.session.add_all(genres)

    print("Seeding movie data...")

    page = 1
    total_pages = min(10, float("inf"))  # Set the total_pages to a maximum of 500

    while page <= total_pages:
        url = f"https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "include_video": "false",
            "page": page,
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            total_pages = min(
                data.get("total_pages", 0), 10
            )  # Update total_pages with a maximum of 500

            # Extract and insert movie data into the database
            for movie_data in data.get("results", []):

                genre_ids = movie_data.get("genre_ids", [])
                genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()

                # for genre in genres:
                #     print(genre)

                movie = Movie(
                    title=movie_data.get("title"),
                    release_date=movie_data.get("release_date"),
                    poster_image=movie_data.get("poster_path"),
                    popularity=movie_data.get("popularity"),
                    genres=genres,
                    # Extract other relevant fields as needed
                )
                db.session.add(movie)

            db.session.commit()  # Committing after each page ensures data integrity

            print(f"Processed page {page}/{total_pages}")
            page += 1
        else:
            print(f"Failed to retrieve data from page {page}")
            break

    print("Seeding film club data...")
    club1 = Club(
        name="Criterion Classics",
        description="We watch Criterion movies.",
    )
    club2 = Club(name="Foreign Cinema", description="We love subtitles.")
    club3 = Club(name="Horror Haven", description="For fans of horror films.")
    club4 = Club(
        name="Sci-Fi Lovers", description="Exploring the cosmos of sci-fi cinema."
    )
    club5 = Club(
        name="Drama Delight",
        description="Emotional journeys and compelling narratives.",
    )
    club6 = Club(
        name="Action Alley",
        description="Explosive thrills and adrenaline-pumping action.",
    )
    club7 = Club(
        name="Comedy Corner", description="Laugh-out-loud comedies and witty humor."
    )
    club8 = Club(
        name="Documentary Discovery",
        description="Exploring real-life stories and events.",
    )
    club9 = Club(
        name="Animation Adventure", description="Magical worlds and animated wonders."
    )
    club10 = Club(
        name="Fantasy Frontier",
        description="Journeys into fantastical realms and adventures.",
    )
    club11 = Club(
        name="Romancing the Movies",
        description="Love stories and heartwarming romances.",
    )
    club12 = Club(
        name="Mystery Mansion",
        description="Unraveling mysteries and suspenseful tales.",
    )
    club13 = Club(
        name="Thriller Theater",
        description="Nail-biting suspense and thrilling twists.",
    )
    club14 = Club(
        name="Western Wilds", description="Journeys into the untamed frontier."
    )
    club15 = Club(
        name="Cult Classics",
        description="Exploring offbeat and cult-favorite films.",
    )
    club16 = Club(
        name="Music & Musicals",
        description="Singing, dancing, and musical masterpieces.",
    )
    club17 = Club(
        name="Historical Highlights", description="Exploring history through cinema."
    )
    club18 = Club(
        name="Family Flicks", description="Entertainment for the whole family."
    )
    club19 = Club(
        name="Experimental Expanse", description="Pushing the boundaries of cinema."
    )
    club20 = Club(
        name="Global Gems",
        description="Exploring international cinema and diverse cultures.",
    )

    clubs = [
        club1,
        club2,
        club3,
        club4,
        club5,
        club6,
        club7,
        club8,
        club9,
        club10,
        club11,
        club12,
        club13,
        club14,
        club15,
        club16,
        club17,
        club18,
        club19,
        club20,
    ]

    db.session.add_all(clubs)

    print("Seeding club membership...")
    # Define a list of users (assuming you have users in your database)
    users = User.query.all()

    # Shuffle the list of users to randomize the order
    random.shuffle(users)

    # Assign a random subset of users to each club
    for club in clubs:
        # Determine the number of members for each club (you can adjust this number as needed)
        num_members = random.randint(5, 15)  # Random number between 5 and 15

        # Select a random subset of users to be members of the club
        club_members = random.sample(users, num_members)

        # Add the selected users to the club's members
        club.members.extend(club_members)

    print("Seeding screening room data...")
    screening_room1 = ScreeningRoom(club_id=1, movie_id=1)
    screening_room2 = ScreeningRoom(club_id=1, movie_id=2)
    screening_room3 = ScreeningRoom(club_id=2, movie_id=3)
    screening_room4 = ScreeningRoom(club_id=2, movie_id=4)
    screening_room5 = ScreeningRoom(club_id=3, movie_id=5)
    screening_room6 = ScreeningRoom(club_id=3, movie_id=6)
    screening_room7 = ScreeningRoom(club_id=4, movie_id=7)
    screening_room8 = ScreeningRoom(club_id=4, movie_id=8)
    screening_room9 = ScreeningRoom(club_id=5, movie_id=9)
    screening_room10 = ScreeningRoom(club_id=5, movie_id=10)
    screening_room11 = ScreeningRoom(club_id=6, movie_id=11)
    screening_room12 = ScreeningRoom(club_id=6, movie_id=12)
    screening_room13 = ScreeningRoom(club_id=7, movie_id=13)
    screening_room14 = ScreeningRoom(club_id=7, movie_id=14)
    screening_room15 = ScreeningRoom(club_id=8, movie_id=15)
    screening_room16 = ScreeningRoom(club_id=8, movie_id=16)
    screening_room17 = ScreeningRoom(club_id=9, movie_id=17)
    screening_room18 = ScreeningRoom(club_id=9, movie_id=18)
    screening_room19 = ScreeningRoom(club_id=10, movie_id=19)
    screening_room20 = ScreeningRoom(club_id=10, movie_id=20)
    screening_room21 = ScreeningRoom(club_id=11, movie_id=21)
    screening_room22 = ScreeningRoom(club_id=11, movie_id=22)
    screening_room23 = ScreeningRoom(club_id=12, movie_id=23)
    screening_room24 = ScreeningRoom(club_id=12, movie_id=24)
    screening_room25 = ScreeningRoom(club_id=13, movie_id=25)
    screening_room26 = ScreeningRoom(club_id=13, movie_id=26)
    screening_room27 = ScreeningRoom(club_id=14, movie_id=27)
    screening_room28 = ScreeningRoom(club_id=14, movie_id=28)
    screening_room29 = ScreeningRoom(club_id=15, movie_id=29)
    screening_room30 = ScreeningRoom(club_id=15, movie_id=30)
    screening_room31 = ScreeningRoom(club_id=16, movie_id=31)
    screening_room32 = ScreeningRoom(club_id=16, movie_id=32)
    screening_room33 = ScreeningRoom(club_id=17, movie_id=33)
    screening_room34 = ScreeningRoom(club_id=17, movie_id=34)
    screening_room35 = ScreeningRoom(club_id=18, movie_id=35)
    screening_room36 = ScreeningRoom(club_id=18, movie_id=36)
    screening_room37 = ScreeningRoom(club_id=19, movie_id=37)
    screening_room38 = ScreeningRoom(club_id=19, movie_id=38)
    screening_room39 = ScreeningRoom(club_id=20, movie_id=39)
    screening_room40 = ScreeningRoom(club_id=20, movie_id=40)

    screening_rooms = [
        screening_room1,
        screening_room2,
        screening_room3,
        screening_room4,
        screening_room5,
        screening_room6,
        screening_room7,
        screening_room8,
        screening_room9,
        screening_room10,
        screening_room11,
        screening_room12,
        screening_room13,
        screening_room14,
        screening_room15,
        screening_room16,
        screening_room17,
        screening_room18,
        screening_room19,
        screening_room20,
        screening_room21,
        screening_room22,
        screening_room23,
        screening_room24,
        screening_room25,
        screening_room26,
        screening_room27,
        screening_room28,
        screening_room29,
        screening_room30,
        screening_room31,
        screening_room32,
        screening_room33,
        screening_room34,
        screening_room35,
        screening_room36,
        screening_room37,
        screening_room38,
        screening_room39,
        screening_room40,
    ]

    db.session.add_all(screening_rooms)

    print("Seeding posts...")
    rooms_to_post_to = ScreeningRoom.query.all()
    for room in rooms_to_post_to:
        for _ in range(11):
            post = Post(
                content=fake.text(),
                author_id=randint(1, 11),
                screening_room_id=room.id,
            )
            db.session.add(post)

    print("Seeding ratings...")
    rooms_to_post_to = ScreeningRoom.query.all()
    for room in rooms_to_post_to:
        for _ in range(11):
            rating = Rating(
                rating=randint(1, 5),
                author_id=randint(1, 11),
                screening_room_id=room.id,
            )
            db.session.add(rating)

    db.session.commit()
