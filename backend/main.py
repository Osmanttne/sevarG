# Loading in necessary libraries for gemini and reading .env
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
roboflow_api_key = os.getenv("ROBOFLOW_API_KEY")

client = genai.Client(api_key=api_key)

# myfile = client.files.upload(file=media / "image.png")


# while (True):
#     user_input = input("Enter an input:")
#     response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents=user_input,
# )
#     print(response.text)
#     if (user_input == "exit"):
#         break

# 1. Import the library
from inference_sdk import InferenceHTTPClient

# 2. Connect to your workflow
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=roboflow_api_key
)

# 3. Run your workflow on an image
result = client.run_workflow(
    workspace_name="training-data-for-independent-research",
    workflow_id="detect-count-and-visualize",
    images={
        "image": "YOUR_IMAGE.jpg" # Path to your image file
    },
    use_cache=True # Speeds up repeated requests
)

# 4. Get your results
print(result)