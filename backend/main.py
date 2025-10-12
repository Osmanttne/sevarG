# Loading in necessary libraries for gemini and reading .env
from google import genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from inference_sdk import InferenceHTTPClient
from fastapi import *
import tempfile
import os
import json

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

async def get_product_suggestions(accessibility_analysis: str):
    """
    Takes the accessibility analysis and returns product suggestions with Lowe's search links
    """
    prompt = f"""Based on this accessibility analysis:

{accessibility_analysis}

Please suggest 3-5 specific products that could help improve accessibility. For each product, provide:
1. Product name (be specific, e.g., "36-inch Grab Bar" not just "Grab Bar")
2. Brief description of how it helps
3. A search term optimized for Lowe's website (2-4 words)

Format your response as a JSON array like this:
[
  {{
    "product": "Product Name",
    "description": "How it helps with accessibility",
    "search_term": "search term"
  }}
]

Only respond with the JSON array, no other text."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt]
    )
    
    # Extract JSON from response
    response_text = response.text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    try:
        products = json.loads(response_text.strip())
        
        # Add Lowe's links to each product
        for product in products:
            search_term = product.get("search_term", product["product"])
            # Create Lowe's search URL
            lowes_search = search_term.replace(" ", "+")
            product["lowes_link"] = f"https://www.lowes.com/search?searchTerm={lowes_search}"
        
        return products
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return [{"error": "Could not parse product suggestions", "raw_response": response_text}]

@app.post("/gemini")
async def gemini_endpoint(file: UploadFile = File(...)):
    response = await query_gemini(file)
    return response

@app.post("/gemini-with-products")
async def gemini_with_products_endpoint(file: UploadFile = File(...)):
    """
    Analyzes the image for accessibility AND provides product suggestions with Lowe's links
    """
    # Get accessibility analysis
    analysis_response = await query_gemini(file)
    analysis_text = analysis_response.get("response", "")
    
    # Get product suggestions based on the analysis
    products = await get_product_suggestions(analysis_text)
    
    return {
        "analysis": analysis_text,
        "products": products
    }

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