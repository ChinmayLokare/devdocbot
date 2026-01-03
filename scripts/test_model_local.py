import time
from sentence_transformers import SentenceTransformer

def test_model():
    print("Loading model...")
    start_load = time.time()

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print(f"✅ Model loaded in {time.time() - start_load:.2f}s")

    sentences = [
        "Hello, world!",
        "How do I deploy to AWS Lambda?",
        "Docker containers are useful",
        "The quick brown fox jumps over the lazy dog.",
        "Python is a great language."
    ]

    print(f"⏳ Generating embeddings for {len(sentences)} sentences...")
    start_embed = time.time()
    embeddings = model.encode(sentences)
    duration = time.time() - start_embed

    # Validation
    dims = len(embeddings[0])
    print(f"✅ Generated in {duration:.2f}s")
    print(f"📏 Dimension check: {dims} (Expected: 384)")

    if dims == 384:
        print("✅ Dimensions match Pinecone index!")
    else:
        print("❌ CRITICAL: Dimensions do not match!")

    print(f"\nExample Vector (First 5 values of 'Hello, world!'):")
    print(embeddings[0][:5])


if __name__ == "__main__":
    test_model()

