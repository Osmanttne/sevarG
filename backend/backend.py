# Loading in necessary libraries for gemini and reading .env
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a poem about the sea in 4 lines.",
)

print(response.text)