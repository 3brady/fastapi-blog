import asyncio
import random
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import delete, select, update

import models
from database import AsyncSessionLocal, engine
from image_utils import PROFILE_PICS_DIR
from main import app

USERS = [
    {
        "username": "sarah_m",
        "email": "sarah@example.com",
        "password": "SunnyDay2026!",
    },
    {
        "username": "mark_t",
        "email": "mark@example.com",
        "password": "MorningRun2026@",
    },
    {
        "username": "lina_k",
        "email": "lina@example.com",
        "password": "PastaNight2026#",
    },
    {
        "username": "dave_n",
        "email": "dave@example.com",
        "password": "SideProject2026$",
    },
    {
        "username": "amina_r",
        "email": "amina@example.com",
        "password": "FinalsDone2026!",
    },
]

POSTS = [
    {
        "author": "sarah_m",
        "title": "First Week Back",
        "content": "First week of term is done. Still haven't memorized all the new names, but nobody's grading me on that yet.",
    },
    {
        "author": "mark_t",
        "title": "Morning Runs",
        "content": "Started running before work again. It's cold, it's dark, and honestly it's the only part of the day that's actually quiet.",
    },
    {
        "author": "lina_k",
        "title": "Pasta Night",
        "content": "Made a simple garlic and butter pasta tonight. Took twenty minutes and cost almost nothing. Will absolutely be making this again.",
    },
    {
        "author": "dave_n",
        "title": "The API Kept Timing Out",
        "content": "Spent most of yesterday chasing a timeout that turned out to be a connection pool issue. Fixed with a longer timeout and a lot of sighing.",
    },
    {
        "author": "amina_r",
        "title": "Finals Are Over",
        "content": "Finals are finally over. I'm going to sleep for a full day and then figure out what to do with my life.",
    },
    {
        "author": "sarah_m",
        "title": "Grading on a Saturday",
        "content": "It's Saturday and I'm grading essays. The things I write in the margins are getting funnier, which probably means I need a break.",
    },
    {
        "author": "mark_t",
        "title": "Office AC",
        "content": "The office AC broke again. Everyone is blaming everyone else. I just want to get through the day without sweating through my shirt.",
    },
    {
        "author": "lina_k",
        "title": "Farmers Market Haul",
        "content": "The farmer's market had good tomatoes this week. Bought too many. Now I have to figure out what to do with three kilos of them.",
    },
    {
        "author": "dave_n",
        "title": "Side Project: Week 3",
        "content": "Week three of my side project and I've already rewritten the models twice. The good news is that the third version is definitely the right one.",
    },
    {
        "author": "amina_r",
        "title": "Library Sessions",
        "content": "The library is the only place I actually get work done. I don't know if it's the silence or the guilt, but it works.",
    },
    {
        "author": "sarah_m",
        "title": "The Classroom Projector",
        "content": "The classroom projector worked on the first try today. I want to thank whoever fixed it, but I don't know who to thank.",
    },
    {
        "author": "mark_t",
        "title": "Meal Prep Sunday",
        "content": "Made five lunches for the week. Rice, chicken, and broccoli. Exciting stuff, but my wallet appreciates it.",
    },
    {
        "author": "lina_k",
        "title": "Sourdough Attempt",
        "content": "Tried making sourdough for the first time. The starter bubbled, the dough rose, and the loaf came out... dense. It's a work in progress.",
    },
    {
        "author": "dave_n",
        "title": "Remote Work Setup",
        "content": "Upgraded my home desk setup with a second monitor. Productivity jumped maybe 10%, but the setup looks way cooler, which honestly counts for a lot.",
    },
    {
        "author": "amina_r",
        "title": "Part-Time Job",
        "content": "Started a part-time job at a bookstore. Mostly I restock shelves and recommend books. Customers ask me about books I haven't read yet constantly.",
    },
    {
        "author": "sarah_m",
        "title": "Student Questions",
        "content": "A student asked me a question I couldn't answer today. I said I'd look it up and get back to them. I actually did. Small wins.",
    },
    {
        "author": "mark_t",
        "title": "Trail Race",
        "content": "Signed up for a 10k trail race. I am in no way ready for a 10k trail race. The registration fee is already paid though, so now I have to train.",
    },
    {
        "author": "lina_k",
        "title": "Weeknight Stir Fry",
        "content": "Frozen veg, whatever meat was on sale, and a sauce I made with stuff from the pantry. Dinner done in fifteen minutes. Highly recommend.",
    },
    {
        "author": "dave_n",
        "title": "That Dependency",
        "content": "Removed a dependency I didn't need today. Replaced it with a ten line function. It felt great. I should do this more often.",
    },
    {
        "author": "amina_r",
        "title": "Group Project Chaos",
        "content": "Group project meeting lasted three hours and we decided... nothing. We have another meeting next week to decide when to schedule more meetings.",
    },
    {
        "author": "sarah_m",
        "title": "Rainy Sunday",
        "content": "It rained all day so I did nothing but read and drink tea. Best Sunday in a while.",
    },
    {
        "author": "mark_t",
        "title": "Working From Home",
        "content": "Working from home today. The commute is great. The kitchen is a constant temptation, but the commute is really great.",
    },
    {
        "author": "lina_k",
        "title": "Soup Season",
        "content": "Made a big pot of vegetable soup for the week. It's officially soup season and I'm so here for it.",
    },
    {
        "author": "dave_n",
        "title": "Scope Creep",
        "content": "The client asked for 'just a small change'. Four hours later I've rebuilt half the feature. Small changes are a lie.",
    },
    {
        "author": "amina_r",
        "title": "Campus Coffee",
        "content": "Found a corner of the campus cafe nobody knows about. Free refills, no crowd, and a window with actual sunlight. I'm never leaving.",
    },
    {
        "author": "sarah_m",
        "title": "Book I Finished This Weekend",
        "content": "Finished a book over the weekend that I'd been meaning to read for months. It was fine. Not a revelation, but a solid weekend.",
    },
    {
        "author": "mark_t",
        "title": "Shoes",
        "content": "Bought new running shoes. Old ones had holes. Not a fun purchase, but my feet are grateful.",
    },
    {
        "author": "lina_k",
        "title": "The Cheap Dinner I Make Too Often",
        "content": "Eggs, rice, and soy sauce. I make it at least twice a week and I'm not ashamed. Cheap, fast, and better than half the takeaways around here.",
    },
    {
        "author": "dave_n",
        "title": "Debugging by Talking to the Wall",
        "content": "Explained my bug out loud to nobody in particular and found the issue in the middle of the explanation. Talking to the wall is a legitimate technique.",
    },
    {
        "author": "amina_r",
        "title": "Weekend Trip",
        "content": "Went to a small coastal town for the weekend with friends. Walked a lot, ate a lot, came back tired in a good way.",
    },
    {
        "author": "sarah_m",
        "title": "Lesson Planning",
        "content": "Lesson planning for the week is done. It took three hours and two cups of coffee. That's a normal amount, right?",
    },
    {
        "author": "mark_t",
        "title": "The 5am Club",
        "content": "Tried the whole waking up at 5am thing. Day three and I've mostly been staring at the kitchen in the dark. We'll see how it goes.",
    },
    {
        "author": "lina_k",
        "title": "Recipe Win",
        "content": "Tried a new recipe for chicken and it actually came out like the picture. That never happens. Saving it forever.",
    },
    {
        "author": "dave_n",
        "title": "New Laptop",
        "content": "New laptop arrived. Spent the first hour configuring it. Spent the second hour wondering if I backed up everything. I did. Probably.",
    },
    {
        "author": "amina_r",
        "title": "Sleep Deprivation",
        "content": "Got four hours of sleep before the morning class. I remember the lecture vaguely. Mostly I remember the lecture room being very beige.",
    },
    {
        "author": "sarah_m",
        "title": "Coffee Before School",
        "content": "I don't function before my morning coffee and today I forgot to buy it. I functioned at maybe 60%. Rough day.",
    },
    {
        "author": "mark_t",
        "title": "Lunch Break Walk",
        "content": "Started taking a walk during lunch. Twenty minutes, no phone. It does more for my afternoon than any meeting ever has.",
    },
    {
        "author": "lina_k",
        "title": "Kitchen Mess",
        "content": "Cooked a nice dinner and then spent twenty minutes scrubbing the kitchen. The dinner was worth the cleanup. Barely.",
    },
    {
        "author": "dave_n",
        "title": "The Invoice Finally Paid",
        "content": "The invoice I sent two months ago finally got paid. I had already written it off. It's a good week. I'll believe all future invoices arrive on time now.",
    },
    {
        "author": "amina_r",
        "title": "The Elective I Chose",
        "content": "Chose my elective for next semester based purely on the schedule. Nothing that starts before 10am. Some might say lazy, I say strategic.",
    },
    {
        "author": "sarah_m",
        "title": "Field Trip Planning",
        "content": "Planning a field trip for the class. Permission slips, bus times, headcounts. I feel like I'm organizing a small army.",
    },
    {
        "author": "mark_t",
        "title": "Weekend Hike",
        "content": "Went on a hike Sunday. Six kilometres, one very muddy section, and a sandwich at the top that tasted incredible. Worth the wash.",
    },
    {
        "author": "lina_k",
        "title": "Dinner With Friends",
        "content": "Friends came over last night. Made a big pot of chili and we all ate too much. Someone asked for the recipe, which is the highest compliment.",
    },
    {
        "author": "dave_n",
        "title": "Learning SQL the Hard Way",
        "content": "Found a slow query today the hard way. Learned more about indexes in one afternoon than in my whole career. Turns out the docs were right again.",
    },
    {
        "author": "amina_r",
        "title": "Roommate Cooking",
        "content": "Me and my roommate cook in shifts. My nights are decent. Their nights are also decent. The shared kitchen, however, is a war zone.",
    },
    {
        "author": "sarah_m",
        "title": "A Quiet Evening",
        "content": "Graded, lesson prepped, and then actually sat down with a book for an hour. A quiet evening is a luxury and I'm grateful.",
    },
    {
        "author": "mark_t",
        "title": "Sleep",
        "content": "Turns out eight hours of sleep is a real thing and it changes everything. I know I sound like an infomercial but I've been living wrong.",
    },
    {
        "author": "lina_k",
        "title": "Leftover Reinvention",
        "content": "Had leftover roast chicken and turned it into the best soup of my life. Leftovers deserve their own cooking show.",
    },
    {
        "author": "dave_n",
        "title": "Two Clients, One Deadline",
        "content": "Two clients, same deadline, both urgent. I said yes to both to be safe. I don't know why I keep doing this to myself.",
    },
    {
        "author": "amina_r",
        "title": "Budget Week",
        "content": "It's budget week and I actually stuck to it this time. Mostly because I ran out of money by Wednesday. Either way, I'm counting it as a win.",
    },
    {
        "author": "sarah_m",
        "title": "Why I Keep a Notebook",
        "content": "I keep a paper notebook for all the things I'll forget if they're on a phone. There's now a note in it about writing in the notebook more often.",
    },
    {
        "author": "mark_t",
        "title": "Fitness Tracker",
        "content": "Got a fitness tracker and now I walk more just to watch the number go up. It's basically a video game where the prize is cardiovascular health.",
    },
    {
        "author": "lina_k",
        "title": "Pantry Basics",
        "content": "Keeping the pantry stocked with onions, garlic, and canned tomatoes solves most of my 'what's for dinner' problems. It's the only meal planning I do.",
    },
    {
        "author": "dave_n",
        "title": "Automating the Boring Stuff",
        "content": "Wrote a script to do the boring reporting task I hate. It took longer than doing it manually once, but it's the last time I ever have to do it.",
    },
    {
        "author": "amina_r",
        "title": "Walking to Class in the Rain",
        "content": "Got caught in the rain walking to class. My umbrella broke in the wind. Everything was soaked. The lecture was about statistics, so the day was already lost.",
    },
    {
        "author": "sarah_m",
        "title": "Small Moments",
        "content": "One of the quieter kids in class answered a question today without me calling on them. Nobody else noticed. I noticed. It made my whole day.",
    },
    {
        "author": "mark_t",
        "title": "Rest Day",
        "content": "Rest day today. Did absolutely nothing and it was exactly what I needed. Running tomorrow. Probably.",
    },
    {
        "author": "lina_k",
        "title": "Slow Sunday Cooking",
        "content": "Made nothing but a big pot of beans and a loaf of bread all day. The apartment smells like a bakery and I'm in no hurry to leave it.",
    },
    {
        "author": "dave_n",
        "title": "Friday Deploy",
        "content": "We've all heard about Friday deploys. Did one anyway. It worked, which either proves I'm lucky or that the warnings were always about someone else.",
    },
    {
        "author": "amina_r",
        "title": "Almost Graduating",
        "content": "One semester left. I keep telling people that and they keep asking what's next. I don't know what's next. I'll probably just keep showing up.",
    },
]


# The oldest post - created separately so the pagination/date logic stays intact.
POST_44 = {
    "author": "dave_n",
    "title": "The First Deploy",
    "content": "The first project I ever deployed went live at 2am and broke within the hour. I've gotten a lot better since then, which is a low bar.",
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
        await db.execute(delete(models.PasswordResetToken))
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
    print("  No profile pictures (default avatars)")


if __name__ == "__main__":
    asyncio.run(populate())