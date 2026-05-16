import os
import json
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any
from jinja2 import Template
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("github-card-tools")

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-flash-lite-latest")

@mcp.tool()
async def scrape_github(username: str) -> dict:
    """Fetch GitHub stats for a given username."""
    headers = {}
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        
    async with httpx.AsyncClient(headers=headers) as client:
        # User info
        user_resp = await client.get(f"https://api.github.com/users/{username}")
        user_resp.raise_for_status()
        user_data = user_resp.json()

        # Repos
        repos_resp = await client.get(f"https://api.github.com/users/{username}/repos?sort=stars&per_page=30")
        repos_resp.raise_for_status()
        repos_data = repos_resp.json()

    # Aggregate languages
    languages = {}
    top_repos = []
    for repo in repos_data:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
        
        if len(top_repos) < 6:
            top_repos.append({
                "name": repo["name"],
                "stars": repo["stargazers_count"],
                "language": repo["language"],
                "description": repo["description"]
            })

    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "name": user_data.get("name") or username,
        "avatar_url": user_data.get("avatar_url"),
        "bio": user_data.get("bio"),
        "location": user_data.get("location"),
        "public_repos": user_data.get("public_repos"),
        "followers": user_data.get("followers"),
        "top_repos": top_repos,
        "languages": [l[0] for l in sorted_langs[:5]]
    }

@mcp.tool()
async def analyze_profile(github_data: dict) -> dict:
    """Analyze GitHub profile using Gemini to get developer vibe and theme."""
    prompt = f"""
    Analyze this GitHub user data and return a JSON object with:
    1. developer_vibe (1 sentence personality)
    2. top_skills (list of 3)
    3. fun_fact (something clever inferred from their repos)
    4. card_theme (one of: "hacker", "builder", "researcher", "designer", "open-source-hero")

    GitHub Data: {json.dumps(github_data)}
    
    Return ONLY valid JSON.
    """
    
    response = model.generate_content(prompt)
    # Basic JSON cleaning in case Gemini adds markdown blocks
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:-3].strip()
    elif text.startswith("```"):
        text = text[3:-3].strip()
        
    return json.loads(text)

@mcp.tool()
async def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """Generate a self-contained HTML string for a beautiful dev card."""
    template_str = """
    <div class="card {{ theme }}">
        <style>
            .card { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; border-radius: 12px; max-width: 400px; color: #fff; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
            .hacker { background: #0d1117; border: 1px solid #238636; }
            .builder { background: #f6f8fa; color: #24292f; border: 1px solid #d0d7de; }
            .researcher { background: #051e3e; border: 1px solid #1e3a8a; }
            .designer { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .open-source-hero { background: #2ea44f; }
            .avatar { width: 80px; height: 80px; border-radius: 50%; border: 3px solid rgba(255,255,255,0.2); margin-bottom: 10px; }
            .builder .avatar { border-color: rgba(0,0,0,0.1); }
            .badge { display: inline-block; padding: 4px 10px; border-radius: 15px; font-size: 12px; background: rgba(255,255,255,0.15); margin-right: 5px; margin-bottom: 5px; border: 1px solid rgba(255,255,255,0.1); }
            .builder .badge { background: rgba(0,0,0,0.05); border-color: rgba(0,0,0,0.1); }
            .repo { font-size: 13px; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); opacity: 0.9; }
            .builder .repo { border-top-color: rgba(0,0,0,0.1); }
            .stats { display: flex; gap: 20px; margin: 15px 0; padding: 10px 0; border-top: 1px solid rgba(255,255,255,0.1); border-bottom: 1px solid rgba(255,255,255,0.1); }
            .builder .stats { border-color: rgba(0,0,0,0.1); }
            .vibe { font-style: italic; margin: 10px 0; line-height: 1.4; opacity: 0.9; }
        </style>
        <img src="{{ github_data.avatar_url }}" class="avatar" />
        <h2 style="margin: 0;">{{ github_data.name }}</h2>
        <p style="font-size: 14px; opacity: 0.7; margin: 2px 0;">@{{ username }}</p>
        <p class="vibe">"{{ analysis.developer_vibe }}"</p>
        <div style="margin: 10px 0;">
            {% for skill in analysis.top_skills %}
            <span class="badge">{{ skill }}</span>
            {% endfor %}
        </div>
        <div class="stats">
            <span><strong>{{ github_data.public_repos }}</strong> Repos</span>
            <span><strong>{{ github_data.followers }}</strong> Followers</span>
        </div>
        <div style="margin-top: 10px;">
            <strong style="font-size: 14px;">TOP PROJECTS</strong>
            {% for repo in github_data.top_repos[:3] %}
            <div class="repo">
                <strong>{{ repo.name }}</strong>: {{ repo.language }} | ⭐ {{ repo.stars }}
            </div>
            {% endfor %}
        </div>
        <p style="font-size: 11px; margin-top: 15px; opacity: 0.6; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;">
            💡 {{ analysis.fun_fact }}
        </p>
    </div>
    """
    template = Template(template_str)
    return template.render(
        username=username,
        github_data=github_data,
        analysis=analysis,
        theme=analysis.get("card_theme", "hacker")
    )

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """Saves the HTML to static/cards/{username}.html."""
    path = f"static/cards/{username}.html"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return f"/static/cards/{username}.html"

if __name__ == "__main__":
    mcp.run()
