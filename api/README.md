# AI MongoDB Tool API

FastAPI-based REST API for generic MongoDB read/write operations plus a legacy conversation route set.

## Features

- ✅ Generic MongoDB operations: find, insert, update, delete, aggregate
- ✅ List MongoDB collections
- ✅ Health check endpoints
- ✅ MongoDB connection management
- ✅ Swagger/OpenAPI documentation
- ✅ CORS support

## Project Structure

```
api/
├── app/
│   ├── db/
│   │   └── mongodb.py          # MongoDB connection manager
│   ├── models/
│   │   ├── chat.py             # Chat models (Conversation, Message)
│   ├── routes/
│   │   ├── conversations.py    # Chat-specific conversation endpoints
│   │   ├── health.py           # Health check endpoints
│   │   └── mongodb_tool.py     # Generic MongoDB tool endpoints
│   ├── config.py               # Configuration
│   └── main.py                 # FastAPI app
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Setup

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your MongoDB URI:

```bash
copy .env.example .env
```

Edit `.env`:

```text
MONGODB_URI=mongodb+srv://your_username:your_password@your_cluster.mongodb.net
MONGODB_DB_NAME=ai_chat_db
SECRET_KEY=your-super-secret-key
```

### 3. Run the API

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### Health Check
- `GET /health` - API health status
- `GET /health/db` - Database connection status

### Generic MongoDB Tool
- `GET /mongo/collections` - List collections in the configured database
- `POST /mongo/find` - Find documents
- `POST /mongo/insert` - Insert a document
- `POST /mongo/update` - Update document(s)
- `POST /mongo/delete` - Delete document(s)
- `POST /mongo/aggregate` - Run an aggregation pipeline

### Legacy Chat Routes
- `POST /conversations` - Create new conversation
- `GET /conversations` - List user's conversations
- `GET /conversations/{id}` - Get conversation details
- `PUT /conversations/{id}` - Update conversation
- `DELETE /conversations/{id}` - Delete conversation
- `POST /conversations/{id}/messages` - Add message to conversation
- `GET /conversations/{id}/messages` - Get all messages

## Example Usage

### List collections

```bash
curl http://localhost:8000/mongo/collections
```

### Find documents

```bash
curl -X POST http://localhost:8000/mongo/find \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "my_collection",
    "filter": {"status": "active"},
    "limit": 20
  }'
```

### Insert a document

```bash
curl -X POST http://localhost:8000/mongo/insert \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "my_collection",
    "document": {"name": "Alice", "role": "admin"}
  }'
```

### Update documents

```bash
curl -X POST http://localhost:8000/mongo/update \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "my_collection",
    "filter": {"role": "admin"},
    "update": {"$set": {"active": true}},
    "many": true
  }'
```

### Delete documents

```bash
curl -X POST http://localhost:8000/mongo/delete \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "my_collection",
    "filter": {"role": "admin"},
    "many": false
  }'
```

### Aggregate

```bash
curl -X POST http://localhost:8000/mongo/aggregate \
  -H "Content-Type: application/json" \
  -d '{
    "collection": "my_collection",
    "pipeline": [
      {"$match": {"active": true}},
      {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ]
  }'
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
```

### Linting

```bash
pylint app/
```

## Deployment

### Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t mongo-tool-api .
docker run -p 8000:8000 --env-file .env mongo-tool-api
```

## Environment Variables

Required:
- `MONGODB_URI` - MongoDB connection string
- `SECRET_KEY` - Secret key for tokens or app secrets

Optional:
- `MONGODB_DB_NAME` - Database name (default: ai_chat_db)
- `DEBUG` - Enable debug mode (default: False)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry (default: 30)

## License

MIT
