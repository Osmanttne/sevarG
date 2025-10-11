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
            use_cache=True
        )

        return {"response": result.json()}
    except Exception as e:
        return {"error": str(e)}

@app.post("/roboflow")
async def roboflow_endpoint(image: UploadFile = File(...)):
    response = await query_roboflow(image)
    return response