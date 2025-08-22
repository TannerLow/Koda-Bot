import os
from datetime import datetime, date
from typing import Optional

from dotenv import load_dotenv
import requests

from .model import GithubContributionDay


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def github_last_contrib(login: str) -> Optional[GithubContributionDay]:
    """Return the most recent contribution date as a datetime.date object."""
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
    
    last_date_str = None
    count: int = 0
    for week in weeks:
        for day in week["contributionDays"]:
            n = day["contributionCount"]
            if day["contributionCount"] > 0:
                last_date_str = day["date"]
                count = n
    
    if last_date_str:
        return GithubContributionDay(
            date=datetime.strptime(last_date_str, "%Y-%m-%d").date(),
            count=count
        )
    else:
        return None  # No contributions found

