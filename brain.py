from fastapi import FastAPI, File, UploadFile
import requests
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="TurkeyApp AI Brain")

# Setup API Key
HF_TOKEN = os.getenv("HF_TOKEN", "REPLACE_WITH_YOUR_HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32"

@app.get("/")
def read_root():
    return {"status": "Brain is operational"}

@app.post("/vectorize")
async def vectorize(image: UploadFile = File(...)):
    """Receives an image and returns its CLIP embedding vector."""
    try:
        content = await image.read()
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        response = requests.post(HF_API_URL, headers=headers, data=content)
        
        if response.status_code != 200:
            return {"error": f"Hugging Face error: {response.text}", "status_code": response.status_code}
            
        vector = response.json()
        return {"vector": vector}
    except Exception as e:
        return {"error": str(e)}

@app.post("/embed-text")
async def embed_text(params: dict):
    """Receives text and returns its CLIP embedding vector."""
    try:
        text = params.get("text", "")
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": text}
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            return {"error": response.text}
            
        vector = response.json()
        return {"vector": vector}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
