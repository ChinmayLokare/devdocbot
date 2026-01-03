import json
import time
import os
import logging
from sentence_transformers import SentenceTransformer

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# GLOBAL SCOPE
# We load the model here so it stays cached between Lambda invocations (Warm Start)
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
model = None

def load_model():
    """Lazy load the model to handle cold starts gracefully."""
    global model
    if model is None:
        logger.info(f"Loading model {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)
        logger.info("Model loaded successfully.")
    return model


def lambda_handler(event, context):
    """
    AWS Lambda Handler
    Input: {"text": "string"}
    Output: {"embedding": [float], "dimension": int, ...}
    """
    start_time = time.time()

    try:
        # 1. Parse input
        if 'body' in event: #API gateway format
            body = json.loads(event['body'])
            text = body.get('text')
        else:
            text = event.get('text')


        if not text or not isinstance(text, str):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Input must contain a "text" string field'})
            }

        if len(text.strip())==0:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Text cannot be empty'})
            }

        # 2. Load Model & Generate Embedding
        embedder = load_model()

        # encode() returns a numpy array, we need a list for JSON serialization
        embedding = embedder.encode(text).tolist()

        execution_time = int((time.time() - start_time) * 1000)

        # 3. Return Response
        response = {
            "embedding": embedding,
            "dimension": len(embedding),
            "model": MODEL_NAME,
            "execution_time_ms": execution_time
        }

        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }

    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error processing embedding'})
        }
