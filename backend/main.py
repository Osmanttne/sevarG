# Loading in necessary libraries for gemini and reading .env
from google import genai
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import *
import tempfile
import os
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import io

load_dotenv()

api_key = os.getenv("API_KEY")

client = genai.Client(api_key=api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sevarg.design",
        "http://localhost:5500",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def query_gemini_with_detection(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp:
        temp.write(await file.read())
        temp_path = temp.name
    
    try:
        img = Image.open(temp_path)
        img_width, img_height = img.size
        img.close()
        
        myfile = client.files.upload(file=temp_path)
        
        detection_prompt = f"""Analyze this image for accessibility features and barriers. 

The image dimensions are {img_width}x{img_height} pixels.

For EACH accessibility feature or barrier you identify, provide:
1. The feature type (e.g., "ramp", "stairs", "grab bar", "wheelchair accessible entrance", "elevator", "steep slope", "narrow doorway", etc.)
2. A bounding box with coordinates in this format: [x_min, y_min, x_max, y_max] where:
   - x_min, y_min is the top-left corner
   - x_max, y_max is the bottom-right corner
   - All coordinates are in pixels
   - x ranges from 0 to {img_width}
   - y ranges from 0 to {img_height}

Respond ONLY with a JSON array in this exact format:
[
  {{
    "feature": "feature name",
    "category": "accessible" or "barrier",
    "bbox": [x_min, y_min, x_max, y_max],
    "confidence": "high/medium/low"
  }}
]

Be specific with bounding boxes - they should tightly fit around each feature you identify."""

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[myfile, detection_prompt]
        )
        
        response_text = response.text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        try:
            detections = json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            detections = []
        
        annotated_image = create_annotated_image_from_detections(temp_path, detections)
        
        return {
            "detections": detections,
            "annotated_image": annotated_image,
            "image_dimensions": {"width": img_width, "height": img_height}
        }
    finally:
        try:
            os.unlink(temp_path)
        except PermissionError:
            import time
            time.sleep(0.1)
            try:
                os.unlink(temp_path)
            except:
                pass

def create_annotated_image_from_detections(image_path: str, detections: list) -> str:
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        print(f"Annotating {len(detections)} detections")
        
        colors = {
            "accessible": "lime",
            "barrier": "red",
            "default": "yellow"
        }
        
        for detection in detections:
            if 'bbox' not in detection:
                continue
                
            bbox = detection['bbox']
            if len(bbox) != 4:
                continue
            
            x_min, y_min, x_max, y_max = bbox
            
            category = detection.get('category', 'default')
            color = colors.get(category, colors['default'])
            
            draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=3)
            
            feature = detection.get('feature', 'detected')
            confidence = detection.get('confidence', '')
            label = f"{feature}"
            if confidence:
                label += f" ({confidence})"
            
            bbox_text = draw.textbbox((x_min, y_min - 22), label, font=font)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]
            
            draw.rectangle(
                [x_min, y_min - text_height - 6, x_min + text_width + 6, y_min],
                fill=color
            )
            
            draw.text((x_min + 3, y_min - text_height - 3), label, fill="black", font=font)
        
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_str}"
        
    except Exception as e:
        print(f"Error creating annotated image: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

async def generate_lowes_shopping_list(detections: list, analysis: str):
    barriers = [d for d in detections if d.get('category') == 'barrier']
    barrier_descriptions = "\n".join([f"- {d.get('feature', 'barrier')}" for d in barriers])
    
    shopping_prompt = f"""Based on these accessibility barriers identified in a building:

{barrier_descriptions}

And this analysis:
{analysis}

Create a detailed shopping list of products from Lowe's Home Improvement that would resolve these accessibility issues.

For EACH product, provide:
1. Product name
2. Estimated price range
3. Product category (e.g., "Accessibility", "Hardware", "Ramps", "Grab Bars")
4. Why this product helps
5. A realistic Lowe's product URL (use format: https://www.lowes.com/search?searchTerm=PRODUCT_NAME)

Respond ONLY with a JSON array in this exact format:
[
  {{
    "product_name": "Product Name",
    "price_range": "$XX - $XXX",
    "category": "Category",
    "description": "How this helps with accessibility",
    "url": "https://www.lowes.com/search?searchTerm=product-name"
  }}
]

Be specific and practical. Include 3-6 items that would genuinely help resolve the identified barriers."""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[shopping_prompt]
        )
        
        response_text = response.text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        shopping_list = json.loads(response_text.strip())
        return shopping_list
        
    except Exception as e:
        print(f"Error generating shopping list: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []

async def query_gemini_analysis(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp:
        temp.write(await file.read())
        temp_path = temp.name
    
    myfile = client.files.upload(file=temp_path)
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[myfile, "Identify if this building has disability access features. If not, suggest what could be added to help. Provide a detailed analysis."]
    )
    os.unlink(temp_path)
    return {"response": response.text}

@app.post("/gemini")
async def gemini_endpoint(file: UploadFile = File(...)):    
    print("Starting analysis")
    file_content = await file.read()
    from io import BytesIO
    analysis_file = UploadFile(
        file=BytesIO(file_content),
        filename=file.filename
    )
    detection_file = UploadFile(
        file=BytesIO(file_content),
        filename=file.filename
    )
    print("1: Running analysis and detection...")
    analysis_response = await query_gemini_analysis(analysis_file)
    detection_response = await query_gemini_with_detection(detection_file)
    
    print("2: Generating Lowe's shopping list...")
    shopping_list = await generate_lowes_shopping_list(
        detection_response["detections"],
        analysis_response["response"]
    )
    
    
    print("Pipeline complete!")
    
    return {
        "response": analysis_response["response"],
        "problem_image": detection_response["annotated_image"],
        "shopping_list": shopping_list,
        "detections": detection_response["detections"],
        "image_dimensions": detection_response["image_dimensions"]
    }