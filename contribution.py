import os
import discord
from discord.ext import commands
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# --- LOAD ENV ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --- HELPER FUNCTIONS ---

def date_utc(delta_days: int = 0) -> str:
    """Return YYYY-MM-DD string for UTC date with offset in days (timezone-aware)."""
    target_date = datetime.now(timezone.utc) + timedelta(days=delta_days)
    return target_date.strftime("%Y-%m-%d")

def github_contribs_on_date(login: str, delta_days: int = 0) -> int:
    """Fetch contribution count for a specific date in UTC."""
    target_str = date_utc(delta_days)

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }"""

    headers = {
        "Accept": "application/json",
        "User-Agent": "discord-contrib-bot",
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }

    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"login": login}},
        headers=headers
    )

    if resp.status_code != 200:
        raise RuntimeError(f"GitHub API error: {resp.status_code} {resp.text}")

    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GitHub GraphQL error: {data['errors']}")

    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    
    # Count contributions for the target date
    for week in weeks:
        for day in week["contributionDays"]:
            if day["date"] == target_str:
                return int(day["contributionCount"])
    return 0

from datetime import datetime, timezone, timedelta

def github_last_contrib_date(login: str, max_days: int = 3) -> str:
    """
    Return the most recent date the user contributed within the last `days` days.
    """
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }"""

    headers = {
        "Accept": "application/json",
        "User-Agent": "discord-contrib-bot"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"login": login}},
        headers=headers
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GitHub GraphQL error: {data['errors']}")

    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

    # Compute the last `days` UTC dates
    today = datetime.now(timezone.utc).date()
    recent_dates = { (today - timedelta(days=i)).isoformat() for i in range(max_days) }

    # Flatten all days and find the latest contribution in the last `days`
    last_date = None
    for week in weeks:
        for day in week["contributionDays"]:
            if day["date"] in recent_dates and day["contributionCount"] > 0:
                if not last_date or day["date"] > last_date:
                    last_date = day["date"]

    return last_date or "No contributions found in the last {} days".format(max_days)


# --- DISCORD BOT ---

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command()
async def contribs(ctx, github_username: str):
    """
    Fetch GitHub contributions for yesterday, today, tomorrow (UTC) and last contribution date.
    """
    try:
        yesterday = github_contribs_on_date(github_username, delta_days=-1)
        today = github_contribs_on_date(github_username, delta_days=0)
        tomorrow = github_contribs_on_date(github_username, delta_days=1)
        last_date = github_last_contrib_date(github_username)
        
        await ctx.send(
            f"📊 GitHub contributions for **{github_username}** (UTC):\n"
            f"Yesterday: **{yesterday}**\n"
            f"Today: **{today}**\n"
            f"Tomorrow: **{tomorrow}**\n"
            f"Most recent contribution date: **{last_date}**"
        )
    except Exception as e:
        await ctx.send(f"❌ Error fetching contributions: {e}")

bot.run(DISCORD_TOKEN)
