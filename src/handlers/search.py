import json
import time
import os
import logging
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- GLOBAL SCOPE (Caching for Warm Starts) ---
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
INDEX_NAME = 'devdocbot-docs'

# Variables to hold cached resources
model = None
pc_index = None


def load_resources():
    """Lazy load model and database connection."""
    global model, pc_index

    # 1. Load Model
    if model is None:
        logger.info(f"🥶 COLD START: Loading model {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)

    # 2. Connect to Pinecone
    if pc_index is None:
        logger.info("Connecting to Pinecone...")
        api_key = os.environ.get("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not set in environment")

        pc = Pinecone(api_key=api_key)
        pc_index = pc.Index(INDEX_NAME)

    return model, pc_index


def lambda_handler(event, context):
    """
    Search Handler
    Input: { "query": "text", "top_k": 5, "filter": { "category": "aws" } }
    """
    total_start = time.time()

    try:
        # --- 1. Parse Input ---
        if 'body' in event and isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event

        query_text = body.get('query')
        top_k = int(body.get('top_k', 3))  # Ensure int
        metadata_filter = body.get('filter')

        print(f"🔹 Incoming Request: Query='{query_text}' | Top_K={top_k} | Filter={metadata_filter}")

        if not query_text:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing "query" parameter'})
            }

        # --- 2. Load Resources ---
        embedder, index = load_resources()

        # --- 3. Generate Embedding ---
        embed_start = time.time()

        # Generate raw numpy array
        raw_embedding = embedder.encode(query_text)

        # Convert to strict Python list of floats (Fixes potential numpy serialization issues)
        query_vector = [float(x) for x in raw_embedding.tolist()]

        embed_time = (time.time() - embed_start) * 1000

        # Debug: Check vector health
        print(f"🔹 Vector Generated: Length={len(query_vector)} | Sample={query_vector[:3]}")

        # --- 4. Search Pinecone ---
        search_start = time.time()

        # Construct arguments dynamically to avoid passing filter=None
        query_args = {
            "vector": query_vector,
            "top_k": top_k,
            "include_metadata": True
        }

        if metadata_filter:
            query_args["filter"] = metadata_filter

        # Perform Query
        search_results = index.query(**query_args)

        search_time = (time.time() - search_start) * 1000

        # --- 5. Format Results ---
        matches = []
        for match in search_results['matches']:
            matches.append({
                "id": match['id'],
                "score": float(match['score']),
                "text": match['metadata'].get('text', ''),
                "metadata": match['metadata']
            })

        total_time = (time.time() - total_start) * 1000

        response = {
            "query": query_text,
            "results": matches,
            "count": len(matches),
            "performance": {
                "total_time_ms": int(total_time),
                "embed_time_ms": int(embed_time),
                "search_time_ms": int(search_time)
            }
        }

        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace to console
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }