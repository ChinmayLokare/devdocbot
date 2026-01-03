import json
import os
import time
import hashlib
import requests
import boto3
from pinecone import Pinecone
from decimal import Decimal
from datetime import datetime, timedelta
from metric_helper import put_metric, log_structured

# --- CONFIGURATION ---
HF_TOKEN = os.environ.get('HF_API_TOKEN')
HF_API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"

dynamodb = boto3.resource('dynamodb')
CACHE_TABLE_NAME = os.environ.get('CACHE_TABLE_NAME', 'devdocbot-search-cache')
cache_table = dynamodb.Table(CACHE_TABLE_NAME)

pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
index = pc.Index(os.environ.get('PINECONE_INDEX', 'devdocbot-docs'))


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal): return float(o)
        return super(DecimalEncoder, self).default(o)


# --- HELPER FUNCTIONS ---
def get_query_hash(query):
    return hashlib.md5(query.lower().strip().encode()).hexdigest()


def to_decimal(obj):
    """Convert floats to Decimal for DynamoDB"""
    if isinstance(obj, float): return Decimal(str(obj))
    if isinstance(obj, dict): return {k: to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list): return [to_decimal(x) for x in obj]
    return obj


def get_embedding(text):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(HF_API_URL, headers=headers, json={"inputs": text})
    return response.json()


# --- MAIN HANDLER ---
def lambda_handler(event, context):
    start_time = time.time()
    query = "unknown"
    cache_hit = False  # Default to False
    results = []

    try:
        # 1. Parse Input
        body = event.get('body', '{}')
        if isinstance(body, str): body = json.loads(body)
        query = body.get('query', '')
        top_k = int(body.get('top_k', 3))

        log_structured('search_started', {'query': query})

        if not query: 
            return {
                'statusCode': 400, 
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': 'Query required'
            }

        # 2. Check Cache
        query_hash = get_query_hash(query)
        try:
            cached = cache_table.get_item(Key={'query_hash': query_hash})
            if 'Item' in cached:
                item = cached['Item']
                # Check TTL
                if item.get('ttl', 0) > int(time.time()):
                    results = item.get('results')
                    cache_hit = True
                    log_structured('cache_hit', {'query': query})
        except Exception as e:
            print(f"Cache Read Error: {e}")

        # 3. If Miss: Generate Embedding & Search
        if not cache_hit:
            query_vector = get_embedding(query)

            # Handle HF Loading Error
            if isinstance(query_vector, dict) and 'error' in query_vector:
                return {'statusCode': 503, 'body': json.dumps({'error': 'AI Model loading...'})}

            # Search Pinecone
            search_res = index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True
            )

            # Format Results
            for m in search_res['matches']:
                results.append({
                    'score': float(m['score']),
                    'text': m['metadata'].get('text', ''),
                    'title': m['metadata'].get('title', 'Untitled'),
                    'url': m['metadata'].get('url', '')
                })

            # Save to Cache (Async-ish)
            try:
                ttl = int((datetime.now() + timedelta(hours=1)).timestamp())
                cache_table.put_item(
                    Item={
                        'query_hash': query_hash,
                        'query': query,
                        'results': to_decimal(results),  # Convert floats for Dynamo
                        'ttl': ttl,
                        'cached_at': int(time.time())
                    }
                )
            except Exception as e:
                print(f"Cache Write Error: {e}")

        # 4. Metrics & Logging
        duration = (time.time() - start_time) * 1000
        put_metric('SearchLatency', duration, 'Milliseconds')
        put_metric('SearchCount', 1, 'Count')
        put_metric('CacheHitRate', 100 if cache_hit else 0, 'Percent')

        if not results:
            put_metric('ZeroResults', 1, 'Count')
        else:
            # Safe access to score (results[0] might be Decimal from cache or float from Pinecone)
            top_score = float(results[0]['score'])
            put_metric('RelevanceScore', top_score)

        log_structured('search_completed', {
            'query': query,
            'duration_ms': duration,
            'result_count': len(results),
            'cache_hit': cache_hit
        })

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization'
            },
            'body': json.dumps({'query': query, 'results': results}, cls=DecimalEncoder)
        }

    except Exception as e:
        log_structured('search_error', {'error': str(e)}, 'ERROR')
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}