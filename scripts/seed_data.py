import requests
import time
import json

# ---------------- CONFIGURATION ----------------
API_URL = "https://9xlucsfpd9.execute-api.us-east-2.amazonaws.com/dev/documents"
# -----------------------------------------------
all_docs = []

# ==========================================
# 1. INTERNAL API: Order Management System (OMS)
#    Team: Checkout Squad
#    Lead Dev: Sarah Chen
# ==========================================
oms_docs = [
    {
        "title": "OMS API: Overview and Ownership",
        "text": """
        The Order Management System (OMS) API manages the lifecycle of customer orders from placement to fulfillment.
        
        **Team Responsible:** Checkout Squad (Slack: #team-checkout)
        **Tech Lead:** Sarah Chen (sarah.chen@company.internal)
        **On-Call:** PagerDuty Service 'OMS-Critical'
        
        Base URL: https://api.internal.company.com/oms/v2
        Authentication: Requires 'Internal-Service-Key' header.
        """,
        "source": "confluence",
        "url": "https://wiki.company.internal/oms/overview"
    },
    {
        "title": "OMS API: Fetching Orders",
        "text": """
        To retrieve order details, use the GET /orders endpoint.
        
        **Endpoint:** GET /v2/orders/{order_id}
        **Developer Contact:** Mike Ross (migration to v2)
        
        Parameters:
        - order_id: The UUID of the order.
        - include_items: (bool) Whether to hydrate line items.
        
        Example:
        GET /v2/orders/123-abc?include_items=true
        
        Note: Orders older than 3 years are moved to Cold Storage (S3).
        """,
        "source": "confluence",
        "url": "https://wiki.company.internal/oms/get-orders"
    },
    {
        "title": "OMS API: Creating Orders",
        "text": """
        Creating orders requires strict idempotency keys to prevent duplicate charges.
        
        **Endpoint:** POST /v2/orders
        **Required Header:** X-Idempotency-Key
        
        Validation:
        - SKU must exist in Product Catalog.
        - User must have active status.
        
        If the Product Catalog API is down, this endpoint will return 503 Service Unavailable.
        """,
        "source": "confluence",
        "url": "https://wiki.company.internal/oms/create-orders"
    },
    {
        "title": "OMS Architecture Diagram & Dependencies",
        "text": """
        The OMS service depends on the following internal services:
        1. **Product Catalog Service** (for SKU validation)
        2. **User Profile Service** (for shipping addresses)
        3. **Payment Gateway** (Stripe wrapper)
        
        Database: Aurora PostgreSQL (Primary), DynamoDB (Order History).
        Developed by the Checkout Squad.
        """,
        "source": "confluence",
        "url": "https://wiki.company.internal/oms/architecture"
    },
    {
        "title": "OMS: Troubleshooting 409 Errors",
        "text": """
        If you receive a 409 Conflict error from the OMS API, it usually means an Idempotency Key collision.
        
        **Resolution:**
        1. Check if the order was already created using the same key.
        2. Generate a new UUID for the X-Idempotency-Key header.
        
        Contact Alex Smith (alex.smith@company.internal) if this persists during high load events like Black Friday.
        """,
        "source": "runbook",
        "url": "https://wiki.company.internal/oms/troubleshooting"
    }
]

# ==========================================
# 2. INTERNAL API: Product Catalog
#    Team: Catalog Team
#    Lead Dev: David Kim
# ==========================================
catalog_docs = [
    {
        "title": "Product Catalog API: Getting Started",
        "text": """
        The Product Catalog API is the single source of truth for all item metadata, pricing, and stock levels.
        
        **Team Responsible:** Catalog Team (Slack: #team-catalog)
        **Lead Developer:** David Kim
        
        We use GraphQL for this service.
        Endpoint: https://api.internal.company.com/catalog/graphql
        """,
        "source": "confluence",
        "url": "https://wiki.company.internal/catalog/overview"
    },
    {
        "title": "Product Catalog: Fetching Products",
        "text": """
        To fetch products, use the 'product' query in GraphQL.
        
        Query Example:
        query {
          product(id: "sku-123") {
            name
            price {
              amount
              currency
            }
            inventory_level
          }
        }
        
        Do NOT use the legacy REST API (/v1/products) as it is deprecated since Q3 2024.
        """,
        "source": "confluence",
        "url": "https://wiki.company.internal/catalog/fetching"
    },
    {
        "title": "Product Catalog: Bulk Updates",
        "text": """
        For updating inventory levels in bulk (e.g., receiving a shipment), use the 'bulkInventoryUpdate' mutation.
        
        Limit: 500 items per request.
        
        This process is asynchronous. The mutation returns a Job ID. You must poll the Job Status API to check completion.
        Developed by: Jessica Lee.
        """,
        "source": "confluence",
        "url": "https://wiki.company.internal/catalog/bulk-updates"
    },
    {
        "title": "Product Catalog: Caching Strategy",
        "text": """
        Product data is heavily cached in Redis.
        
        TTL Settings:
        - Pricing: 15 minutes
        - Description/Images: 24 hours
        - Inventory: 0 (Real-time, no cache)
        
        If you see stale prices, purge the Redis cache using the internal admin tool.
        """,
        "source": "confluence",
        "url": "https://wiki.company.internal/catalog/caching"
    },
    {
        "title": "Product Catalog: Event Stream",
        "text": """
        When a product is created or modified, an event is emitted to the 'catalog-events' Kafka topic.
        
        Event Schema:
        {
          "event_type": "PRODUCT_UPDATED",
          "sku": "123",
          "changes": ["price", "stock"],
          "timestamp": "2024-01-01T12:00:00Z"
        }
        
        Subscribe to this topic if you need real-time updates for Search Indexing.
        """,
        "source": "confluence",
        "url": "https://wiki.company.internal/catalog/events"
    }
]

# ==========================================
# 3. KUBERNETES (Infrastructure)
# ==========================================
k8s_docs = [
    {
        "title": "K8s: Deployment Best Practices",
        "text": """
        Always define resource requests and limits for your Pods.
        
        Example:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
            
        Without limits, a memory leak in one pod can crash the specific node it is running on.
        """,
        "source": "manual",
        "url": "https://k8s.docs/deployments"
    },
    {
        "title": "K8s: Troubleshooting CrashLoopBackOff",
        "text": """
        CrashLoopBackOff means the pod starts, crashes, and K8s tries to restart it repeatedly.
        
        Steps to debug:
        1. Check logs: 'kubectl logs [pod-name] --previous'
        2. Check events: 'kubectl describe pod [pod-name]'
        3. Verify liveness probes are not failing too quickly.
        4. Check for missing environment variables or secrets.
        """,
        "source": "runbook",
        "url": "https://k8s.docs/troubleshooting"
    },
    {
        "title": "K8s: Horizontal Pod Autoscaler (HPA)",
        "text": """
        HPA automatically scales the number of Pods based on observed CPU utilization.
        
        Command:
        kubectl autoscale deployment my-app --cpu-percent=50 --min=1 --max=10
        
        Note: You must have metrics-server installed in the cluster for HPA to work.
        """,
        "source": "manual",
        "url": "https://k8s.docs/hpa"
    },
    {
        "title": "K8s: Secrets Management (External Secrets)",
        "text": """
        We do NOT store secrets in Git or plain YAML files.
        We use the 'External Secrets Operator' to sync secrets from AWS Secrets Manager into Kubernetes.
        
        To add a secret:
        1. Add value to AWS Secrets Manager.
        2. Create a 'SecretStore' reference in your helm chart.
        """,
        "source": "manual",
        "url": "https://k8s.docs/secrets"
    },
    {
        "title": "K8s: Ingress Controllers",
        "text": """
        Ingress exposes HTTP and HTTPS routes from outside the cluster to services within the cluster.
        We use NGINX Ingress Controller.
        
        Annotations are required for SSL redirection:
        nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
        """,
        "source": "manual",
        "url": "https://k8s.docs/ingress"
    }
]

# ==========================================
# 4. PYTHON BEST PRACTICES
# ==========================================
python_docs = [
    {
        "title": "Python: Type Hinting Standards",
        "text": """
        All new Python code must use Type Hints (PEP 484).
        
        Correct:
        def calculate_total(price: float, tax: float) -> float:
            return price + tax
            
        Incorrect:
        def calculate_total(price, tax):
            return price + tax
            
        We use 'mypy' in our CI/CD pipeline to enforce this.
        """,
        "source": "guidelines",
        "url": "https://python.internal/standards"
    },
    {
        "title": "Python: Dependency Management with Poetry",
        "text": """
        We use Poetry instead of pip/requirements.txt for all new projects.
        
        Commands:
        - poetry init (Create new project)
        - poetry add requests (Add dependency)
        - poetry run python main.py (Run script)
        
        This ensures deterministic builds via the poetry.lock file.
        """,
        "source": "guidelines",
        "url": "https://python.internal/poetry"
    },
    {
        "title": "Python: Asynchronous Programming (AsyncIO)",
        "text": """
        For I/O bound tasks (calling APIs, DBs), use 'async' and 'await'.
        
        Do not use 'requests' library in async functions as it is blocking. Use 'aiohttp' or 'httpx'.
        
        Example:
        async with httpx.AsyncClient() as client:
            resp = await client.get('https://api.com')
        """,
        "source": "guidelines",
        "url": "https://python.internal/async"
    },
    {
        "title": "Python: Logging Standards",
        "text": """
        Do not use 'print()'. Use the standard 'logging' module.
        In production, logs must be JSON formatted for CloudWatch ingestion.
        
        Use the internal wrapper:
        from shared.logger import logger
        logger.info("Order created", extra={"order_id": 123})
        """,
        "source": "guidelines",
        "url": "https://python.internal/logging"
    },
    {
        "title": "Python: Testing with Pytest",
        "text": """
        All PRs must have 80% code coverage.
        Use 'pytest' fixtures for setup/teardown.
        
        Mock external services using 'unittest.mock' or 'pytest-mock'. Never call real production APIs during unit tests.
        """,
        "source": "guidelines",
        "url": "https://python.internal/testing"
    }
]

# Combine all lists
all_docs = oms_docs + catalog_docs + k8s_docs + python_docs

print(f"🚀 Preparing to ingest {len(all_docs)} documents...")

for i, doc in enumerate(all_docs):
    print(f"[{i+1}/{len(all_docs)}] Sending: {doc['title']}")
    try:
        response = requests.post(
            API_URL,
            json={"documents": [doc]},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            print(f"   ❌ Failed: {response.text}")
        else:
            print(f"   ✅ OK")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Sleep to be nice to the rate limits
    time.sleep(1.5)

print("\n✨ Ingestion Complete! Search index will update shortly.")