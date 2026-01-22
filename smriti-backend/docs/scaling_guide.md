# Smriti Backend - Scaling Guide

## Current Setup (5 Users)

**Infrastructure:**
- Render.com Free Tier (512MB RAM, 0.1 CPU)
- MongoDB Atlas M0 Free Tier (512MB storage)
- Cloudinary Free Tier (25GB storage, 25GB bandwidth)

**This works perfectly for:** 5-50 users

---

## Scaling Roadmap

### Phase 1: 50-500 Users (Low Cost)

#### 1. Upgrade Render Instance
**Current:** Free tier (sleeps after 15 min)
**Upgrade to:** Starter ($7/month)
- 512MB RAM, 0.5 CPU
- No sleep mode
- Better performance

#### 2. Upgrade MongoDB Atlas
**Current:** M0 Free (512MB)
**Upgrade to:** M2 Shared ($9/month)
- 2GB storage
- Better performance
- Automated backups

#### 3. Add Caching (Optional)
**Why:** Reduce database queries
**How:** Add Redis for caching frequently accessed data

```python
# Install redis
pip install redis

# Add to your code
import redis
from functools import wraps

redis_client = redis.Redis(
    host='your-redis-host',
    port=6379,
    decode_responses=True
)

def cache_posts(timeout=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(user_id, *args, **kwargs):
            cache_key = f"posts:{user_id}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(user_id, *args, **kwargs)
            redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator
```

**Cost:** Redis Cloud Free Tier (30MB) or Upstash ($10/month)

**Total Phase 1 Cost:** ~$16-26/month

---

### Phase 2: 500-5,000 Users (Medium Scale)

#### 1. Upgrade Render Instance
**Upgrade to:** Standard ($25/month)
- 2GB RAM, 1 CPU
- Handles concurrent requests better

#### 2. Upgrade MongoDB Atlas
**Upgrade to:** M10 Dedicated ($57/month)
- 10GB storage
- Dedicated resources
- Auto-scaling
- Point-in-time recovery

#### 3. Add CDN for Static Files
**Why:** Faster file delivery globally
**How:** Cloudinary already provides CDN
**Action:** Upgrade Cloudinary if needed ($89/month for Plus)

#### 4. Implement Database Indexing
```python
# Add indexes to frequently queried fields
async def create_indexes():
    db = await get_database()
    
    # Index on user_id for faster post queries
    await db.posts.create_index("user_id")
    
    # Index on created_at for sorting
    await db.posts.create_index([("created_at", -1)])
    
    # Compound index for user posts sorted by date
    await db.posts.create_index([
        ("user_id", 1),
        ("created_at", -1)
    ])
```

#### 5. Add Monitoring
**Tools:**
- Sentry (error tracking) - Free tier available
- New Relic or Datadog (performance monitoring)
- Render built-in metrics

**Total Phase 2 Cost:** ~$82-171/month

---

### Phase 3: 5,000-50,000 Users (High Scale)

#### 1. Horizontal Scaling
**Multiple Render Instances:**
- Deploy 2-3 instances behind a load balancer
- Render Pro ($85/month per instance)

#### 2. Database Optimization
**MongoDB Atlas M30** ($193/month)
- 40GB storage
- 4GB RAM
- Replica sets for high availability

**Add Read Replicas:**
- Separate read/write operations
- Read from replicas, write to primary

```python
# Separate read/write connections
class Database:
    write_client: AsyncIOMotorClient = None
    read_client: AsyncIOMotorClient = None
    
    def connect(self):
        # Write to primary
        self.write_client = AsyncIOMotorClient(
            settings.MONGODB_WRITE_URI
        )
        
        # Read from replica
        self.read_client = AsyncIOMotorClient(
            settings.MONGODB_READ_URI,
            readPreference='secondaryPreferred'
        )
```

#### 3. Implement Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/signup")
@limiter.limit("5/minute")  # 5 signups per minute per IP
async def signup(request: Request, user: UserCreate):
    # ... existing code
```

#### 4. Add Message Queue
**Why:** Handle background tasks (file processing, emails)
**How:** Use Celery + Redis

```python
# For async tasks like document processing
from celery import Celery

celery_app = Celery('smriti', broker='redis://localhost:6379')

@celery_app.task
def process_document(document_url):
    # Process document in background
    pass
```

#### 5. Database Sharding (If Needed)
**When:** 100GB+ data
**How:** Shard by user_id

**Total Phase 3 Cost:** ~$450-600/month

---

## Performance Optimizations

### 1. Database Query Optimization
```python
# Bad: N+1 query problem
posts = await db.posts.find({"user_id": user_id}).to_list(100)
for post in posts:
    author = await db.users.find_one({"_id": post["user_id"]})

# Good: Use aggregation
posts = await db.posts.aggregate([
    {"$match": {"user_id": user_id}},
    {"$lookup": {
        "from": "users",
        "localField": "user_id",
        "foreignField": "_id",
        "as": "author"
    }},
    {"$limit": 100}
]).to_list(100)
```

### 2. Pagination Optimization
```python
# Use cursor-based pagination for large datasets
@app.get("/api/posts/")
async def get_posts(
    cursor: Optional[str] = None,
    limit: int = Query(default=20, le=100)
):
    query = {}
    if cursor:
        # Decode cursor to get last post ID
        last_id = decode_cursor(cursor)
        query["_id"] = {"$gt": ObjectId(last_id)}
    
    posts = await db.posts.find(query).limit(limit).to_list(limit)
    next_cursor = encode_cursor(posts[-1]["_id"]) if posts else None
    
    return {"posts": posts, "next_cursor": next_cursor}
```

### 3. Connection Pooling
```python
# Already configured in Motor
client = AsyncIOMotorClient(
    settings.MONGODB_URI,
    maxPoolSize=50,  # Increase for high traffic
    minPoolSize=10
)
```

---

## Monitoring & Alerts

### Key Metrics to Track
1. **Response Time:** < 200ms for 95% of requests
2. **Error Rate:** < 1%
3. **Database Queries:** < 100ms average
4. **Memory Usage:** < 80% of available
5. **CPU Usage:** < 70% average

### Setup Alerts
```python
# Example: Sentry integration
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=0.1,  # 10% of transactions
    environment=settings.ENVIRONMENT
)
```

---

## Cost Breakdown by User Count

| Users | Render | MongoDB | Redis | CDN | Total/Month |
|-------|--------|---------|-------|-----|-------------|
| 5-50 | Free | Free | Free | Free | $0 |
| 50-500 | $7 | $9 | $10 | Free | $26 |
| 500-5K | $25 | $57 | $10 | $89 | $181 |
| 5K-50K | $255 | $193 | $30 | $89 | $567 |

---

## When to Scale What

### Immediate Actions (Now)
- ✅ Add database indexes
- ✅ Implement proper error logging
- ✅ Set up monitoring

### When You Hit 50 Users
- Upgrade to Render Starter
- Add Redis caching
- Upgrade MongoDB to M2

### When You Hit 500 Users
- Upgrade to Render Standard
- Upgrade MongoDB to M10
- Implement rate limiting
- Add CDN for static files

### When You Hit 5,000 Users
- Multiple Render instances
- MongoDB M30 with replicas
- Message queue for background tasks
- Consider microservices architecture

---

## Alternative: Serverless Architecture

For unpredictable traffic, consider serverless:

**AWS Lambda + API Gateway:**
- Pay per request
- Auto-scales infinitely
- No server management

**Cost:** ~$0.20 per 1M requests

**Migration Path:**
1. Containerize your app (already done with Docker!)
2. Deploy to AWS Lambda using AWS SAM or Serverless Framework
3. Use MongoDB Atlas (same as now)
4. Use S3 instead of Cloudinary for files

---

## Quick Wins (Do These Now)

### 1. Add Compression
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 2. Enable HTTP/2
Already enabled on Render by default ✅

### 3. Optimize Docker Image
```dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Summary

**Current (5 users):** $0/month - Perfect!

**Next milestone (50 users):** $26/month
- Upgrade Render + MongoDB
- Add Redis caching

**Growth path:** Scale incrementally based on actual usage

**Key principle:** Don't over-optimize early. Scale when you have real traffic, not anticipated traffic.

**Your current setup is production-ready for your initial users!** 🚀
