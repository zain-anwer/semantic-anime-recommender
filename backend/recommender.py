# I just got confused between strip and split ~_~

from fastapi import FastAPI, Request
from database import anime_collection, query_cache
from rapidfuzz import process, fuzz
from nltk.corpus import stopwords
from datetime import datetime
from math import log10
import nltk
import re

nltk.download('stopwords', quiet=True)
STOPWORDS = set(stopwords.words('english'))

def normalize_query(query : str):
    
    query = query.lower()

    # removing accents, extra spaces, special characters etc

    # removing anything that is not a letter, number, underscore, or whitespace
    query = re.sub(r'[^\w\s]', '', query)
    
    # spaces
    query = re.sub(r'\s+', ' ', query).strip()

    tokens = query.split()
    tokens = [token for token in tokens if token not in STOPWORDS]

    # commenting this out because word embeddings care about order
    # tokens = sorted(tokens)
    
    return " ".join(tokens)

def detect_mode(query, titles, title_id_pairs):

    SIMILAR_SIGNALS = r"""

    \b(
    # direct similarity phrases

    similar\s+to
    | in\s+the\s+vein\s+of
    | along\s+the\s+lines\s+of
    | in\s+the\s+style\s+of
    | same\s+(vibe|style|feel|energy|tone)\s+as
    | reminds?\s+me\s+of
    | makes?\s+me\s+think\s+of

    # "like X" patterns
    | (something|anything|anime|shows?|series)\s+like
    | (more|stuff)\s+like
    | just\s+like
    | \blike\b   # bare "like" — kept as last resort since it's broad

    # consumption + implicit request
    | i\s+(just\s+)?(watched|finished|binged|completed|saw|read)
    | i\s+(really\s+)?(liked|loved|enjoyed|adored|was\s+obsessed\s+with)
    | i\s+(ve|have)\s+(watched|seen|finished|completed|loved|liked|enjoyed)
    | just\s+(finished|watched|completed|binged)

    # recommendation framing
    | (can\s+you\s+)?(recommend|suggest)\s+(me\s+)?(something|anime|a\s+show|shows?)?\s*(like|similar\s+to)?
    | (find|show|give)\s+me\s+(something|anime|more)?\s*(like|similar)?
    | looking\s+for\s+(something|anime|more|a\s+show)\s*(like|similar\s+to)?
    | what\s+(else\s+)?(should|can|do)\s+i\s+watch\s+(if\s+i\s+(liked?|loved?|enjoyed?))?
    | (something|anything|anime|shows?|series)(\s+\w+)?\s+like
    | \blike\b
    | what\s+anime\s+is\s+(like|similar\s+to)
    | anything\s+(like|similar\s+to)

    # fan identity
    | (for\s+)?fans?\s+of
    | if\s+you\s+(liked?|loved?|enjoyed?|watched?)
    | (fellow\s+)?fan\s+of

    # more-of-same framing
    | more\s+(of|like)
    | another\s+(anime|show|series)\s+like
    | other\s+(anime|shows?|series)\s+(like|similar\s+to)
    | (are\s+there|is\s+there)\s+(any|another|more)\s+(anime|shows?)?\s*(like|similar\s+to)?
    )\b

    """

    FILLER = r'\b(so|some|anime|like|that|just|want|need|something|anything|supernatural|epic|good|great|similar|more|another|show|series|please)\b'

    # (Regex definitions stay the same as your snippet)
    SIMILAR_SIGNALS = re.compile(SIMILAR_SIGNALS, re.IGNORECASE | re.VERBOSE)
    FILLER = re.compile(FILLER, re.IGNORECASE | re.VERBOSE)

    similar_intent = re.search(SIMILAR_SIGNALS, query)

    if not similar_intent:
        return ('vibe', None)

    entity_query = re.sub(SIMILAR_SIGNALS, '', query)
    entity_query = re.sub(r'[^\w\s]', '', entity_query)
    entity_query = re.sub(r'\s+', ' ', entity_query).strip()

    t1 = [t[0] for t in titles]
    t2 = [t[1] for t in titles]

    match1, score1, idx1 = process.extractOne(entity_query, t1, scorer=fuzz.partial_ratio)
    match2, score2, idx2 = process.extractOne(entity_query, t2, scorer=fuzz.partial_ratio)

    score = max(score1, score2)
    idx = idx1 if score1 >= score2 else idx2
    match = match1 if score1 >= score2 else match2

    if score >= 85:
    
        def get_clean_tokens(text):
            text = re.sub(FILLER, '', text.lower()) # Remove filler
            text = re.sub(r'[^\w\s]', '', text)     # Remove punctuation
            return set(text.split())

        query_tokens = get_clean_tokens(entity_query)
        title_tokens = get_clean_tokens(match)

        shortest_length = max(min(len(query_tokens), len(title_tokens)), 1)
        overlap = len(query_tokens & title_tokens) / shortest_length

        if overlap >= 0.5:
            anime_id = title_id_pairs[idx][2]
            anime_match = anime_collection.find_one({'_id': anime_id})
            return ('similar', anime_match)
        
    return ('vibe', None)

def get_recommendations(query,limit,min_score,genres,model,titles,title_id_pairs):

    normalized_query = normalize_query(query)
    query_embeddings = query_cache.find_one({'_id':normalized_query})
    print("Original Query: ",query)
    print("Normalized Query: ",normalized_query)

    if query_embeddings != None:
        query_cache.update_one(
            {'_id': normalized_query}, 
            {'$inc': {'hit_count': 1}}
        )
        query_embeddings = query_embeddings['embedding']
        mode = 'vibe' # since we only cache vibe queries
        anime_match = None

    else:

        mode, anime_match = detect_mode(query,titles,title_id_pairs)

        if mode == 'similar':
            query_embeddings = anime_match['embedding']
        else:
            query_embeddings = model.encode(
                query, normalize_embeddings=True
            ).tolist()

            query_cache.insert_one(
                {
                    '_id' : normalized_query,
                    'original_query' : query,
                    'embedding' : query_embeddings,
                    'hit_count' : 1,
                    'created_at' : datetime.utcnow(),
                }
            )
    
    # vector search plus post processing for filters and collaborative filtering
    # the pipeline can be thought of as a list of operations and checks performed sequentially

    pipeline = [
        
        {
            '$vectorSearch': {
                'index': 'vector_index',            # index name
                'path': 'embedding',                 # name of the field that stores embeddings
                'queryVector': query_embeddings,     # the query embeddings
                'numCandidates': 200 * limit,        # this is the size of the priority queue in ANN search
                'limit': limit * 5                   # we overfetch to account for filtering that will happen below
            }

        },

        {
            '$addFields': {
                'similarity': {'$meta': 'vectorSearchScore'}  # this looks for the score in the meta data
            }
        }
    ]

    # here we add the filtering part of the pipeline 

    # filtering by min_score
    match_conditions = {}
    if min_score != None:
        match_conditions['score'] = {'$gte':min_score}
    
    # filtering by genres
    if genres:
        match_conditions['genres'] = {'$all':genres}
    
    # removing the result with the _id equals that of the anime in case of similar search
    if mode == 'similar' and anime_match is not None:
        match_conditions['_id'] = {'$ne':anime_match['_id']}

    # Adding a similarity threshold / floor value
    MIN_SIMILARITY_THRESHOLD = 0.7
    MIN_VIBE_QUERY_THRESHOLD = 0.5

    if mode == 'similar':
        match_conditions['similarity'] = {'$gte':MIN_SIMILARITY_THRESHOLD}
    else:
        match_conditions['similarity'] = {'$gte':MIN_VIBE_QUERY_THRESHOLD}

    if match_conditions:
        pipeline.append({'$match':match_conditions})


    # formula for hybrid ranking:
    # 0.7 * similarity + (log(popularity_rank)/log(max_popularity_rank)) * 0.3
    
    MAX_POP_LOG = log10(30000)  # log(30000) (to be on the safe side since max popularity score in my dataset is 29853)

    pipeline.append({
        "$addFields": {
            "pop_score": {
                "$subtract": [
                    1,
                    {
                        "$divide": [
                            {"$log10": {"$max": ["$popularity", 1]}}, # safetyyy : max(pop, 1)
                            MAX_POP_LOG
                        ]
                    }
                ]
            }
        }
    })

    pipeline.append({
        "$addFields": {
            "hybrid_score": {
                "$add": [
                    {"$multiply": ["$similarity", 0.80]},
                    {"$multiply": ["$pop_score", 0.20]}
                ]
            }
        }
    })

    # sort in descending order based on the newly created hybrid score field
    pipeline.append({"$sort": {"hybrid_score": -1}})

    # drop the embedding field (frontend doesn't need that)
    pipeline.append({"$project": {"embedding": 0}})

    # limit the number of searches
    pipeline.append({"$limit": limit})
    
    try:
        results = list(anime_collection.aggregate(pipeline))
        print(f"Vector search returned {len(results)} results")
        if results:
            print(f"First result: {results[0].get('title')} similarity: {results[0].get('similarity')}")
    except Exception as e:
        print(f"Pipeline error: {e}")
        results = []

    return mode, results