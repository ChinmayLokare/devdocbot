# System Architecture

This document outlines the high-level infrastructure and data flow for **DevDocBot**.

---

## 1. High-Level Infrastructure
This flowchart illustrates the component relationship and boundaries between AWS, External AI services, and Users.

```mermaid
graph TD
    User[User/Developer]
    GH[GitHub Repo]
    
    subgraph "AWS Cloud (Serverless)"
        API[API Gateway]
        
        
        subgraph "Search Service"
            SL[Search Lambda]
            DDB_Cache[(DynamoDB Cache)]
        end
        
        subgraph "Ingestion Service"
            WL[Webhook Lambda]
            SQS[SQS Queue]
            IL[Indexer Lambda]
            DDB_Docs[(DynamoDB Metadata)]
        end
        
        CW[CloudWatch Monitoring]
    end
    
    subgraph "External AI & Data"
        HF[Hugging Face API]
        PC[(Pinecone Vector DB)]
    end

    %% -- Search Flow --
    User -->|POST /search| API
    API -->|Proxy| SL
    SL -->|Read/Write| DDB_Cache
    SL -->|Generate Embedding| HF
    SL -->|Semantic Search| PC
    
    %% -- Indexing Flow --
    GH -->|Git Push| API
    API -->|Webhook| WL
    WL -->|Enqueue| SQS
    SQS -->|Batch Trigger| IL
    IL -->|Generate Embedding| HF
    IL -->|Upsert Vector| PC
    IL -->|Update Status| DDB_Docs
    
    %% -- Monitoring --
    SL -.->|Metrics| CW
    IL -.->|Metrics| CW

```

## 2. Search Request Sequence
This diagram details the logic flow when a user performs a search, including the "Read-Through Caching" strategy.

```mermaid

sequenceDiagram
    participant U as User
    participant API as API Gateway
    participant L as Search Lambda
    participant C as DynamoDB Cache
    participant AI as Hugging Face (Embeddings)
    participant V as Pinecone (Vector DB)
    
    U->>API: POST /search {"query": "kubernetes"}
    API->>L: Invoke Lambda
    L->>C: Check Cache (MD5 of query)
    
    alt Cache Hit (TTL Valid)
        C-->>L: Return Cached JSON
        L-->>API: Return Results
        API-->>U: 200 OK (Latency: <50ms)
    else Cache Miss
        C-->>L: null
        Note over L,AI: Real-time Semantic Search
        L->>AI: Generate Embedding for "kubernetes"
        AI-->>L: Vector [0.12, -0.45, ...]
        L->>V: Query(Vector, Top_K=5)
        V-->>L: Return Matching Doc IDs & Scores
        L->>C: Save Results (TTL 1hr)
        L-->>API: Return Results
        API-->>U: 200 OK (Latency: ~300ms)
    end
```