from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from notion_client import Client as NotionClient
import httpx
import os
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

# --- Models ---
class ChatRequest(BaseModel):
    model: str  # e.g., 'claude', 'gpt', 'gemini', 'qwen'
    message: str
    context: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    model: str

class Note(BaseModel):
    name: str
    description: Optional[str] = None
    content: str

class LearningPlan(BaseModel):
    user_id: str
    goals: List[str]
    plan: List[str]

class NotionSaveRequest(BaseModel):
    title: str
    content: str

# --- Integration Placeholders ---
# Notion integration config (replace with your actual integration token and database ID)
NOTION_TOKEN = "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"
NOTION_DATABASE_ID = "21c5e35a991380a58298fb633226e432"
notion = NotionClient(auth=NOTION_TOKEN)

# --- Example Python learning topics by level ---
PYTHON_TOPICS = {
    "beginner": [
        "Introduction to Python",
        "Variables and Data Types",
        "Basic Operators",
        "Control Flow (if, for, while)",
        "Functions",
        "Lists and Dictionaries",
        "Basic Input/Output"
    ],
    "intermediate": [
        "Modules and Packages",
        "File Handling",
        "Error Handling",
        "List Comprehensions",
        "OOP: Classes and Objects",
        "Virtual Environments",
        "Testing with pytest"
    ],
    "advanced": [
        "Decorators",
        "Generators",
        "Context Managers",
        "Async Programming",
        "Type Hints",
        "Web Development (FastAPI)",
        "Working with APIs"
    ]
}

class LearningPlanRequest(BaseModel):
    user_id: str
    level: str  # 'beginner', 'intermediate', 'advanced'
    goals: Optional[List[str]] = None

# LLM API configuration
LLM_API_ENDPOINTS = {
    "claude": "https://api.anthropic.com/v1/messages",
    "gpt": "https://api.openai.com/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent"
}

LLM_API_KEYS = {
    "claude": os.getenv("CLAUDE_API_KEY", ""),
    "gpt": os.getenv("OPENAI_API_KEY", ""),
    "gemini": os.getenv("GEMINI_API_KEY", "")
}

async def call_llm(model: str, message: str, context: Optional[list] = None) -> str:
    try:
        if model == "claude":
            headers = {"x-api-key": LLM_API_KEYS["claude"], "content-type": "application/json"}
            payload = {
                "model": "claude-3-opus-20240229",
                "max_tokens": 256,
                "messages": context or []
            }
            payload["messages"].append({"role": "user", "content": message})
            async with httpx.AsyncClient() as client:
                resp = await client.post(LLM_API_ENDPOINTS["claude"], json=payload, headers=headers)
                if resp.status_code != 200:
                    return f"Claude API error: {resp.text}"
                data = resp.json()
                # Claude 3 returns content as a list of message objects
                if "content" in data:
                    return data["content"]
                elif "content" in data.get("completion", {}):
                    return data["completion"]["content"]
                return str(data)
        elif model == "gpt":
            headers = {"Authorization": f"Bearer {LLM_API_KEYS['gpt']}", "content-type": "application/json"}
            messages = context or []
            messages.append({"role": "user", "content": message})
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 256
            }
            async with httpx.AsyncClient() as client:
                resp = await client.post(LLM_API_ENDPOINTS["gpt"], json=payload, headers=headers)
                if resp.status_code != 200:
                    return f"OpenAI API error: {resp.text}"
                return resp.json()["choices"][0]["message"]["content"]
        elif model == "gemini":
            headers = {"content-type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": message}]}]
            }
            url = f"{LLM_API_ENDPOINTS['gemini']}?key={LLM_API_KEYS['gemini']}"
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    return f"Gemini API error: {resp.text}"
                data = resp.json()
                # Gemini 1.5 returns text in this nested structure
                return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Model {model} not supported yet."
    except Exception as e:
        return f"LLM call failed: {str(e)}"

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"message": "AgenticAI-PPL MCP server is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Maintain conversation context if provided
    context = request.context or []
    response = await call_llm(request.model, request.message, context)
    return ChatResponse(response=response, model=request.model)

@app.get("/notes", response_model=List[Note])
def list_notes():
    # Placeholder: return all notes
    return []

@app.post("/notes", response_model=Note)
def add_note(note: Note):
    # Placeholder: add note logic
    return note

@app.get("/learning-plan/{user_id}", response_model=LearningPlan)
def get_learning_plan(user_id: str):
    # Placeholder: fetch learning plan for user
    return LearningPlan(user_id=user_id, goals=["Learn Python"], plan=["Start with basics", "Practice exercises"])

@app.post("/learning-plan", response_model=LearningPlan)
def generate_learning_plan(req: LearningPlanRequest):
    topics = PYTHON_TOPICS.get(req.level.lower(), PYTHON_TOPICS["beginner"])
    plan = topics.copy()
    if req.goals:
        plan += req.goals
    return LearningPlan(user_id=req.user_id, goals=req.goals or [], plan=plan)

@app.post("/integrations/notion/save")
def save_to_notion(req: NotionSaveRequest):
    try:
        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Task": {  # <-- updated to match your Notion title property
                    "title": [
                        {"text": {"content": req.title}}
                    ]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": req.content}}
                        ]
                    }
                }
            ]
        )
        return {"status": "success", "notion_page_id": response["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrations/google-drive/upload")
def upload_to_drive():
    # Placeholder for Google Drive upload
    return {"status": "Not implemented"}

@app.post("/integrations/gmail/auth")
def gmail_auth():
    # Placeholder for Gmail authentication
    return {"status": "Not implemented"}

@app.post("/integrations/canva/create")
def create_canva_design():
    # Placeholder for Canva integration
    return {"status": "Not implemented"}

@app.post("/learning-plan/save-to-notion")
def save_learning_plan_to_notion(req: LearningPlanRequest):
    try:
        # Generate the learning plan as before
        topics = PYTHON_TOPICS.get(req.level.lower(), PYTHON_TOPICS["beginner"])
        plan = topics.copy()
        if req.goals:
            plan += req.goals
        plan_text = "\n".join(plan)
        # Save to Notion
        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Task": {
                    "title": [
                        {"text": {"content": f"Learning Plan for {req.user_id}"}}
                    ]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": plan_text}}
                        ]
                    }
                }
            ]
        )
        return {"status": "success", "notion_page_id": response["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notes/save-to-notion")
def save_note_to_notion(note: Note):
    try:
        response = notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Task": {
                    "title": [
                        {"text": {"content": note.name}}
                    ]
                }
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": note.content}}
                        ]
                    }
                }
            ]
        )
        return {"status": "success", "notion_page_id": response["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
