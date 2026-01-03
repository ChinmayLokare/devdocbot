import os
import time
import uuid
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Sample "Documentation"
DOCS = [
    {"text": "To restart the application, run 'systemctl restart app'.", "category": "operations"},
    {"text": "The API rate limit is 100 requests per minute.", "category": "api"},
    {"text": "Use the 'main' branch for production deployments.", "category": "git"},
    {"text": "Database backups run automatically every night at 2 AM.", "category": "database"},
    {"text": "AWS Lambda functions have a 15-minute timeout limit.", "category": "aws"},
    {"text": "You can view logs in CloudWatch under the /aws/lambda log group.", "category": "aws"},
    {"text": "To install dependencies, run 'pip install -r requirements.txt'.", "category": "python"},
    {"text": "Environment variables are stored in the .env file.", "category": "config"},
    {"text": "The default port for the web server is 8080.", "category": "network"},
    {"text": "Contact the security team immediately if you detect a breach.", "category": "security"},
]


def ingest():
    # 1. Init Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=api_key)
    index = pc.Index("devdocbot-docs")

    # 2. Init Model
    print("⏳ Loading model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # 3. Prepare Batch
    vectors_to_upload = []

    print(f"🚀 Processing {len(DOCS)} documents...")

    for doc in DOCS:
        # Create Embedding
        vector = model.encode(doc['text']).tolist()

        # Create Metadata
        metadata = {
            "text": doc['text'],
            "category": doc['category'],
            "timestamp": time.time()
        }

        # Create Unique ID
        doc_id = str(uuid.uuid4())

        # Format for Pinecone: (id, vector, metadata)
        vectors_to_upload.append((doc_id, vector, metadata))

    # 4. Upload
    print("📤 Uploading to Pinecone...")
    index.upsert(vectors=vectors_to_upload)
    print("✅ Upload complete!")

    # 5. Verify & Test Search
    time.sleep(2)  # Give Pinecone a moment to index
    print("\n🔎 Testing Search: 'How do I view logs?'")

    query_vector = model.encode("How do I view logs?").tolist()

    results = index.query(
        vector=query_vector,
        top_k=2,
        include_metadata=True
    )

    for match in results['matches']:
        print(f"Score: {match['score']:.4f} | Text: {match['metadata']['text']}")


if __name__ == "__main__":
    ingest()