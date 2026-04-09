import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"

HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def build_search_query(language: str, location: Optional[str] = None) -> str:
    query = f"language:{language}"
    if location:
        query += f" location:{location}"
    return query


def search_users(query: str, per_page: int = 30):
    url = f"{BASE_URL}/search/users"
    params = {"q": query, "per_page": min(per_page, 100), "sort": "followers", "order": "desc"}
    response = requests.get(url, headers=HEADERS, params=params, timeout=25)
    response.raise_for_status()
    return response.json().get("items", [])


def get_user_info(username: str):
    url = f"{BASE_URL}/users/{username}"
    response = requests.get(url, headers=HEADERS, timeout=25)
    if response.status_code != 200:
        return None
    return response.json()


def get_user_repos(username: str, max_repos: int = 50):
    url = f"{BASE_URL}/users/{username}/repos"
    params = {"per_page": min(max_repos, 100), "sort": "updated", "direction": "desc"}
    response = requests.get(url, headers=HEADERS, params=params, timeout=25)
    if response.status_code != 200:
        return []
    return response.json()
