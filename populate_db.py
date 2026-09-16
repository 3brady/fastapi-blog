import asyncio
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from sqlalchemy import delete, select, update

import models
from database import AsyncSessionLocal, engine
from image_utils import PROFILE_PICS_DIR
from main import app

POPULATE_IMAGES_DIR = Path("populate_images")

USERS = [
    {
        # Ahmed's account - kept exactly as it was in the original seed data.
        "username": "3brady",
        "email": "22abdelrady22@gmail.com",
        "password": "AHMEDaly2006",
        "image": "3brady.jpg",
    },
    {
        "username": "JotaroKujo",
        "email": "jotaro@jojo.example",
        "password": "StarPlatinum!1",
        "image": "jotaro.jpg",
    },
    {
        "username": "JosephJoestar",
        "email": "joseph@jojo.example",
        "password": "HermitPurple!2",
        "image": "joseph.jpg",
    },
    {
        "username": "DIO",
        "email": "dio@jojo.example",
        "password": "TheWorld!3",
        "image": "dio.jpg",
    },
    {
        "username": "Josuke4",
        "email": "josuke@jojo.example",
        "password": "CrazyDiamond!4",
        "image": "josuke.jpg",
    },
    {
        "username": "GiornoGiovanna",
        "email": "giorno@jojo.example",
        "password": "GoldExperience!5",
        "image": "giorno.jpg",
    },
]

POSTS = [
    {
        "author": '3brady',
        "title": 'Started This Blog',
        "content": "I've been wanting to build a proper blog project for a while, so I finally did it. Now I just need to stop breaking the database every five minutes.",
    },
    {
        "author": 'JotaroKujo',
        "title": 'A Quiet Morning',
        "content": 'The morning was quiet. Good. I prefer it that way. Then someone started making noise outside. Annoying.',
    },
    {
        "author": 'JosephJoestar',
        "title": 'Age Is Just a Number',
        "content": "I'm still young. Young enough to run, young enough to fight, and young enough to beat Caesar at a race.",
    },
    {
        "author": 'DIO',
        "title": 'The World',
        "content": 'People spend their lives searching for power. They fail to understand that power is merely a reflection of will.',
    },
    {
        "author": 'Josuke4',
        "title": 'Hair Emergency',
        "content": 'WHOEVER SAID MY HAIR LOOKS LIKE THAT IS GETTING PUNCHED.',
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'Gold Experience',
        "content": 'Power means very little without a purpose. What matters is what you choose to do with it.',
    },
    {
        "author": '3brady',
        "title": 'Morioh Is Weird',
        "content": 'I started looking into the JoJo universe for this project and somehow every ten minutes I discover something even stranger.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'The Ocean',
        "content": "The sea is calm today. It doesn't stay calm for long. Neither do most people.",
    },
    {
        "author": 'JosephJoestar',
        "title": 'The Secret Plan',
        "content": "I have a plan. It's a very good plan. It may not be the plan I originally told you about, but that is part of the plan.",
    },
    {
        "author": 'DIO',
        "title": 'Ambition',
        "content": 'I do not ask the world for permission. I decide what I want, and then I take the necessary steps.',
    },
    {
        "author": 'Josuke4',
        "title": 'Angry Today',
        "content": "I'm trying to have a normal day. Then some idiot decides to make fun of my hair. Seriously?",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'A Goal',
        "content": 'I have a dream. I intend to see it through.',
    },
    {
        "author": '3brady',
        "title": 'Who Would You Follow?',
        "content": 'If you could follow one JoJo character on social media, who would it be? Personally, I feel like following Joseph would be a full-time job.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'About My Hat',
        "content": "Someone asked why I always wear this hat. It's not a hat. That's all I'm saying.",
    },
    {
        "author": 'JosephJoestar',
        "title": "Next You'll Say",
        "content": "Next you'll say, 'Joseph, why are you posting this?' And now you're wondering how I knew.",
    },
    {
        "author": 'DIO',
        "title": 'Silence',
        "content": 'Silence is underrated. It allows lesser minds to wonder what you are thinking.',
    },
    {
        "author": 'Josuke4',
        "title": 'Crazy Diamond',
        "content": "Crazy Diamond fixed a broken bike today. That's what it's for. Helping people.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'The Future',
        "content": "The future isn't something I wait for. It is something I work toward.",
    },
    {
        "author": '3brady',
        "title": 'The Jotaro Problem',
        "content": "I tried writing a post in Jotaro's style. Three sentences later I realized he would probably just say 'yare yare daze' and leave.",
    },
    {
        "author": 'JotaroKujo',
        "title": 'Another Strange Case',
        "content": 'There was another Stand user in town. We dealt with it. No need to make a big deal out of it.',
    },
    {
        "author": 'JosephJoestar',
        "title": 'Caesar',
        "content": "Some names stay with you. Some friends stay with you even when they're gone.",
    },
    {
        "author": 'DIO',
        "title": 'A Beautiful Evening',
        "content": 'The evening is beautiful. The world looks almost worthy of being ruled.',
    },
    {
        "author": 'Josuke4',
        "title": 'Town Problems',
        "content": "Morioh is weird. Like, really weird. But it's our weird town, so leave it alone.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'Resolve',
        "content": 'There are moments when retreat is impossible. In those moments, resolve becomes everything.',
    },
    {
        "author": '3brady',
        "title": "DIO's Feed",
        "content": 'DIO having a social media account would be terrible for everyone involved. Every post would sound like he was announcing the end of civilization.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'A Long Day',
        "content": 'Long day. Fought a Stand user, got dragged into an argument, and nearly missed dinner. Yare yare.',
    },
    {
        "author": 'JosephJoestar',
        "title": 'Training',
        "content": "Ham on. Breathing steady. Keep moving. If you're tired, move anyway.",
    },
    {
        "author": 'DIO',
        "title": 'Followers',
        "content": 'Many people desire greatness. Few possess the courage to pursue it.',
    },
    {
        "author": 'Josuke4',
        "title": 'Friends',
        "content": "I don't care what people say. If you're my friend, I'll have your back.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'A New Beginning',
        "content": 'Every beginning is difficult. That does not make it less worth pursuing.',
    },
    {
        "author": '3brady',
        "title": "Josuke's Notifications",
        "content": 'I can already imagine Josuke getting into an argument because someone commented on his hair. His notification count would be terrifying.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'Travel Notes',
        "content": "Traveling with a group is inefficient. Traveling with my friends is worse. I'd still rather have them around.",
    },
    {
        "author": 'JosephJoestar',
        "title": 'Family Dinner',
        "content": "Family dinner was peaceful for exactly eleven minutes. That's a new record.",
    },
    {
        "author": 'DIO',
        "title": 'Patience',
        "content": 'Patience is not weakness. It is the luxury of someone who knows the outcome is already decided.',
    },
    {
        "author": 'Josuke4',
        "title": 'A Good Day',
        "content": "Helped an old lady carry her groceries, fixed a kid's bike, got lunch with friends. Pretty good day.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'Trust',
        "content": 'Trust is earned through action. Words alone are insufficient.',
    },
    {
        "author": '3brady',
        "title": 'Giorno Would Be Verified',
        "content": 'Giorno would have a perfectly clean profile, one profile picture, no unnecessary posts, and somehow millions of followers.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'Star Platinum',
        "content": "Star Platinum doesn't need an introduction.",
    },
    {
        "author": 'JosephJoestar',
        "title": 'Technology',
        "content": 'People keep inventing gadgets that do things I can already do with a newspaper, some string, and a little luck.',
    },
    {
        "author": 'DIO',
        "title": 'A Reminder',
        "content": 'Remember this: hesitation creates opportunities for others. Do not hesitate.',
    },
    {
        "author": 'Josuke4',
        "title": 'Okay, Who Did This?',
        "content": "Someone put gum on the underside of my desk. I'm finding out who did it.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'Leadership',
        "content": 'A leader does not stand above everyone else. A leader moves forward first.',
    },
    {
        "author": '3brady',
        "title": 'Joseph Would Post Everything',
        "content": 'Joseph would absolutely post his entire day online. Training, food, arguments, family drama. Nothing would stay private.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'Photography',
        "content": "My daughter wanted a picture. I took one. She said I look angry. I wasn't.",
    },
    {
        "author": 'JosephJoestar',
        "title": 'Aging Gracefully',
        "content": 'My knees hurt. My back hurts. My spirit remains magnificent.',
    },
    {
        "author": 'DIO',
        "title": 'The Night',
        "content": 'Night suits me. There are fewer distractions and fewer people pretending they understand the world.',
    },
    {
        "author": 'Josuke4',
        "title": 'Hair Again',
        "content": "I'm not sensitive about my hair. I'm sensitive about people being stupid about my hair.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'A Necessary Choice',
        "content": 'Some choices are unpleasant. That does not make avoiding them the correct choice.',
    },
    {
        "author": '3brady',
        "title": 'Database Update',
        "content": 'The database is finally behaving. This is the closest thing to a peaceful ending I expect to get from this project.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'Morioh',
        "content": "Morioh has more Stand users than any normal town should have. I'm beginning to suspect normal isn't an option here.",
    },
    {
        "author": 'JosephJoestar',
        "title": 'Retirement',
        "content": 'Retirement is wonderful. You can sleep whenever you want. Unless someone calls you because another Stand user is causing trouble.',
    },
    {
        "author": 'DIO',
        "title": 'Victory',
        "content": 'Victory is not merely defeating an opponent. It is making them understand that resistance was pointless.',
    },
    {
        "author": 'Josuke4',
        "title": 'Dinner',
        "content": "My mom made dinner. Best food in town. Don't tell her I said that.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'Quiet Confidence',
        "content": 'There is no need to announce what you intend to accomplish. Let the result speak.',
    },
    {
        "author": '3brady',
        "title": 'Why I Like JoJo',
        "content": 'The best thing about JoJo is how every part feels different while still feeling unmistakably like JoJo.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'Old Friends',
        "content": 'Some people disappear for years and somehow return exactly as loud as you remember them.',
    },
    {
        "author": 'JosephJoestar',
        "title": 'I Have Seen Some Things',
        "content": "After everything I've seen, very little surprises me anymore. Very little.",
    },
    {
        "author": 'DIO',
        "title": 'Ambition, Again',
        "content": 'Dreams are for those who sleep. I prefer goals.',
    },
    {
        "author": 'Josuke4',
        "title": 'A Weird Guy',
        "content": "There was this super weird guy in town today. Quiet, polite, and somehow way too creepy. Something's off.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'One Step',
        "content": 'One step at a time. One decision at a time. Eventually, the path becomes clear.',
    },
    {
        "author": '3brady',
        "title": 'The Feed Test',
        "content": 'I wanted the feed to feel like actual people using the site, not a list of random sample posts. So now everyone gets their own voice.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'I Said I Was Fine',
        "content": "I'm fine. Stop asking.",
    },
    {
        "author": 'JosephJoestar',
        "title": 'Breakfast',
        "content": "Breakfast is important. Don't skip it. Also, if someone tells you otherwise, they're probably an idiot.",
    },
    {
        "author": 'DIO',
        "title": 'A New Order',
        "content": 'The world is full of people waiting for someone else to decide their fate. I have never had that weakness.',
    },
    {
        "author": 'Josuke4',
        "title": 'The Gang',
        "content": "My friends are idiots. They're my idiots, though.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'The Dream',
        "content": 'I will achieve my dream. Not because the world promised it to me, but because I chose to pursue it.',
    },
    {
        "author": '3brady',
        "title": 'One More Bug',
        "content": 'Fixed three bugs today and created two new ones. The ancient programming ritual continues.',
    },
    {
        "author": 'JotaroKujo',
        "title": 'The Road Home',
        "content": 'The trip is over. The people I met along the way made it worth the trouble.',
    },
    {
        "author": 'JosephJoestar',
        "title": 'Vacation',
        "content": 'I planned a peaceful vacation. Then my family got involved.',
    },
    {
        "author": 'DIO',
        "title": 'A Simple Question',
        "content": 'Why settle for an ordinary life when you were capable of taking everything?',
    },
    {
        "author": 'Josuke4',
        "title": 'Stand Users',
        "content": "If another Stand user shows up at school, I'm going home.",
    },
    {
        "author": 'GiornoGiovanna',
        "title": 'Another Day',
        "content": 'Another day, another obstacle. We continue.',
    },
]


# The oldest post - created separately so the pagination/date logic stays intact.
POST_44 = {
    "author": "3brady",
    "title": "A Strange Day in Morioh",
    "content": "There are days when Morioh feels almost normal. Those days never last. Still, I wouldn't trade this town for anywhere else.",
}


async def clear_existing_data() -> None:
    # Delete profile pictures from local storage
    if PROFILE_PICS_DIR.exists():
        for file in PROFILE_PICS_DIR.iterdir():
            if file.is_file() and file.name != ".gitkeep":
                file.unlink()
        print(f"Deleted profile pictures from {PROFILE_PICS_DIR}")

    # Clear database tables (order respects foreign keys)
    async with AsyncSessionLocal() as db:
        await db.execute(delete(models.Post))
        await db.execute(delete(models.User))
        await db.commit()
    print("Cleared existing data")


def shuffle_posts(posts: list[dict]) -> list[dict]:
    """Return a genuinely mixed feed while avoiding obvious author streaks."""
    shuffled = posts.copy()

    # A fresh shuffle on every populate means the feed changes every time.
    # Retry if two consecutive posts come from the same account. With the
    # current distribution this is extremely unlikely to need many attempts.
    for _ in range(1000):
        random.shuffle(shuffled)
        if all(
            shuffled[i]["author"] != shuffled[i - 1]["author"]
            for i in range(1, len(shuffled))
        ):
            return shuffled

    # Defensive fallback: if the data distribution ever changes, still return
    # a random order rather than getting stuck in an infinite loop.
    return shuffled


async def update_post_dates() -> None:
    now = datetime.now(UTC)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.Post).order_by(models.Post.id))
        posts = result.scalars().all()

        if not posts:
            return

        # POST_44 is the oldest. The rest are assigned increasing timestamps
        # so the database's normal newest-first ordering matches the shuffled
        # POSTS order used when creating them.
        oldest_date = now - timedelta(days=90)
        if len(posts) == 1:
            step = timedelta(0)
        else:
            step = timedelta(days=90 / (len(posts) - 1))

        for i, post in enumerate(posts):
            post_date = oldest_date + (step * i)
            await db.execute(
                update(models.Post)
                .where(models.Post.id == post.id)
                .values(date_posted=post_date),
            )

        await db.commit()
    print("Updated post dates")


async def populate() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as client:
        # Clear existing data (local images first, then database)
        await clear_existing_data()

        users: list[dict] = []

        print(f"\nCreating {len(USERS)} users...")
        for user_data in USERS:
            response = await client.post(
                "/api/users",
                json={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            user = response.json()
            print(f"  Created: {user['username']}")

            response = await client.post(
                "/api/users/token",
                data={
                    "username": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            token = response.json()["access_token"]

            if image_name := user_data.get("image"):
                image_path = POPULATE_IMAGES_DIR / image_name
                if image_path.exists():
                    response = await client.patch(
                        f"/api/users/{user['id']}/picture",
                        files={
                            "file": (
                                image_name,
                                image_path.read_bytes(),
                                "image/png",
                            ),
                        },
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    response.raise_for_status()
                    print(f"    Uploaded: {image_name}")

            users.append(
                {"id": user["id"], "username": user["username"], "token": token},
            )

        print(f"\nCreating {len(POSTS) + 1} posts...")

        # First create POST_44 (will become oldest after date update)
        response = await client.post(
            "/api/posts",
            json={"title": POST_44["title"], "content": POST_44["content"]},
            headers={"Authorization": f"Bearer {next(
                user["token"] for user in users if user["username"] == POST_44["author"]
            )}"},
        )
        response.raise_for_status()
        print(f"  Created: '{POST_44['title']}'")

        # Randomize the feed before inserting. Each post keeps its explicit
        # author, but the overall timeline is mixed so it feels like a real
        # social feed rather than one account posting in batches.
        feed_posts = shuffle_posts(POSTS)

        # Create remaining posts in reverse so the first item in feed_posts
        # becomes the newest post after date_posted is assigned.
        users_by_username = {user["username"]: user for user in users}

        for post_data in reversed(feed_posts):
            user = users_by_username[post_data["author"]]
            response = await client.post(
                "/api/posts",
                json={
                    "title": post_data["title"],
                    "content": post_data["content"],
                },
                headers={"Authorization": f"Bearer {user['token']}"},
            )
            response.raise_for_status()
            title = post_data["title"]
            print(
                f"  Created: '{title[:50]}...'"
                if len(title) > 50
                else f"  Created: '{title}'",
            )

        print("\nUpdating post dates...")
        await update_post_dates()

    await engine.dispose()

    print("\nDone!")
    print(f"  {len(USERS)} users")
    print(f"  {len(POSTS) + 1} posts")
    print("  Profile pictures saved locally")


if __name__ == "__main__":
    asyncio.run(populate())