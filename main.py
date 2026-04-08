# echo "# AI-TALENT - главный файл приложения" >> main.py
# echo "# Этот проект ищет разработчиков на GitHub" >> main.py

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Optional
import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = FastAPI(
    title="AI Talent API",
    description="API для поиска и анализа разработчиков на GitHub",
    version="1.0.0"
)

# GitHub API настройки
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_HEADERS = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
} if GITHUB_TOKEN else {}

# Базовый URL GitHub API
GITHUB_API = "https://api.github.com"

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С GITHUB API ==========

def search_developers(language: str = "python", location: str = None, per_page: int = 30):
    """
    Поиск разработчиков по языку программирования
    
    Args:
        language: язык программирования (python, javascript, java и т.д.)
        location: местоположение (опционально)
        per_page: количество результатов
    
    Returns:
        list: список разработчиков
    """
    url = f"{GITHUB_API}/search/users"
    
    # Формируем поисковый запрос
    query = f"language:{language}"
    if location:
        query += f" location:{location}"
    
    params = {
        "q": query,
        "per_page": min(per_page, 100),
        "sort": "followers",
        "order": "desc"
    }
    
    try:
        response = requests.get(url, headers=GITHUB_HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка поиска: {e}")
        return []


def get_user_repos(username: str, max_repos: int = 50):
    """
    Получение репозиториев пользователя
    
    Args:
        username: имя пользователя GitHub
        max_repos: максимальное количество репозиториев
    
    Returns:
        list: список репозиториев
    """
    url = f"{GITHUB_API}/users/{username}/repos"
    params = {
        "per_page": min(max_repos, 100),
        "sort": "updated",
        "direction": "desc"
    }
    
    try:
        response = requests.get(url, headers=GITHUB_HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка получения репозиториев {username}: {e}")
        return []


def get_user_info(username: str):
    """
    Получение детальной информации о пользователе
    
    Args:
        username: имя пользователя GitHub
    
    Returns:
        dict: информация о пользователе
    """
    url = f"{GITHUB_API}/users/{username}"
    
    try:
        response = requests.get(url, headers=GITHUB_HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка получения информации о {username}: {e}")
        return None


def extract_skills_from_repos(repos: List[dict]) -> dict:
    """
    Извлечение навыков из репозиториев
    
    Args:
        repos: список репозиториев
    
    Returns:
        dict: словарь с навыками и их частотой
    """
    skills = {}
    
    for repo in repos:
        # Язык программирования
        language = repo.get("language")
        if language:
            skills[language] = skills.get(language, 0) + 1
        
        # Извлечение технологий из описания
        description = repo.get("description", "")
        if description:
            tech_keywords = [
                "Django", "Flask", "FastAPI", "React", "Vue", "Angular",
                "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes",
                "AWS", "GCP", "Azure", "TensorFlow", "PyTorch", "Pandas",
                "Numpy", "Scrapy", "Celery", "RabbitMQ", "GraphQL", "REST"
            ]
            
            for tech in tech_keywords:
                if tech.lower() in description.lower():
                    skills[tech] = skills.get(tech, 0) + 1
    
    # Сортируем навыки по частоте
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_skills)


# ========== API ЭНДПОИНТЫ ==========

@app.get("/")
async def root():
    """Главная страница API"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Talent API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
            .endpoint {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .method {
                display: inline-block;
                background: #4CAF50;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            .url {
                font-family: monospace;
                font-size: 14px;
                margin-left: 10px;
                color: #007bff;
            }
            .description {
                margin-top: 8px;
                color: #666;
                margin-left: 60px;
            }
            .example {
                background: #f0f0f0;
                padding: 8px;
                border-radius: 4px;
                margin-top: 8px;
                font-family: monospace;
                font-size: 12px;
            }
            .search-box {
                margin: 20px 0;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            input, select, button {
                padding: 10px;
                margin: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background: #4CAF50;
                color: white;
                cursor: pointer;
                border: none;
            }
            button:hover {
                background: #45a049;
            }
            .result {
                margin-top: 20px;
            }
            .developer-card {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .skills {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 10px;
            }
            .skill-tag {
                background: #e0e0e0;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <h1>🚀 AI Talent API</h1>
        <p>API для поиска и анализа разработчиков на GitHub</p>
        
        <div class="search-box">
            <h3>🔍 Поиск разработчиков</h3>
            <input type="text" id="language" placeholder="Язык программирования" value="python">
            <input type="text" id="location" placeholder="Местоположение (опционально)">
            <button onclick="searchDevelopers()">Найти</button>
            <div id="results" class="result"></div>
        </div>
        
        <h2>📚 Доступные эндпоинты</h2>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url">/search</span>
            <div class="description">Поиск разработчиков по языку программирования</div>
            <div class="example">Пример: <a href="/search?language=python&location=moscow">/search?language=python&location=moscow</a></div>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url">/developers/{username}</span>
            <div class="description">Детальная информация о разработчике</div>
            <div class="example">Пример: <a href="/developers/octocat">/developers/octocat</a></div>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url">/developers/{username}/repos</span>
            <div class="description">Репозитории разработчика</div>
            <div class="example">Пример: <a href="/developers/octocat/repos">/developers/octocat/repos</a></div>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <span class="url">/top/{language}</span>
            <div class="description">Топ разработчиков по языку</div>
            <div class="example">Пример: <a href="/top/python">/top/python</a></div>
        </div>
        
        <script>
            async function searchDevelopers() {
                const language = document.getElementById('language').value;
                const location = document.getElementById('location').value;
                const resultsDiv = document.getElementById('results');
                
                let url = `/search?language=${language}`;
                if (location) url += `&location=${location}`;
                
                resultsDiv.innerHTML = '<p>⏳ Загрузка...</p>';
                
                try {
                    const response = await fetch(url);
                    const data = await response.json();
                    
                    if (data.length === 0) {
                        resultsDiv.innerHTML = '<p>❌ Разработчики не найдены</p>';
                        return;
                    }
                    
                    resultsDiv.innerHTML = `<h3>✅ Найдено: ${data.length} разработчиков</h3>`;
                    
                    for (const dev of data) {
                        resultsDiv.innerHTML += `
                            <div class="developer-card">
                                <strong>👤 ${dev.username}</strong>
                                <br>
                                <a href="${dev.profile}" target="_blank">${dev.profile}</a>
                                <div class="skills">
                                    ${dev.skills.split(', ').map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                                </div>
                            </div>
                        `;
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `<p>❌ Ошибка: ${error.message}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """)


@app.get("/search")
def search_developers_endpoint(
    language: str = Query("python", description="Язык программирования"),
    location: Optional[str] = Query(None, description="Местоположение (город или страна)"),
    limit: int = Query(30, description="Максимальное количество результатов", ge=1, le=50)
):
    """
    Поиск разработчиков по языку программирования
    
    - **language**: язык программирования (python, javascript, java, go, rust и т.д.)
    - **location**: опциональное местоположение (moscow, berlin, london, usa)
    - **limit**: количество результатов (от 1 до 50)
    
    Возвращает список разработчиков с их профилями и предполагаемыми навыками.
    """
    developers = search_developers(language, location, per_page=limit)
    results = []
    
    for dev in developers[:limit]:
        username = dev["login"]
        
        # Получаем репозитории для анализа навыков
        repos = get_user_repos(username, max_repos=30)
        
        # Извлекаем навыки из репозиториев
        skills_dict = extract_skills_from_repos(repos)
        
        # Формируем список навыков (топ-5)
        top_skills = list(skills_dict.keys())[:5]
        
        # Если навыков не найдено, добавляем язык по умолчанию
        if not top_skills:
            top_skills = [language.capitalize()]
        
        results.append({
            "username": username,
            "profile": dev["html_url"],
            "avatar_url": dev.get("avatar_url"),
            "skills": ", ".join(top_skills),
            "repos_count": len(repos),
            "languages": list(skills_dict.keys())[:3]
        })
    
    return results


@app.get("/developers/{username}")
def get_developer_info(username: str):
    """
    Получение детальной информации о разработчике
    
    - **username**: имя пользователя GitHub
    
    Возвращает полную информацию о разработчике.
    """
    user_info = get_user_info(username)
    
    if not user_info:
        raise HTTPException(status_code=404, detail=f"Разработчик {username} не найден")
    
    repos = get_user_repos(username, max_repos=50)
    skills = extract_skills_from_repos(repos)
    
    return {
        "username": user_info.get("login"),
        "name": user_info.get("name"),
        "bio": user_info.get("bio"),
        "company": user_info.get("company"),
        "location": user_info.get("location"),
        "email": user_info.get("email"),
        "followers": user_info.get("followers"),
        "following": user_info.get("following"),
        "public_repos": user_info.get("public_repos"),
        "profile_url": user_info.get("html_url"),
        "avatar_url": user_info.get("avatar_url"),
        "created_at": user_info.get("created_at"),
        "top_skills": list(skills.keys())[:10],
        "recent_repos": [
            {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "url": repo.get("html_url")
            }
            for repo in repos[:5]
        ]
    }


@app.get("/developers/{username}/repos")
def get_developer_repos(username: str, limit: int = Query(20, le=100)):
    """
    Получение репозиториев разработчика
    
    - **username**: имя пользователя GitHub
    - **limit**: количество репозиториев
    
    Возвращает список репозиториев с их характеристиками.
    """
    repos = get_user_repos(username, max_repos=limit)
    
    if not repos:
        raise HTTPException(status_code=404, detail=f"Репозитории для {username} не найдены")
    
    return {
        "username": username,
        "total": len(repos),
        "repositories": [
            {
                "name": repo.get("name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "size_kb": repo.get("size"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "url": repo.get("html_url")
            }
            for repo in repos
        ]
    }


@app.get("/top/{language}")
def get_top_developers(
    language: str,
    location: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Получение топ разработчиков по языку
    
    - **language**: язык программирования
    - **location**: опциональное местоположение
    - **limit**: количество результатов
    
    Возвращает топ разработчиков, отсортированных по подписчикам.
    """
    developers = search_developers(language, location, per_page=limit)
    
    results = []
    for dev in developers[:limit]:
        user_info = get_user_info(dev["login"])
        if user_info:
            results.append({
                "username": dev["login"],
                "name": user_info.get("name"),
                "followers": user_info.get("followers"),
                "public_repos": user_info.get("public_repos"),
                "profile_url": dev["html_url"],
                "avatar_url": dev.get("avatar_url")
            })
    
    # Сортируем по подписчикам
    results.sort(key=lambda x: x["followers"], reverse=True)
    
    return {
        "language": language,
        "location": location or "worldwide",
        "count": len(results),
        "developers": results
    }


@app.get("/health")
def health_check():
    """Проверка статуса API"""
    return {
        "status": "healthy",
        "github_token_configured": bool(GITHUB_TOKEN),
        "api_version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
