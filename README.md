# DevDocBot 🤖

> **AWS-native semantic search engine for technical documentation using RAG (Retrieval-Augmented Generation).**

![AWS](https://img.shields.io/badge/AWS-Serverless-orange)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple)
![Pinecone](https://img.shields.io/badge/VectorDB-Pinecone-green)
![Status](https://img.shields.io/badge/Status-Live-success)

**DevDocBot** acts as an intelligent layer over GitHub repositories. Instead of Ctrl+F keyword matching, it uses **Vector Embeddings** to understand the *meaning* of your query.

*Example: Searching for "how to scale" will find documents about "Horizontal Pod Autoscaler" even if the word "scale" isn't present.*

---

## 🏗️ Architecture

The system follows a **Serverless Event-Driven Architecture** to ensure zero idle costs and infinite scalability.

### Key Components
1.  **Ingestion Pipeline:** GitHub Webhooks → API Gateway → SQS Queue → Indexer Lambda.
2.  **Search Pipeline:** API Gateway → Search Lambda → DynamoDB Cache → Vector Search.
3.  **AI/ML:** Hugging Face `all-MiniLM-L6-v2` (via BAAI) for embeddings.
4.  **Database:** Pinecone (Vectors) + DynamoDB (Metadata & Caching).

*(See [docs/architecture.md](docs/architecture.md) for detailed diagrams)*

---

## 🚀 Features

-   🔍 **Semantic Search:** Understands natural language queries.
-   ⚡ **Sub-100ms Latency:** Implements Read-Through Caching via DynamoDB.
-   🔄 **Auto-Sync:** Listens to GitHub `push` events to re-index documentation in real-time.
-   🛡️ **Resilience:** Uses Dead Letter Queues (DLQ) and SQS retries for fault tolerance.
-   📊 **Observability:** Custom CloudWatch Dashboard tracking Hit Rate, Latency, and Indexing Throughput.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Compute** | AWS Lambda | Python 3.11 serverless functions |
| **API** | API Gateway | REST API with throttling |
| **Queue** | Amazon SQS | Async processing buffer |
| **Cache** | DynamoDB | Key-Value store for search results |
| **Vector DB** | Pinecone | Storing 384-dimensional embeddings |
| **IaC** | Terraform | Infrastructure defined as code |
| **Monitoring** | CloudWatch | Custom metrics and alarms |

---

## 🔌 API Usage

**Base URL:** `[YOUR_API_GATEWAY_URL]`

### 1. Search
```bash
curl -X POST /search \
  -H "Content-Type: application/json" \
  -d '{"query": "deploy to kubernetes", "top_k": 3}'




## Infrastructure as Code (IaC)

This project currently uses a hybrid deployment strategy:
1.  **Core Services:** Deployed via AWS Console for rapid prototyping.
2.  **IaC Demo:** A Terraform configuration is included in `/infra` to demonstrate how the stack would be provisioned in an enterprise environment.

**Terraform Plan:**
The `/infra` directory contains a modular Terraform setup including:
*   `providers.tf`: AWS Provider configuration.
*   `main.tf`: Resource definitions (DynamoDB example included).
*   `variables.tf`: Reusable configuration.

To run the IaC demo:
```bash
cd infra
terraform init
terraform apply