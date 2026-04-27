import os
import requests
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone

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
