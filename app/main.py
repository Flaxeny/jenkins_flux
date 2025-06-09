from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import os

app = FastAPI()

MONGO_HOST = os.getenv("MONGO_HOST", "mongodb-service")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info() 
    db = client.mydatabase
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    db = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/items/")
def create_item(item: dict):
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not available")
    item_id = db.items.insert_one(item).inserted_id
    return {"item_id": str(item_id)}

@app.get("/items/{item_id}")
def read_item(item_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection not available")
    item = db.items.find_one({"_id": item_id})
    if item:
        item["_id"] = str(item["_id"])
        return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/health")
def health_check():
    try:
        client.server_info()
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="MongoDB connection failed")
