# Anime Semantic Recommender System

A natural language anime recommendation engine that accepts descriptive vibe queries or title-based similarity searches and returns semantically relevant results using dense vector retrieval.

**Live Demo:** [semantic-anime-recommender.vercel.app](https://semantic-anime-recommender.vercel.app)  
**Backend:** Hosted on Hugging Face Spaces

---

## What It Does

Users can search in two ways:

- **Vibe search** — describe what you want: *"something dark and psychological"*, *"wholesome slice of life with found family"*
- **Similar search** — reference a title: *"something like Cowboy Bebop"*, *"anime like Attack on Titan"*

The system automatically detects query intent via fuzzy title matching and routes accordingly.

---

## Architecture

```
User Query (Natural Language)
        │
        ▼
 Intent Detection (rapidfuzz)
   ┌────┴────┐
   │         │
Similar     Vibe
  Mode      Mode
   │         │
   │    model.encode()  ←  all-mpnet-base-v2
   │         │
   └────┬────┘
        ▼
 MongoDB Atlas Vector Search
 (HNSW Index, Cosine Similarity)
        │
        ▼
 Hybrid Reranking
 (0.75 × semantic + 0.25 × popularity)
        │
        ▼
  Top-K Results → FastAPI → Vite/React Frontend
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Embeddings | `sentence-transformers` · `all-mpnet-base-v2` (768d) |
| Vector Store | MongoDB Atlas Vector Search · HNSW index |
| Backend | FastAPI · Python 3.12 |
| Frontend | Vite + React · TailwindCSS |
| Frontend Hosting | Vercel |
| Backend Hosting | Hugging Face Spaces |
| Database | MongoDB Atlas (free tier) |

---

## Dataset

- **Source:** Jikan API v4 (unofficial MyAnimeList REST wrapper)
- **Size:** 9,235 anime after cleaning
- **Scraping strategy:** Multi-pass — sorted by popularity descending (top 2,500 all-time) + sorted by score descending from 2010 onwards + pre-2010 classics pass
- **Second pass:** Individual `/anime/{id}/full` endpoint calls to recover missing `themes` and `synopsis` fields
- **Coverage:** Verified to contain 99%+ of culturally significant anime including Attack on Titan, Demon Slayer, Jujutsu Kaisen, Fullmetal Alchemist Brotherhood, Cowboy Bebop, and 9,000+ others

### Cleaning Pipeline

- Dropped synopses under 50 words (insufficient signal for embedding)
- Removed MAL placeholder strings (`"No synopsis information has been added..."`)
- Stripped `[Written by MAL Rewrite]` and `(Source: ...)` citation suffixes
- Removed non-ASCII characters and normalised whitespace
- Imputed `score` and `episodes` nulls with column median
- Filled missing `themes` and `demographics` with empty string (not dropped — synopsis carries embedding weight)
- Filtered non-anime content types: `Music`, `CM`, `PV`

### Genre Distribution

```python
Genre entropy: [your value here]  # higher = more balanced coverage
```

Known limitation: MAL's community skews toward Shounen and Action. Older and niche genres (Josei, historical) are underrepresented — a characteristic of the source platform, not the pipeline.

---

## Embedding Strategy

Each anime is embedded using a concatenated enriched text string:

```
{synopsis} {genres} {themes} {demographics}
```

Genre and theme tokens are appended directly to the synopsis so the model can capture explicit genre associations even when the synopsis text doesn't use those words. For example, a synopsis describing "a boy learning to cook" doesn't contain "slice-of-life" — but appending the genre tag pulls the embedding toward the correct neighbourhood.

All embeddings are L2-normalised at generation time (`normalize_embeddings=True`), reducing cosine similarity to a dot product and improving HNSW index performance.

---

## Retrieval Pipeline

### Vector Search

MongoDB Atlas Vector Search with an HNSW approximate nearest neighbour index over the 768-dimensional embedding field. Index configuration:

```json
{
  "fields": [
    { "type": "vector", "path": "embedding", "numDimensions": 768, "similarity": "cosine" },
    { "type": "filter", "path": "score" },
    { "type": "filter", "path": "genres" },
    { "type": "filter", "path": "popularity" }
  ]
}
```

`numCandidates` is set to `200 × limit` to ensure high recall before post-filtering.

### Hybrid Reranking

Raw cosine similarity is blended with a log-normalised popularity signal:

```
pop_score = 1 - (log10(popularity_rank) / log10(30000))
hybrid_score = 0.75 × similarity + 0.25 × pop_score
```

This prevents obscure anime with inflated cosine scores from displacing well-known relevant results, while still allowing semantically superior matches to win.

### Query Normalisation & Caching

Vibe query embeddings are cached in a `query_cache` MongoDB collection keyed by a normalised query string (lowercased, punctuation stripped, stopwords removed). Cache hits skip model inference entirely, reducing p50 latency by ~150-200ms.

---

## Query Intent Detection

Intent is classified via rapidfuzz fuzzy title matching after stripping recommendation preamble phrases ("something like", "anime similar to", "I loved X so...", etc.):

```python
REC_STOP_PHRASES = r"i (loved|liked|watched|want|need)|(something|anything|anime|show) like|similar to|..."
```

A token coverage check prevents false positives — the matched title's tokens must appear substantially in the cleaned query before routing to similar mode. Matching is performed against both Japanese romaji titles and English titles simultaneously, taking the higher-confidence match.

---

## Evaluation

Evaluated on a hand-curated 20-query test set covering vibe queries and title-similarity queries across diverse genres.

| Metric | Score |
|---|---|
| Mean Precision@10 | 0.16 |
| Mean Reciprocal Rank | 0.45 |

**Note on metrics:** These scores reflect strict exact-match evaluation against a manually assembled relevant set. Many returned results are genuinely good recommendations not captured in the relevant set — qualitative inspection shows strong performance particularly on vibe queries (Death Note for "dark psychological", Haikyuu/Kuroko for "sports competition teamwork", Toradora/Tsuki ga Kirei for "slow burn romance").

Known weaknesses:
- Short 3-word vibe queries (stopword removal reduces signal)
- Queries where "similar to X" phrasing strips the title below fuzzy match threshold
- Hubness in embedding space — some anime with generic synopses appear as universal neighbours

---

## Project Structure

```
anime-recommender-system/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # MongoDB connection
│   ├── recommender.py       # Embedding, intent detection, vector search pipeline
│   ├── evaluation.py        # Precision@K and MRR evaluation script
│   ├── test_cases.py        # Hand-curated 20-query evaluation set
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.jsx
│   │   │   ├── AnimeCard.jsx
│   │   │   └── ResultsGrid.jsx
│   │   ├── hooks/
│   │   │   └── useRecommendations.js
│   │   ├── api/
│   │   │   └── recommend.js
│   │   └── App.jsx
│   └── package.json
├── data_processing/
│   ├── scraping.ipynb        # Multi-pass Jikan API scraping
│   ├── cleaning.ipynb        # Data cleaning and EDA
│   └── data_processing_insertion.py  # Embedding generation + MongoDB insertion
└── README.md
```

---

## Running Locally

**Prerequisites:** Python 3.12, Node.js 18+, MongoDB Atlas account

**Backend:**

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:

```
DB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
DB_NAME=anime-recommender
```

```bash
python main.py
```

**Frontend:**

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

```bash
npm run dev
```

---

## API Reference

### `POST /recommend`

```json
{
  "query": "something dark and psychological",
  "limit": 10,
  "min_score": 7.0,
  "genres": ["Psychological"]
}
```

Response:

```json
{
  "mode": "vibe",
  "results": [
    {
      "mal_id": 1535,
      "title": "Death Note",
      "title_english": "Death Note",
      "score": 8.62,
      "genres": ["Mystery", "Psychological", "Supernatural", "Thriller"],
      "similarity": 0.847,
      "hybrid_score": 0.723,
      "image_url": "https://..."
    }
  ]
}
```

### `GET /anime/{mal_id}`

Returns a single anime document by MAL ID.

### `GET /health`

Returns `{"status": "ok"}`.

---

## What I Learned / Would Do Differently

**If I had more time, reliable methods and a GPU!!!:**

- Generate a reliable hard negatives map for documents (so that I could adjust weights to push queries closer to ground truths and away from hard/easy negatives like Rocchio Algorithm)
- Fine-tune `all-mpnet-base-v2` on domain-specific (query, relevant anime synopsis) pairs using Multiple Negatives Ranking Loss — the generic model lacks discriminative power for anime-specific vocabulary
- Implement sparse-dense hybrid retrieval (TF-IDF fallback for out-of-vocabulary queries)
- Add KMeans genre clustering for result diversity (prevent top-10 being all sequels of the same series)
- Collect real user interaction data to enable collaborative filtering signals beyond MAL community recommendations

**Architecture decisions I'd change:**

- Store `embedding_text` in MongoDB alongside the embedding — currently it's only in the CSV, making re-embedding require reloading from file
- Use `deque` instead of list for the scraping second-pass queue
- Add structured logging to FastAPI rather than print statements

---

## Acknowledgements

- [Jikan API](https://jikan.moe/) — unofficial MAL REST wrapper, no API key required
- [sentence-transformers](https://www.sbert.net/) — `all-mpnet-base-v2` model
- [MongoDB Atlas](https://www.mongodb.com/atlas) — vector search infrastructure
