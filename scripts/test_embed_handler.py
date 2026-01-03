import sys
import os
import json

# Add 'src' to python path so we can import the handler
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.handlers.embed import lambda_handler


def run_tests():
    test_cases = [
        {"name": "Simple Text", "input": {"text": "How do I deploy a Docker container?"}},
        {"name": "Empty Text", "input": {"text": ""}},
        {"name": "Wrong Type", "input": {"text": 123}},
    ]

    for test in test_cases:
        print(f"\n🧪 Testing: {test['name']}")

        # Simulate Lambda Context (Mock)
        response = lambda_handler(test['input'], None)

        status = response['statusCode']
        body = json.loads(response['body'])

        print(f"Status: {status}")
        if status == 200:
            print(f"✅ Success! Generated {len(body['embedding'])} dim vector.")
            print(f"⏱️ Time: {body['execution_time_ms']}ms")
        else:
            print(f"⚠️ Expected Error: {body.get('error')}")


if __name__ == "__main__":
    run_tests()