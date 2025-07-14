# main.py
from fastapi import FastAPI, Query
from pydantic import BaseModel
from agents import Agent, Runner
from fastapi.middleware.cors import CORSMiddleware
import json
from config import config
import requests
import os

app = FastAPI()

API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY")
CSE_ID = os.environ.get("CSE_ID")

class Question(BaseModel):
    question: str


def load_faq_text():
    with open("faq.json", "r") as f:
        faq_list = json.load(f)

    # Convert to plain text format for Gemini prompt
    return "\n".join([f"Q: {faq['question']}\nA: {faq['answer']}" for faq in faq_list])

faq_knowledge = load_faq_text()

@app.post("/ask")
async def ask_faq(question: Question):
    prompt = f"""
    You are an intelligent e-commerce assistant. Use the following FAQ to answer the user's question.

    FAQ:
    {faq_knowledge}

    User's Question: {question.question}
    Answer:
    """
    agent = Agent(
        name="e-commerce-assistant",
        instructions="You are an intelligent e-commerce assistant. Use the FAQ to answer the user's question.",
    )
    result = await Runner.run (agent, prompt, run_config=config)
    return { "answer": result.final_output }

@app.get("/search-linkedin")
def search_linkedin(name: str = Query(..., min_length=2)):
    query = f"{name} site:linkedin.com/in"
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "q": query,
        "key": API_KEY,
        "cx": CSE_ID,
    }

    response = requests.get(url, params=params)
    data = response.json()

    profiles = []
    for item in data.get("items", []):
        link = item.get("link", "")
        if "linkedin.com/in/" in link:
            profiles.append(link)

    return {"profiles": profiles[:5]}  # Return top 5 only

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 Allow everything (for development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
