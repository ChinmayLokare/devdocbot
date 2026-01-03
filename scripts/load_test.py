import requests
import time
import statistics
import random

# UPDATE WITH YOUR API GATEWAY URL
API_URL = "https://9xlucsfpd9.execute-api.us-east-2.amazonaws.com/dev/search"

queries = [
    "kubernetes deployment", "docker containers", "aws lambda python",
    "machine learning basics", "python recursion", "api gateway throttling",
    "how to center a div", "react hooks", "sql joins", "terraform state"
]

print(f"🚀 Starting Load Test on {API_URL}")
print("Sending 20 requests...")

latencies = []
hits = 0

for i in range(20):
    query = random.choice(queries)
    start = time.time()

    try:
        resp = requests.post(API_URL, json={"query": query, "top_k": 3})
        duration = (time.time() - start) * 1000
        latencies.append(duration)

        if resp.status_code == 200:
            data = resp.json()
            is_hit = data.get('results') and len(data['results']) > 0
            print(f"[{i + 1}/30] {query[:20].ljust(20)} | {duration:.0f}ms | Status: {resp.status_code}")
        else:
            print(f"[{i + 1}/30] ERROR: {resp.status_code}")

    except Exception as e:
        print(f"Request failed: {e}")

    time.sleep(0.5)

print("\n📊 --- LOAD TEST RESULTS ---")
print(f"Total Requests: {len(latencies)}")
print(f"Avg Latency:    {statistics.mean(latencies):.0f}ms")
print(f"P50 (Median):   {statistics.median(latencies):.0f}ms")
print(f"P95 Latency:    {sorted(latencies)[int(len(latencies) * 0.95)]:.0f}ms")
print(f"Min Latency:    {min(latencies):.0f}ms")
print(f"Max Latency:    {max(latencies):.0f}ms")