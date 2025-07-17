import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
import pickle
import numpy as np
import os

# Load dataset
df = pd.read_csv("data/preprocessed/recipes.csv")
#df =df.iloc[0:50000]

# Initialize model
#st_model = SentenceTransformer("all-MiniLM-L6-v2")

#all-mpnet-base-v2
# st_model = SentenceTransformer("all-mpnet-base-v2") - Observation Recommendation gets better but slow compared to all-MiniLM-L6-v2 

#all-mpnet-base-v2
st_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# Save the trained model
with open("models/recipes_st.pkl", "wb") as model_file:
    pickle.dump(st_model, model_file)


# # Compute embeddings
# df["IngredientEmbedding"] = df["RecipeIngredientParts"].apply(lambda x: st_model.encode(str(x), convert_to_tensor=True).tolist())

# # Save embeddings
# df.to_csv("data/embeddings/recipes.csv", index=False)

# Code for batch processing

# Define batch parameters
batch_size = 5000
num_batches = (len(df) + batch_size - 1) // batch_size  # Calculate the number of batches

# Directory to save batch embeddings
embedding_dir = "data/embeddings/batches"
os.makedirs(embedding_dir, exist_ok=True)

# Process each batch
for i in range(num_batches):
    start_idx = i * batch_size
    end_idx = min((i + 1) * batch_size, len(df))
    batch_df = df.iloc[start_idx:end_idx].copy()  # Use .copy() to avoid SettingWithCopyWarning

    # Print the row indices for the current batch
    print(f"Processing batch {i+1}/{num_batches}, rows {start_idx} to {end_idx-1}")

    # Compute embeddings and add as a new column
    batch_df["IngredientEmbedding"] = batch_df["RecipeIngredientParts"].apply(
        lambda x: st_model.encode(str(x), convert_to_tensor=True).tolist()
    )

    # Save the updated DataFrame to CSV
    batch_df.to_csv(f"{embedding_dir}/embeddings_batch_{i+1}.csv", index=False)
    print(f"Saved embeddings for batch {i+1}/{num_batches}")

# Optionally, concatenate all batch files into a single embeddings file
all_embeddings = pd.concat(
    [pd.read_csv(f"{embedding_dir}/embeddings_batch_{i+1}.csv") for i in range(num_batches)],
    ignore_index=True
)
all_embeddings.to_csv("data/embeddings/recipes.csv", index=False)
print("All batch embeddings concatenated and saved.")
