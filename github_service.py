import requests

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
# Правильные переменные
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
BASE_URL = "https://api.github.com"

# Заголовки с токеном
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def search_developers(language="python", location="usa", per_page=20, page=1):
    """Поиск разработчиков по языку и местоположению"""
    url = f"{BASE_URL}/search/users"
    params = {
            "q": f"language:{language} location:{location}",
            "per_page": per_page,
            "page": page
    }
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code != 200:
        print(f"Ошибка: {response.status_code}")
        print(response.text)
        return []
    
    data = response.json()
    return data.get("items", [])

def get_user_repos(username):
    """Получение репозиториев пользователя"""
    url = f"{BASE_URL}/users/{username}/repos"
    params = {"per_page": 30, "sort": "updated"}
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code != 200:
        print(f"Ошибка: {response.status_code}")
        return []
    
    return response.json()

# Тестирование
if __name__ == "__main__":
    # Поиск разработчиков
    developers = search_developers("python", "moscow")
    print(f"Найдено разработчиков: {len(developers)}")
    
    for dev in developers:
        print(f"\n👤 {dev['login']}")
        
        # Получаем репозитории
        repos = get_user_repos(dev['login'])
        print(f"   Репозиториев: {len(repos)}")
        
        for repo in repos[:3]:  # первые 3
            stars = repo.get('stargazers_count', 0)
            language = repo.get('language', 'Unknown')
            print(f"   📁 {repo['name']} ⭐{stars} ({language})")
            