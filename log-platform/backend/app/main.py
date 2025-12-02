from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from elasticsearch import Elasticsearch, exceptions as es_exceptions
import os
import uuid

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "elasticsearch")
ELASTIC_PORT = os.getenv("ELASTIC_PORT", "9200")
ELASTIC_SCHEME = os.getenv("ELASTIC_SCHEME", "http")
LOG_INDEX = os.getenv("LOG_INDEX", "logs-0001")

app = FastAPI(title="Log Ingestion & Search API")

es = Elasticsearch(f"{ELASTIC_SCHEME}://{ELASTIC_HOST}:{ELASTIC_PORT}", verify_certs=False)


class LogItem(BaseModel):
    service: str
    level: str
    message: str
    timestamp: Optional[datetime] = datetime.utcnow()
    meta: Optional[Dict[str, Any]] = None


class SearchResponseHit(BaseModel):
    id: str
    service: str
    level: str
    message: str
    timestamp: datetime
    meta: Optional[Dict[str, Any]]


class SearchResponse(BaseModel):
    total: int
    hits: List[SearchResponseHit]


@app.on_event("startup")
def startup():
    try:
        if not es.indices.exists(index=LOG_INDEX):
            es.indices.create(
                index=LOG_INDEX,
                body={
                    "mappings": {
                        "properties": {
                            "service": {"type": "keyword"},
                            "level": {"type": "keyword"},
                            "message": {"type": "text"},
                            "timestamp": {"type": "date"},
                            "meta": {"type": "object"}
                        }
                    }
                }
            )
    except Exception as e:
        print("Index creation error:", e)


@app.get("/health")
def health():
    try:
        ok = es.ping()
        return {"status": "ok" if ok else "error"}
    except:
        return {"status": "error"}


@app.post("/logs", status_code=201)
def add_log(log: LogItem):
    try:
        log_id = str(uuid.uuid4())
        es.index(index=LOG_INDEX, id=log_id, document=log.dict())
        return {"id": log_id, "stored": True}
    except es_exceptions.ElasticsearchException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs/search", response_model=SearchResponse)
def search_logs(query: Optional[str] = None, limit: int = 20):
    try:
        body = {
            "query": {"match": {"message": query}} if query else {"match_all": {}},
            "size": limit,
            "sort": [{"timestamp": {"order": "desc"}}],
        }
        results = es.search(index=LOG_INDEX, body=body)
        hits = [
            SearchResponseHit(
                id=hit["_id"],
                **hit["_source"]
            )
            for hit in results["hits"]["hits"]
        ]
        return SearchResponse(total=results["hits"]["total"]["value"], hits=hits)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
