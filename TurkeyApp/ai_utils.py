import requests
import os
import io
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─── Microservice Configuration ───────────────────────────
# For Capstone: The Reflex backend calls this local FastAPI "Brain" service.
BRAIN_URL = os.getenv("BRAIN_URL", "http://localhost:8001")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "REPLACE_WITH_YOUR_PINECONE_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "turkey-app")

async def get_image_embeddings(image_data: bytes) -> list:
    """Calls the local FastAPI 'Brain' to vectorize the image."""
    try:
        files = {"image": ("image.jpg", image_data, "image/jpeg")}
        response = requests.post(f"{BRAIN_URL}/vectorize", files=files)
        
        if response.status_code != 200:
            print(f"Brain Error: {response.text}")
            return []
            
        data = response.json()
        return data.get("vector", [])
    except Exception as e:
        print(f"Failed to connect to Brain microservice: {e}")
        return []

async def get_text_embeddings(text: str) -> list:
    """Calls the local FastAPI 'Brain' to vectorize the text query."""
    try:
        response = requests.post(f"{BRAIN_URL}/embed-text", json={"text": text})
        
        if response.status_code != 200:
            print(f"Brain Text Error: {response.text}")
            return []
            
        data = response.json()
        return data.get("vector", [])
    except Exception as e:
        print(f"Failed to connect to Brain: {e}")
        return []

async def query_pinecone(vector: list, top_k: int = 12) -> list[str]:
    """Queries Pinecone for the most similar image IDs."""
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX)
        
        query_response = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        # Extract IDs (which are our ImageRecord IDs as strings)
        return [match['id'] for match in query_response['matches']]
    except Exception as e:
        print(f"Pinecone Search Error: {e}")
        return []

async def upsert_to_pinecone(image_id: str, vector: list, metadata: dict):
    """Saves the vector to Pinecone for semantic search."""
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX)
        
        index.upsert(vectors=[(image_id, vector, metadata)])
    except Exception as e:
        print(f"Pinecone Error: {e}")
