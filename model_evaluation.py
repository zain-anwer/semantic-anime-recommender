# this is the same test but with a different assymetric model:

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv('anime_data_cleaned.csv')

model = SentenceTransformer('./anime-mpnet-triplet-finetuned')

# STRESS TESTING ASSYMETRIC MODEL:
# the goal is to find the average margins between the similarity scores
# if the delta between similarity scores for relevant and hard negatives is way less than the model is not very discriminative
# we will also be taking a look at the delta between relevant and easy negatives to

test_cases = {
    "political_strategy": {
        "query": "A brilliant strategist uses a newly acquired supernatural power to dismantle a corrupt regime from within.",
        "relevant_id": 1575,      # Code Geass (Focus: Rebellion/Politics)
        "hard_neg_id": 1535,      # Death Note (Focus: Personal Cat-and-Mouse/Police)
        "easy_neg_id": 5680,      # K-On! (Music Club)
        "note": "Tests if it recognizes 'regime/dismantle' vs 'detective/justice'."
    },
    "cyberpunk_justice": {
        "query": "A psychological thriller set in a high-tech dystopia where the line between criminal and lawman is blurred by a surveillance system.",
        "relevant_id": 13601,     # Psycho-Pass (Focus: Surveillance/Law)
        "hard_neg_id": 42310,     # Cyberpunk: Edgerunners (Focus: Crime/Mercenaries)
        "easy_neg_id": 20583,     # Haikyuu!! (Volleyball)
        "note": "Tests 'surveillance/lawman' against general 'cyberpunk crime'."
    },
    "nature_supernatural": {
        "query": "A somber, atmospheric exploration of the balance between humanity and the unseen, ancient spirits of the natural world.",
        "relevant_id": 457,       # Mushishi (Focus: Nature/Ancient)
        "hard_neg_id": 4081,      # Natsume Yuujinchou (Focus: Friendly/Grandma's Book)
        "easy_neg_id": 30276,     # One Punch Man (Superhero)
        "note": "Tests 'nature/ancient' vs 'interpersonal ghost-of-the-week'."
    },
    "cosmic_romance": {
        "query": "A supernatural romance exploring the emotional connection and fate of two individuals separated by cosmic occurrences.",
        "relevant_id": 32281,     # Kimi no Na wa. (Focus: Cosmic/Fate)
        "hard_neg_id": 38826,     # Tenki no Ko (Focus: Weather/Urban)
        "easy_neg_id": 16498,     # Attack on Titan (Giants)
        "note": "Tests for Shinkai-vibe specific nuances: 'cosmic/fate' vs 'weather'."
    },
    "european_manhunt": {
        "query": "A gritty, realistic pursuit of a charismatic but terrifying killer across a cold, post-war European landscape.",
        "relevant_id": 19,        # Monster (Focus: Serial Killer/Europe)
        "hard_neg_id": 37521,     # Vinland Saga (Focus: Revenge/Europe)
        "easy_neg_id": 50265,     # Spy x Family (Comedy/Spy)
        "note": "Tests 'serial killer/post-war' vs 'warrior/medieval'."
    }
}

delta_1 = 0
delta_2 = 0
i = 0

for test in test_cases.items():
  query = test[1]['query']
  relevant = df[df['mal_id'] == test[1]['relevant_id']]['embedding-text'].tolist()[0]
  hard_neg = df[df['mal_id'] == test[1]['hard_neg_id']]['embedding-text'].tolist()[0]
  easy_neg = df[df['mal_id'] == test[1]['easy_neg_id']]['embedding-text'].tolist()[0]
  query_embeddings = model.encode(query,normalize_embeddings=True)
  relevant_embeddings = model.encode(relevant,normalize_embeddings=True)
  hard_neg_embeddings = model.encode(hard_neg,normalize_embeddings=True)
  easy_neg_embeddings = model.encode(easy_neg,normalize_embeddings=True)
  relevant_score = cosine_similarity(query_embeddings.reshape(1,-1),relevant_embeddings.reshape(1,-1))[0][0]
  hard_neg_score = cosine_similarity(query_embeddings.reshape(1,-1),hard_neg_embeddings.reshape(1,-1))[0][0]
  easy_neg_score = cosine_similarity(query_embeddings.reshape(1,-1),easy_neg_embeddings.reshape(1,-1))[0][0]

  print('delta between relevant and hard negative: ',relevant_score - hard_neg_score)
  print('delta between relevant and easy negative: ',relevant_score - easy_neg_score)

  delta_1 += relevant_score - hard_neg_score
  delta_2 += relevant_score - easy_neg_score

  i += 1

print('Average delta between relevant and hard negative: ',delta_1/i)
print('Average delta between relevant and easy negative: ',delta_2/i)

"""
from sentence_transformers import SentenceTransformer, util
import torch

models_to_test = [
    'all-MiniLM-L6-v2',        # your current
    'all-MiniLM-L12-v2',       # upgrade same size
    'multi-qa-MiniLM-L6-cos-v1', # asymmetric specialist
    'all-mpnet-base-v2'
]

death_note_text = Supernatural Suspense Psychological Shounen psychological 
mind games mental manipulation suspense tension Brutal murders... Light Yagami 
discovers a Death Note and becomes Kira, engaged in a battle of wits with L.

queries = [
    "dark psychological mind games and moral dilemmas",
    "wholesome found family and friendship",  # should score LOW for Death Note
]

for model_name in models_to_test:
    model = SentenceTransformer(model_name)
    doc_emb = model.encode(death_note_text, normalize_embeddings=True)
    print(f"\n{model_name}")
    for q in queries:
        q_emb = model.encode(q, normalize_embeddings=True)
        score = util.cos_sim(doc_emb, q_emb).item()
        print(f"  {q[:45]}: {score:.4f}")

"""