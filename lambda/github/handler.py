import base64
import json
import os
import boto3
import requests
from base64 import b64decode
import hashlib
import hmac

# -- Configuration ---

sqs = boto3.client('sqs')
QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

def fetch_github_file(repo, branch, file_path):
    """Fetch file content from Github API"""
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={branch}"

    headers = {'Accept':'application/vnd.github.v3+json'}
    token = os.environ.get('GITHUB_TOKEN')

    if token:
        headers['Authorization'] = f"token {token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return base64.b64decode(data['content']).decode('utf-8')
        print(f"Failed to fetch {file_path}: {response.status_code}")
        return None
    except Exception as e:
        print(f"Failed to fetch {file_path}: {e}")
        return None

def lambda_handler(event, context):

    try:
        # 1. Parse Webhook
        body_str = event.get('body','{}')
        body = json.loads(body_str)
        headers = event.get('headers',{})

        # Normalize header keys (sometimes AWS passes lowercase)
        event_type = headers.get('X-GitHub-Event') or headers.get('x-github-event')

        # Handle ping
        if event_type == 'ping':
            return {'statusCode':200,'body':'pong'}

        if event_type != 'push':
            return {'statusCode': 200, 'body': 'Ignored non-push event'}

        # 2. Extract Info
        repo_name = body['repository']['full_name']
        repo_url = body['repository']['html_url']
        # "refs/heads/main" -> "main"
        branch = body['ref'].split('/')[-1]

        # 3. Find Changed Docs
        changed_files = []
        for commit in body.get('commits',[]):
            changed_files.extend(commit.get('added', []))
            changed_files.extend(commit.get('modified', []))

        doc_files = [
            f for f in changed_files
            if f.lower().endswith(('.md', '.txt', '.rst', '.markdown'))
        ]

        if not doc_files:
            return {'statusCode': 200, 'body': 'No documentation files changed'}

        # 4. Process Files
        processed = 0
        for file_path in doc_files:
            content = fetch_github_file(repo_name, branch, file_path)

            if content:
                # Construct Payload for SQS (Matches Upload Lambda format)
                message = {
                    'doc_id': f"gh-{repo_name}-{file_path}".replace('/', '-').replace('.', '-'),
                    'title': f"{repo_name}/{file_path}",
                    'text': content,
                    'source': 'github',
                    'url': f"{repo_url}/blob/{branch}/{file_path}",
                    'metadata': {
                        'repository': repo_name,
                        'branch': branch
                    }
                }

                sqs.send_message(
                    QueueUrl=QUEUE_URL,
                    MessageBody=json.dumps(message)
                )
                processed += 1
                print(f"Queued: {file_path}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Queued {processed} files'})
        }
    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}