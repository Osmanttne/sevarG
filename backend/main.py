# Loading in necessary libraries for gemini and reading .env
from google import genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from inference_sdk import InferenceHTTPClient
from fastapi import *
import tempfile
import os

load_dotenv()

api_key = os.getenv("API_KEY")
roboflow_api_key = os.getenv("ROBOFLOW_API_KEY")

client = genai.Client(api_key=api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def query_gemini(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp:
        temp.write(await file.read())
        temp_path = temp.name
    myfile = client.files.upload(file=temp_path)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[myfile, "Identify if this building has disability access features. If not, suggest what could be added to help."]
    )
    return {"response": response.text}

@app.post("/gemini")
async def gemini_endpoint(file: UploadFile = File(...)):
    response = await query_gemini(file)
    return response

async def query_roboflow(image: UploadFile):
    try:
        client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=roboflow_api_key
        )

        result = client.run_workflow(
            workspace_name="training-data-for-independent-research",
            workflow_id="detect-count-and-visualize",
            images={
                "image": image.file
            },
            use_cache=True # Speeds up repeated requests
        )

        return {"response": result.json()}
    except Exception as e:
        return {"error": str(e)}

@app.post("/roboflow")
async def roboflow_endpoint(image: UploadFile = File(...)):
    response = await query_roboflow(image)
    return response