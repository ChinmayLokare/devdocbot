import requests
import time
import random

API_URL = "https://9xlucsfpd9.execute-api.us-east-2.amazonaws.com/dev/search"

queries = ["kubernetes", "docker", "aws lambda", "python", "error", "missing doc"]

print("🚀 Generating traffic...")
for i in range(20):
    q = random.choice(queries)
    print(f"Search: {q}")
    try:
        requests.post(API_URL, json={"query": q, "top_k": 2})
    except:
        pass
    time.sleep(0.5)

print("✅ Done.")