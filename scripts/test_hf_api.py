import requests
import os
import time


HF_TOKEN = os.environ.get("HF_API_TOKEN", "hf_PLACEHOLDER_TOKEN_FOR_TESTING")

API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def query(payload):
    response = requests.post(API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"⚠️ Status Code: {response.status_code}")
        print(f"⚠️ Raw Response: {response.text}")
    return response.json()

print("⏳ Sending request to Hugging Face...")
start = time.time()

output = query({
    "inputs": ["This is a test sentence.", "This is another sentence."],
    "options": {"wait_for_model": True}
})

print(f"✅ Response received in {time.time() - start:.2f}s")

if isinstance(output, list) and len(output) > 0 and isinstance(output[0], list):
    print(f"📏 Vector Dimensions: {len(output[0])}")
    print(f"🔢 First 5 values: {output[0][:5]}")
elif 'error' in output:
    print(f"❌ Error: {output['error']}")
    print("   (If model is loading, wait 20s and try again)")
else:
    print(f"⚠️ Unexpected output: {output}")