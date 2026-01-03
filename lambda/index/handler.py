import json
import os
import time
import random
import boto3
import requests
from pinecone import Pinecone
from metrics_helper import put_metric, log_structured

# --- CONFIGURATION ---
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DOCUMENTS_TABLE_NAME', 'devdocbot-documents')
docs_table = dynamodb.Table(TABLE_NAME)


HF_TOKEN = os.environ.get('HF_API_TOKEN')
HF_API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
index = pc.Index(os.environ.get('PINECONE_INDEX', 'devdocbot-docs'))


def get_embeddings(texts):
    """Call Hugging Face API to get embeddings"""

    headers = {'Authorization': f'Bearer {HF_TOKEN}'}

    # BAAI model expects "inputs" as a list of strings
    payload = {
        "inputs": texts,
        "options": {"wait_for_model": True}
    }

    for attempt in range(3):
        try:
            response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=20)

            if response.status_code != 200:
                print(f"HF Error {response.status_code}: {response.text}")
                # If loading, wait
                if "loading" in response.text.lower():
                    time.sleep(10)
                    continue
                # If other error, break and retry
                time.sleep(2)
                continue

            result = response.json()
            return result

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    raise Exception("Failed to get embeddings from Hugging Face")

def lambda_handler(event, context):
    """
    Triggered by SQS Batch
    :param event:
    :param context:
    :return:
    """
    records = event['Records']
    start_time = time.time()
    try:
        # 1. Prepare batch
        texts_to_embed = []
        metadata_list = []

        for record in records:
            body = json.loads(record['body'])

            # Truncate to 1000 chars to be safe with API limits
            texts_to_embed.append(body['text'][:1000])
            metadata_list.append(body)

        print(f"Generating embeddings for {len(texts_to_embed)} docs...")

        # 2. Call API
        try:
            embeddings = get_embeddings(texts_to_embed)
        except Exception as e:
            print(f"Critical Embedding Error: {e}")
            raise e

        # 3. Upload to Pinecone
        vectors_to_upsert = []

        for i,meta in enumerate(metadata_list):

            if i>= len(embeddings):break

            doc_id = meta['doc_id']
            pinecone_id = f"doc-{doc_id}"

            vectors_to_upsert.append({
                'id': pinecone_id,
                'values': embeddings[i],  # The 384 floats
                'metadata': {
                    'title': meta['title'],
                    'text': meta['text'][:1000],
                    'url': meta.get('url', ''),
                    'source': meta.get('source', 'manual')
                }
            })

            # 4. Update DynamoDB
            docs_table.update_item(
                Key={'doc_id': doc_id, 'version': 1},
                UpdateExpression='SET #status = :s, embedding_id = :e, indexed_at = :t',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':s': 'indexed',
                    ':e': pinecone_id,
                    ':t': int(time.time())
                }
            )

        if vectors_to_upsert:
            index.upsert(vectors=vectors_to_upsert)
            print(f"Successfully indexed {len(vectors_to_upsert)} documents.")

        count = len(records)
        duration = (time.time() - start_time) * 1000

        put_metric('DocumentsIndexed', count, 'Count')
        put_metric('IndexingLatency', duration, 'Milliseconds')

        log_structured('indexing_success', {'count': count, 'duration_ms': duration})

        return {'status': 'success'}
    except Exception as e:
        log_structured('indexing_error', {'error': str(e)}, 'ERROR')
        put_metric('IndexingFailures', 1, 'Count')
        raise e
