import json
import uuid
import hashlib
import time
import os
import boto3

# -- Configuration --
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

TABLE_NAME = os.environ.get('DOCUMENTS_TABLE_NAME', 'devdocbot-documents')
QUEUE_URL = os.environ.get('SQS_QUEUE_URL')
docs_table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # 1. Parse Input
        body = event.get('body','{}')
        if isinstance(body, str):
            body = json.loads(body)
        documents = body.get('documents',[])

        if not documents:
            return {'statusCode': 400, 'body': 'No documents provided'}

        queued_count = 0

        for doc in documents:
            title = doc.get('title')
            text = doc.get('text')

            if not title or not text:
                print(f"Skipping invalid doc: {doc}")
                continue

            # Generate IDs

            doc_id = str(uuid.uuid4())
            content_hash = hashlib.md5(text.encode()).hexdigest()

            # 2. Save Metadata to DynamoDB (Status:Pending)
            docs_table.put_item(
                Item={
                    'doc_id': doc_id,
                    'version': 1,
                    'title': title,
                    'status':'pending',
                    'content_hash': content_hash,
                    'queued_at': int(time.time()),
                    'source':doc.get('source','manual'),
                    'url':doc.get('url',''),
                }
            )

            # 3. Send to SQS

            message = {
                'doc_id': doc_id,
                'title': title,
                'text': text,
                'source': doc.get('source', 'manual'),
                'url': doc.get('url', '')
            }

            sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps(message)
            )
            queued_count += 1

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({
                'message': f'{queued_count} documents queued for indexing',
                'doc_ids': [doc_id]  # Just returning last one for simplicity
            })
        }
    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}