import pandas as pd
import math
import logging
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer, InputExample, losses, evaluation
from torch.utils.data import DataLoader
from datasets import load_dataset


with open('pos_neg_map.json','r') as file:
    pos_neg_map = json.load(file)

logging.basicConfig(level=logging.INFO)

# 1. LOAD DATA
df = pd.read_csv('anime_data_cleaned.csv')
# Standardizing the column name as per your snippet
df['embedding_text'] = df['embedding-text']
df.drop(columns=['embedding-text'], inplace=True)

# 2. DATA MIXING (Modified for Triplets)
def get_nli_mixing_triplets(n=200):
    logging.info(f"Loading {n} samples of generic NLI triplets...")
    # SNLI labels: 0=entailment (positive), 1=neutral, 2=contradiction (negative)
    dataset = load_dataset("snli", split="train", streaming=True)
    generic_examples = []
    
    # We need to find a premise that has both an entailment and a contradiction
    # This keeps the "general English" anchor stable
    current_premise = None
    pos = None
    neg = None

    for entry in dataset:
        if len(generic_examples) >= n: break
        
        # In SNLI, same premises are often grouped together
        if entry['label'] == 0: # Entailment
            pos = entry['hypothesis']
            current_premise = entry['premise']
        elif entry['label'] == 2 and entry['premise'] == current_premise: # Contradiction
            neg = entry['hypothesis']
            
            if current_premise and pos and neg:
                generic_examples.append(InputExample(texts=[current_premise, pos, neg]))
                # Reset for next triplet
                current_premise, pos, neg = None, None, None
                
    return generic_examples

# 3. BUILD ANIME TRIPLETS
def build_anime_triplets(df, hard_negatives_map):
    triplet_num = 0
    examples = []
    for _, row in df.iterrows():
        anchor_text = row['embedding_text']
        mal_id_str = str(row['mal_id'])
        
        entry = hard_negatives_map.get(mal_id_str, {})
        pos_ids = entry.get('positives', [])
        neg_ids = entry.get('hard_negatives', [])
        
        for pos_id, neg_id in zip(pos_ids, neg_ids):
            # Cast to int to ensure matching with DataFrame types
            pos_row = df[df['mal_id'] == int(pos_id)]
            neg_row = df[df['mal_id'] == int(neg_id)]
            
            if not pos_row.empty and not neg_row.empty:
                triplet_num += 1
                examples.append(InputExample(texts=[
                    anchor_text, 
                    pos_row.iloc[0]['embedding_text'], 
                    neg_row.iloc[0]['embedding_text']
                ]))
    print('Number of triplets for model: ',triplet_num)
    return examples[:800]

# 4. INITIALIZING MODEL
model = SentenceTransformer('all-mpnet-base-v2')

# --- PREPARE DATA ---
# Ensure your pos_neg_map has 'hard_negatives' filled for this to work!
anime_train = build_anime_triplets(df, pos_neg_map)
generic_train = get_nli_mixing_triplets(n=200)
all_train_examples = anime_train + generic_train

# 5. TRAINING CONFIGURATION
BATCH_SIZE = 8 # Triplet loss can be memory intensive; 16 is safer for CPU
EPOCHS = 1
train_dataloader = DataLoader(all_train_examples, shuffle=True, batch_size=BATCH_SIZE,num_workers=0,pin_memory=False)

# TripletLoss logic: distance(anchor, pos) + margin < distance(anchor, neg)
train_loss = losses.TripletLoss(model=model)

# 6. EVALUATOR (Same as before, tracks if model separates pairs correctly)
eval_examples = [
    InputExample(texts=['dark psychological mind games thriller', 'Death Note synopsis...'], label=1.0),
    InputExample(texts=['dark psychological mind games thriller', 'Haikyuu!! synopsis...'], label=0.0),
]
evaluator = evaluation.EmbeddingSimilarityEvaluator.from_input_examples(eval_examples, name='anime-triplet-eval')

# 7. FIT
warmup_steps = math.ceil(len(train_dataloader) * EPOCHS * 0.1)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    evaluator=evaluator,
    epochs=EPOCHS,
    warmup_steps=warmup_steps,
    output_path='./anime-mpnet-triplet-finetuned',
    save_best_model=True,
    optimizer_params={'lr': 2e-5},
    use_amp=False 
)

logging.info("Training Complete!!! Triplet model saved.")