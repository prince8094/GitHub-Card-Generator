import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.genai import types
from agent import github_card_agent
import uvicorn

app = FastAPI(title="GitHub Dev Card Generator API")

# 7. Add CORS middleware allowing all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directories exist
os.makedirs("static/cards", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Sets up InMemorySessionService and InMemoryMemoryService
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

# 3. Creates a Runner bound to the agent and services
runner = Runner(
    app_name="github-card-generator",
    agent=github_card_agent,
    session_service=session_service,
    memory_service=memory_service,
    auto_create_session=True
)

class GenerateRequest(BaseModel):
    username: str

# 6. Exposes GET /health for Cloud Run health checks
@app.get("/health")
async def health():
    return {"status": "healthy"}

# 4. Exposes POST /generate endpoint
@app.post("/generate")
async def generate_card(request: GenerateRequest):
    username = request.username
    prompt = f"Generate a dev card for {username}"
    
    try:
        # Wrap the prompt in a Content object
        message = types.Content(
            parts=[types.Part(text=prompt)],
            role="user"
        )
        
        # Streams the agent events
        async for event in runner.run_async(
            user_id="default_user",
            session_id=username,
            new_message=message
        ):
            pass
            
        # After agent finishes, check for the card file
        card_path = f"static/cards/{username}.html"
        if not os.path.exists(card_path):
            raise HTTPException(status_code=500, detail="Agent finished but card file was not created.")
            
        with open(card_path, "r", encoding="utf-8") as f:
            card_html = f.read()
            
        return {
            "status": "success",
            "username": username,
            "card_url": f"/static/cards/{username}.html",
            "html": card_html
        }
    except Exception as e:
        print(f"Error generating card for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 5. Exposes GET /card/{username} to serve saved cards
@app.get("/card/{username}")
async def get_card(username: str):
    path = f"static/cards/{username}.html"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Card not found.")
    
    with open(path, "r", encoding="utf-8") as f:
        return {"html": f.read()}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
