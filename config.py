from agents import OpenAIChatCompletionsModel, AsyncOpenAI, RunConfig
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

exter_client = AsyncOpenAI(api_key= API_KEY, base_url= "https://generativelanguage.googleapis.com/v1beta/openai/")
model = OpenAIChatCompletionsModel(model= "gemini-2.0-flash", openai_client= exter_client)
config = RunConfig(model=model, model_provider= exter_client, tracing_disabled= True)
