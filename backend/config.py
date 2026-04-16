from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.database import anime_collection
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

@asynccontextmanager
async def lifespan(app : FastAPI):
    
    print("Loading anime titles into memory...")
    cursor = anime_collection.find({}, {"title": 1,"title_english":1 ,"_id": 1})
    
    # storing the lists in app state
    app.state.title_id_pairs = [(doc["title"],doc["title_english"],doc["_id"]) for doc in cursor]
    app.state.titles = [(t[0],t[1]) for t in app.state.title_id_pairs]
    app.state.model = SentenceTransformer(os.getenv('MODEL_NAME'))

    yield  # handover to server code
    
    # cleaningup code on shutdown
    app.state.titles.clear()
    app.state.title_id_pairs.clear()
    del app.state.model