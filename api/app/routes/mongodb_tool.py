"""Generic MongoDB tool endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from app.db.mongodb import get_mongodb
from bson import ObjectId

router = APIRouter(prefix="/mongo", tags=["mongodb"])


class MongoFindRequest(BaseModel):
    collection: str = Field(..., description="MongoDB collection name")
    filter: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Query filter")
    projection: Optional[Dict[str, Any]] = Field(None, description="Projection document")
    limit: Optional[int] = Field(100, description="Maximum number of documents to return")
    skip: Optional[int] = Field(0, description="Number of documents to skip")


class MongoInsertRequest(BaseModel):
    collection: str = Field(..., description="MongoDB collection name")
    document: Dict[str, Any] = Field(..., description="Document to insert")


class MongoUpdateRequest(BaseModel):
    collection: str = Field(..., description="MongoDB collection name")
    filter: Dict[str, Any] = Field(..., description="Query filter for documents to update")
    update: Dict[str, Any] = Field(..., description="Update operations")
    many: Optional[bool] = Field(False, description="Update many documents")
    upsert: Optional[bool] = Field(False, description="Insert if no matching document is found")


class MongoDeleteRequest(BaseModel):
    collection: str = Field(..., description="MongoDB collection name")
    filter: Dict[str, Any] = Field(..., description="Query filter for documents to delete")
    many: Optional[bool] = Field(False, description="Delete many documents")


class MongoAggregateRequest(BaseModel):
    collection: str = Field(..., description="MongoDB collection name")
    pipeline: List[Dict[str, Any]] = Field(..., description="Aggregation pipeline")


def _serialize_value(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_value(v) for v in value]
    return value


def _serialize_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [_serialize_value(doc) for doc in documents]


@router.get("/collections")
async def list_collections(db = Depends(get_mongodb)):
    """List collections in the configured database"""
    try:
        return {"collections": db.list_collection_names()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find")
async def mongo_find(request: MongoFindRequest, db = Depends(get_mongodb)):
    """Find documents in a collection"""
    try:
        collection = db[request.collection]
        cursor = collection.find(request.filter, request.projection)
        documents = list(cursor.skip(request.skip).limit(request.limit))
        return {"documents": _serialize_documents(documents)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/insert", status_code=status.HTTP_201_CREATED)
async def mongo_insert(request: MongoInsertRequest, db = Depends(get_mongodb)):
    """Insert a document into a collection"""
    try:
        collection = db[request.collection]
        result = collection.insert_one(request.document)
        return {"inserted_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update")
async def mongo_update(request: MongoUpdateRequest, db = Depends(get_mongodb)):
    """Update documents in a collection"""
    try:
        collection = db[request.collection]
        if request.many:
            result = collection.update_many(request.filter, request.update, upsert=request.upsert)
        else:
            result = collection.update_one(request.filter, request.update, upsert=request.upsert)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/delete")
async def mongo_delete(request: MongoDeleteRequest, db = Depends(get_mongodb)):
    """Delete documents from a collection"""
    try:
        collection = db[request.collection]
        if request.many:
            result = collection.delete_many(request.filter)
        else:
            result = collection.delete_one(request.filter)
        return {"deleted_count": result.deleted_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/aggregate")
async def mongo_aggregate(request: MongoAggregateRequest, db = Depends(get_mongodb)):
    """Run an aggregation pipeline"""
    try:
        collection = db[request.collection]
        documents = list(collection.aggregate(request.pipeline))
        return {"documents": _serialize_documents(documents)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
