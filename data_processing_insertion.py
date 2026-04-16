
from pymongo import MongoClient
from dotenv import load_dotenv
import os                           # we need the os library to read the env file
import pandas as pd
from sentence_transformers import SentenceTransformer


# the equivalent of dotenv.config() perhaps
# so that we could load environment variables
load_dotenv("backend/.env")

client = MongoClient(os.getenv('DB_URI'))
db = client[os.getenv('DB_NAME')]
anime_collection = db['anime']
query_cache = db['query_cache']

anime_collection.delete_many({})
query_cache.delete_many({})

# creating a pandas dataframe
df = pd.read_csv('anime_data_cleaned.csv')

# renaming a column because hyphens are problematic
df = df.rename(columns={'embedding-text': 'embedding_text'})

print(f"CSV rows:          {len(df)}")
print(f"Unique mal_ids:    {df['mal_id'].nunique()}")
print(f"MongoDB documents: {anime_collection.count_documents({})}")

# getting model for embeddings generation
model = SentenceTransformer("all-mpnet-base-v2")

print("Generating Embeddings...")

# generating embeddings
embeddings = model.encode(
    df["embedding_text"].tolist(),
    batch_size=64,
    show_progress_bar=True,
    normalize_embeddings=True
)

# checking embedding shape

print("Embedding Shape",embeddings.shape)

# inserting them into the database in batches

BATCH_SIZE = 500
total = len(df)

for i in range(0, total, BATCH_SIZE):
    
    batch_df = df.iloc[i:i+BATCH_SIZE]
    
    batch_embeddings = embeddings[i:i+BATCH_SIZE]
    
    documents = []
    
    for j, (_, row) in enumerate(batch_df.iterrows()):
    
        documents.append({
            "_id":          int(row["mal_id"]),
            "title":        row["title"],
            "title_english":row["title_english"],
            "synopsis":     row["synopsis"],
            "score":        float(row["score"]),
            "popularity":   int(row["popularity"]),
            "episodes":     int(row["episodes"]),
            "status":       row["status"],
            "image_url":    row["image_url"],
            "genres":       row["genres"].split("|") if row["genres"] != "" else [],
            "themes":       row["themes"].split("|") if row["themes"] not in ["", "Unknown"] else [],
            "demographics": row["demographics"].split("|") if row["demographics"] not in ["", "Unknown"] else [],
            "is_scored":    pd.notna(row.get("score")),
            "embedding":    batch_embeddings[j].tolist()
        })
    
    try:
        result = anime_collection.insert_many(documents, ordered=False)
        inserted_count = len(result.inserted_ids)
        db_total = anime_collection.count_documents({})
        print(f"Batch {i//BATCH_SIZE + 1}: attempted {len(documents)}, inserted {inserted_count}, DB total: {db_total}")
    except Exception as e:
        db_total = anime_collection.count_documents({})
        print(f"Batch {i//BATCH_SIZE + 1} errors: {e.details.get('nInserted', 0)} inserted, DB total: {db_total}")

print("Done. Verifying...")
print(f"Documents in collection: {anime_collection.count_documents({})}")