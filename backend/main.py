from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import duckduckgo_search, deduplicate_and_format_sources
from ai_tools import generate_query, summarize_sources, generate_final_answer, reflect_on_summary
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import pathlib
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from app_mcp import run_research_agent
app = FastAPI(title="Research Agent API", version="1.0")



#Only allow the react frontend 

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str
    max_iterations: int = 1

@app.post("/research")
def research_endpoint(request: QuestionRequest):
    try:
        print("startin search agent")
        return run_research_agent(request.question, request.max_iterations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

