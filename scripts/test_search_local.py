import sys
import os
import json
import time
from dotenv import load_dotenv

# Setup path to import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.handlers.search import lambda_handler

# Load Env Vars (Pinecone Key)
load_dotenv()


def run_search_test(name, payload):
    print(f"\n🧪 TEST: {name}")
    print(f"   Input: {json.dumps(payload)}")

    # Invoke Handler
    response = lambda_handler(payload, None)

    # Parse Response
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        perf = body['performance']
        print(f"   ✅ Status: 200 OK")
        print(
            f"   ⏱️ Time: {perf['total_time_ms']}ms (Embed: {perf['embed_time_ms']}ms | Pinecone: {perf['search_time_ms']}ms)")
        print(f"   📂 Results found: {body['count']}")

        print("   --- Top Matches ---")
        for i, res in enumerate(body['results']):
            # Truncate text for display
            text_preview = res['text'][:80] + "..." if len(res['text']) > 80 else res['text']
            print(f"   {i + 1}. Score: {res['score']:.4f} | {text_preview}")
            print(f"      Category: {res['metadata'].get('category')}")
    else:
        print(f"   ❌ Error {response['statusCode']}: {response['body']}")


def main():
    # 1. Test Cold Start (First run loads the model)
    run_search_test("Cold Start - Deployment Query", {
        "query": "How do I deploy to Kubernetes?",
        "top_k": 2
    })

    # 2. Test Warm Start (Model already in memory)
    run_search_test("Warm Start - Logs Query", {
        "query": "Where can I find the application logs?",
        "top_k": 2
    })

    # 3. Test Semantic Matching (Different words, same meaning)
    # Day 2 data had: "The API rate limit is 100 requests per minute."
    run_search_test("Semantic Match - Rate Limiting", {
        "query": "What is the max number of API calls allowed?",
        "top_k": 1
    })

    # 4. Test Metadata Filtering
    # Only search within 'database' category
    run_search_test("Filtered Search (Database only)", {
        "query": "backups",
        "top_k": 5,
        "filter": {"category": "database"}
    })

    # 5. Test Filter with No Results (Logic check)
    run_search_test("Filtered Search (Non-existent category)", {
        "query": "backups",
        "filter": {"category": "space_travel"}
    })


if __name__ == "__main__":
    main()