import os
import requests
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone
from google.cloud import vision
from pexels_api import API as PexelsAPI

load_dotenv()

# AI Config
HF_TOKEN = os.getenv("HF_TOKEN")
# Using the CLIP model via Hugging Face Inference API
API_URL = "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32"
headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

# Pinecone Config
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "turkey-app")

async def get_image_embeddings(image_data: bytes) -> list:
    """Gets CLIP image embeddings via HF Cloud API."""
    try:
        # Note: HF CLIP API expects the image bytes directly
        response = requests.post(API_URL, headers=headers, data=image_data)
        res = response.json()
        if isinstance(res, list) and len(res) > 0:
            return res
        return []
    except Exception as e:
        print(f"HF Image API Error: {e}")
        return []

async def get_text_embeddings(text: str) -> list:
    """Gets CLIP text embeddings via HF Cloud API."""
    try:
        payload = {"inputs": text}
        response = requests.post(API_URL, headers=headers, json=payload)
        res = response.json()
        if isinstance(res, list) and len(res) > 0:
            return res
        return []
    except Exception as e:
        print(f"HF Text API Error: {e}")
        return []

async def query_pinecone(vector: list, top_k: int = 24) -> list:
    """Query Pinecone for similar image IDs."""
    if not vector: return []
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX)
        results = index.query(vector=vector, top_k=top_k, include_metadata=False)
        return [match.id for match in results.matches]
    except Exception as e:
        print(f"Pinecone Query Error: {e}")
        return []

async def upsert_to_pinecone(image_id: str, vector: list):
    """Upload vector to Pinecone."""
    if not vector: return
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX)
        index.upsert(vectors=[(image_id, vector)])
    except Exception as e:
        print(f"Pinecone Upsert Error: {e}")


# Pexels Config
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "b2bh331NfhOQEVuBH26J0UBRQPRvceShOTAEkKCevBIqitGPPU31qmmS")

# Google Vision Config
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "AIzaSyCFbxFd8ZWZmkQrmv0cCFxGSf-WOgLTdHw")
VISION_URL = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"

async def analyze_image_labels(image_path: str) -> list[str]:
    """Uses Google Cloud Vision REST API to extract labels from an image."""
    try:
        import base64
        with open(image_path, "rb") as image_file:
            content = base64.b64encode(image_file.read()).decode("utf-8")
        
        payload = {
            "requests": [
                {
                    "image": {"content": content},
                    "features": [{"type": "LABEL_DETECTION", "maxResults": 10}]
                }
            ]
        }
        
        response = requests.post(VISION_URL, json=payload)
        res = response.json()
        
        # Extract labels from the response
        if "responses" in res and res["responses"]:
            annotations = res["responses"][0].get("labelAnnotations", [])
            return [label["description"] for label in annotations[:8]]
            
        return []
    except Exception as e:
        print(f"Vision API REST Error: {e}")
        return []

async def search_pexels_photos(query: str, per_page: int = 15) -> list[dict]:
    """Searches Pexels for high-quality photos matching the query."""
    try:
        api = PexelsAPI(PEXELS_API_KEY)
        api.search(query, page=1, results_per_page=per_page)
        photos = api.get_entries()
        return [
            {
                "url": photo.large2x,
                "thumbnail": photo.medium,
                "photographer": photo.photographer,
                "photographer_url": photo.photographer_url,
                "alt": f"Photo by {photo.photographer} via Pexels"
            }
            for photo in photos
        ]
    except Exception as e:
        print(f"Pexels API Error: {e}")
        return []
