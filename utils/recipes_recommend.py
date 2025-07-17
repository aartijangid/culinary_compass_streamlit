import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Set device (CPU or GPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

import torch

@torch.jit.script
class MyCustomClass:
    def __init__(self):
        pass

# Load model
def load_data():
    """ Load dataset with embeddings """
    df = pd.read_csv("data/embeddings/recipes.csv")
    
    # Ensure embeddings are properly converted to tensors and moved to the correct device
    df["IngredientEmbedding"] = df["IngredientEmbedding"].apply(lambda x: torch.tensor(eval(x)).to(device))

    with open("models/recipes_st.pkl", "rb") as model_file:
        model_st = pickle.load(model_file)

    return df, model_st

def recommend_recipes(nutrients, ingredients, diet_preference):
#def recommend_recipes(ingredients, diet_preference):
    """Recommend recipes based on user nutrients, ingredients, and dietary preference."""
    df, model_st = load_data()

    # Filter by dietary preference
    if diet_preference == "Veg":
        df_filtered = df[df["DietaryCategory"] == diet_preference].copy()
    else:
        df_filtered = df.copy()

    # Encode input ingredients and move them to the same device
    input_embedding = model_st.encode(" ".join(ingredients), convert_to_tensor=True).to(device)

    # Stack ingredient embeddings and move to the same device
    ingredient_embeddings = torch.stack(df_filtered["IngredientEmbedding"].tolist()).to(device)

    """# Compute cosine similarity
    ingredient_similarities = util.pytorch_cos_sim(ingredient_embeddings, input_embedding).squeeze().cpu().numpy()

    # Compute Euclidean similarity for nutrients
    # nutrient_columns = ["Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", 
    #                     "SodiumContent", "CarbohydrateContent", "FiberContent", "SugarContent", "ProteinContent"]

    nutrient_columns = ["Calories", "FatContent", "CarbohydrateContent", "FiberContent", "SugarContent", "ProteinContent"]
    
    df_nutrients = df_filtered[nutrient_columns].fillna(0).to_numpy()
    input_nutrient_array = np.array([nutrients[col] for col in nutrient_columns]).reshape(1, -1)
    if input_nutrient_array.max() > 0:
        input_nutrient_array = input_nutrient_array/input_nutrient_array.max() # to normalize

    #nutrient_distances = np.linalg.norm(df_nutrients - input_nutrient_array, axis=1)
    #nutrient_similarities = 1 / (1 + nutrient_distances)

    #trying cosine similarity
    # Extract recipe nutrient vectors
    recipe_vectors = np.array(df_filtered[nutrient_columns].values)  # Get nutrient values only
    recipe_vectors = recipe_vectors/recipe_vectors.max() # to normalize

    # Compute cosine similarity between user input and all recipes
    nutrient_similarities = cosine_similarity(input_nutrient_array, recipe_vectors)

    # Add similarity scores to DataFrame
    df_filtered["similarity"] = nutrient_similarities[0]

    # Sort recipes by similarity score
    #recommended_recipes = recipes.sort_values(by="similarity", ascending=False)

    # Display Top Recommendations
    #print(recommended_recipes[["recipe", "similarity"]])

    # Final score (weighted)
    final_scores = (0.4 * nutrient_similarities) + (0.6 * ingredient_similarities)

    # Get top recommendations
    df_filtered["SimilarityScore"] = final_scores.flatten()
    top_recipes = df_filtered.sort_values(by="SimilarityScore", ascending=False).head(5)

    return top_recipes[
        [
            "Name", "CookTime", "Images", "RecipeCategory", "Keywords", 
            "RecipeIngredientQuantities", "RecipeIngredientParts", 
            "Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", 
            "SodiumContent", "CarbohydrateContent", "FiberContent", 
            "SugarContent", "ProteinContent", "RecipeInstructions", "DietaryCategory"
        ]
    ].to_dict(orient="records")"""
# trying to get recommendation in two steps
# Compute cosine similarity
    ingredient_similarities = util.pytorch_cos_sim(ingredient_embeddings, input_embedding).squeeze().cpu().numpy()

 # Add similarity scores to DataFrame
   # 
    df_filtered["ingredient_similarity"] = ingredient_similarities
    # Sort recipes by similarity score
    recommended_recipes = df_filtered.sort_values(by="ingredient_similarity", ascending=False)

    recommended_recipes=recommended_recipes.head(50)
     # Compute Euclidean similarity for nutrients
    nutrient_columns = ["Calories", "FatContent", "CarbohydrateContent", "FiberContent", 
                        "SugarContent", "ProteinContent"]
    
    df_nutrients = recommended_recipes[nutrient_columns].fillna(0).to_numpy()
    input_nutrient_array = np.array([nutrients[col] for col in nutrient_columns]).reshape(1, -1)
    if input_nutrient_array.max() > 0:
        input_nutrient_array = input_nutrient_array/input_nutrient_array.max() # to normalize

    # Extract recipe nutrient vectors
    recipe_vectors = np.array(recommended_recipes[nutrient_columns].values)  # Get nutrient values only
    recipe_vectors = recipe_vectors/recipe_vectors.max() # to normalize

    # Compute cosine similarity between user input and all recipes
    nutrient_similarities = cosine_similarity(input_nutrient_array, recipe_vectors)

    # Add similarity scores to DataFrame
    recommended_recipes["nutrient_similarity"] = nutrient_similarities[0]
     # Final score (weighted)
    #final_scores = (0.5 * nutrient_similarities) + (0.5 * ingredient_similarities)

      # Get top recommendations
    recommended_recipes["SimilarityScore"] = recommended_recipes.apply(lambda row:row["nutrient_similarity"]*0.5 + row["ingredient_similarity"]*0.5, axis=1)

    # Sort recipes by similarity score
    recommended_recipes = recommended_recipes.sort_values(by="SimilarityScore", ascending=False)
    top_recipes = recommended_recipes.head(5)
    return top_recipes[
        [
            "Name", "CookTime", "Images", "RecipeCategory", "Keywords", 
            "RecipeIngredientQuantities", "RecipeIngredientParts", 
            "Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", 
            "SodiumContent", "CarbohydrateContent", "FiberContent", 
            "SugarContent", "ProteinContent", "RecipeInstructions", "DietaryCategory"
        ]
    ].to_dict(orient="records")
    # Display Top Recommendations
    #print(recommended_recipes[["recipe", "similarity"]])    
    #return recommended_recipes
#print (recommend_recipes('iron','veg'))