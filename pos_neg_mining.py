import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import pandas as pd
import json
from sentence_transformers import SentenceTransformer
from backend.recommender import get_recommendations

model = SentenceTransformer('all-mpnet-base-v2')
df = pd.read_csv('anime_data_cleaned.csv')

titles = df['title'].tolist()
titles_english = df['title_english'].tolist()
ids = df['mal_id'].tolist()
titles_zipped = list(zip(titles, titles_english))
# FIX: Zipping into the 2-item structure (zipped_titles, id) the recommender expects
title_id_pairs = list(zip(titles,titles_english, ids))

pos_neg_map = {}

for i, row in df.iterrows():
    if i % 500 == 0:
        print(f"{i} rows processed")
    
    title = row['title']
    
    # increasing filter to 30 to get greater chances of finding good positive, negative pairs
    _, results = get_recommendations(title, 30, None, None, model, titles_zipped, title_id_pairs)
            
    positives = []
    negatives = []

    anchor_genres = set(row['genres'].split('|'))

    for res in results:
        if int(res['_id']) == int(row['mal_id']):
            continue
            
        intersection = anchor_genres.intersection(set(res['genres']))
        
        # we are calculating overlap ratio so that single genre anime are not unnecessarily penalized
        overlap_ratio = len(intersection) / len(anchor_genres) if anchor_genres else 0
        
        # positive ones must have at least 0.7% overlap 
        if (overlap_ratio >= 0.5 or len(intersection) >= 2) and res['score'] > 7 and len(positives) < 3:
            positives.append(int(res['_id']))
        
        # negative ones must have less than 50% overlap
        elif overlap_ratio <= 0.4 and res['score'] > 6.0 and len(negatives) < 3:
            negatives.append(int(res['_id']))
            
    pos_neg_map[str(row['mal_id'])] = {
        'positives': positives,
        'hard_negatives': negatives
    }

with open('pos_neg_map.json', 'w') as file:
    json.dump(pos_neg_map, file)