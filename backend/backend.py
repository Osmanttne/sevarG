# Loading in necessary libraries for gemini and reading .env
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

client = genai.Client(api_key=api_key)

# myfile = client.files.upload(file=media / "image.png")


while (True):
    user_input = input("Enter an input:")
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_input,
)
    print(response.text)
    if (user_input == "exit"):
        break
