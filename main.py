# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
from agents import Agent, Runner
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from config import config


# Load .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


app = FastAPI()

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

    # model = genai.GenerativeModel("gemini-1.5-flash")  # You can use "gemini-1.5-pro" if preferred
    # response = model.generate_content(prompt)
    # answer = response.text.strip()

    # return { "answer": answer }
    agent = Agent(
        name="e-commerce-assistant",
        instructions="You are an intelligent e-commerce assistant. Use the following FAQ to answer the user's question.",
    )
    result = await Runner.run (agent, prompt, run_config=config)
    return { "answer": result.final_output }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 Allow everything (for development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
