import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ Error: PINECONE_API_KEY not found in .env")
        return

    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        
        index_name = "devdocbot-docs"
        
        # Check if index exists
        active_indexes = pc.list_indexes().names()
        if index_name in active_indexes:
            print(f"✅ Success! Connected to Pinecone. Index '{index_name}' exists.")
            
            # Connect to index and describe stats
            index = pc.Index(index_name)
            print(f"📊 Index Stats: {index.describe_index_stats()}")
        else:
            print(f"⚠️ Connected, but index '{index_name}' not found.")
            
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    test_connection()