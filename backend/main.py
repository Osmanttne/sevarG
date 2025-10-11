# Loading in necessary libraries for gemini and reading .env
from google import genai
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient
from fastapi import *
import os

load_dotenv()

api_key = os.getenv("API_KEY")
roboflow_api_key = os.getenv("ROBOFLOW_API_KEY")

client = genai.Client(api_key=api_key)

app = FastAPI()

async def query_gemini(file: UploadFile):
    
    myfile = client.files.upload(file=file.file)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[myfile, "Identify if this building has disability access features. If not, suggest what could be added to help."]
    )
    return {"response": response}

@app.post("/")
async def gemini_endpoint(file: UploadFile = File(...)):
    response = await query_gemini(file)
    return response


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