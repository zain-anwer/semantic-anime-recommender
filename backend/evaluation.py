from sentence_transformers import SentenceTransformer
from database import anime_collection, query_cache
from recommender import get_recommendations
from test_cases import TEST_SET


query_cache.delete_many({})

model = SentenceTransformer("all-mpnet-base-v2")

def precision_at_k(retrieved_ids, relevant_ids, k):
    top_k = retrieved_ids[:k]
    hits = len(set(top_k) & set(relevant_ids))
    return hits / k

def reciprocal_rank(retrieved_ids, relevant_ids):
    for i, id in enumerate(retrieved_ids):
        if id in relevant_ids:
            return 1/(i+1)
    return 0

cursor = anime_collection.find({}, {"title": 1,"title_english":1 ,"_id": 1})
title_id_pairs = [(doc["title"],doc["title_english"],doc["_id"]) for doc in cursor]
titles = [(t[0],t[1]) for t in title_id_pairs]

rr_list = []
pr_list = []

# verifying whether the test case ids are even present or not:

print("Verifying relevant_ids exist in collection...\n")
    
for test in TEST_SET:
    found = []
    missing = []
    for rid in test["relevant_ids"]:
        doc = anime_collection.find_one({"_id": rid}, {"title": 1})
        if doc:
            found.append(f"{rid}:{doc['title']}")
        else:
            missing.append(rid)
    print(f"Query: {test['query'][:40]}")
    print(f"  Found:   {found}")
    print(f"  Missing: {missing}\n")


query_cache.drop()

for i, test in enumerate(TEST_SET):
    mode, results = get_recommendations(test["query"],10,None,None,model,titles,title_id_pairs)
    
    retrieved_ids = [r["_id"] for r in results]
   
    titles_map = {d['_id']: d['title'] for d in anime_collection.find({"_id": {"$in": retrieved_ids}})}
    print("Query: ",test["query"])
    print("Results: ",titles_map)

    pr = precision_at_k(retrieved_ids,test["relevant_ids"],10)
    rr = reciprocal_rank(retrieved_ids,test["relevant_ids"])
    pr_list.append(pr)
    rr_list.append(rr)
    if mode == test["mode"]:
        print("Mode detected accurately for test case ",i+1)    
        print("Test case query: ",test["query"])
    else:
        print("INCORRECTLY IDENTIFIED QUERY TYPE")

mean_pr = sum(pr_list) / len(pr_list)
mean_rr = sum(rr_list) / len(rr_list)

print('-' * 50)
print("Mean Precision:          ",mean_pr)
print("Mean Reciprocal Rank:    ",mean_rr)
print('-' * 50)