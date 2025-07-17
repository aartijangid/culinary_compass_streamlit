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
    
    visualize_similarity_3d(recommended_recipes)
    
    # Displaying input and recipe embeddings with cosine similarity and nutritional values
    for idx, recipe in top_recipes.iterrows():
        recipe_embedding = recipe["IngredientEmbedding"]  # The recipe's embedding from your DataFrame
        recipe_embedding_tensor = torch.tensor(recipe_embedding).to(device)

        # Calculate cosine similarity for input vs. recipe
        embedding_similarity = util.pytorch_cos_sim(input_embedding, recipe_embedding_tensor).item()

        # print(f"Recipe: {recipe['Name']}")
        # print(f"Input Ingredient Embedding: {input_embedding.cpu().numpy()}")
        # print(f"Recipe Ingredient Embedding: {recipe_embedding}")
        print(f"Cosine Similarity: {embedding_similarity:.4f}")
        
        # Nutritional details for input vs. recommended recipe
        print(f"\nInput Nutrients: {nutrients}")
        print(f"Recipe Nutrients: {recipe[nutrient_columns].to_dict()}")
        
        # Displaying similarity of nutrition
        print(f"Nutrient Similarity: {recipe['nutrient_similarity']:.4f}")
        print(f"Ingredient Similarity: {recipe['ingredient_similarity']:.4f}")
        print(f"Similarity Score: {recipe['SimilarityScore']:.4f}")
        print("-" * 50)
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

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def visualize_similarity_3d(recommended_recipes):
    # Sort the recipes by SimilarityScore in descending order and select top 5
    top_5_recipes = recommended_recipes.sort_values(by="SimilarityScore", ascending=False).head(5)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Scatter plot in 3D for all recipes with smaller markers (green)
    ax.scatter(recommended_recipes["ingredient_similarity"], recommended_recipes["nutrient_similarity"], recommended_recipes["SimilarityScore"], 
               color='#a4c1f3', alpha=0.7, s=50)
    
    # Highlight top 5 recipes with larger markers and different color (blue)
    ax.scatter(top_5_recipes["ingredient_similarity"], top_5_recipes["nutrient_similarity"], top_5_recipes["SimilarityScore"], 
               color='#6d15a1', alpha=1.0, s=50, label='Top 5 Recipes')
    
    # Set axis labels and title
    ax.set_title("Ingredient Similarity vs Nutrient Similarity vs Similarity Score")
    ax.set_xlabel("Ingredient Similarity")
    ax.set_ylabel("Nutrient Similarity")
    ax.set_zlabel("Similarity Score")
    
    # Set axis limits (to avoid the plot scaling issues and overlap)
    ax.set_xlim([recommended_recipes["ingredient_similarity"].min(), recommended_recipes["ingredient_similarity"].max()])
    ax.set_ylim([recommended_recipes["nutrient_similarity"].min(), recommended_recipes["nutrient_similarity"].max()])
    ax.set_zlim([recommended_recipes["SimilarityScore"].min(), recommended_recipes["SimilarityScore"].max()])
    
    # Annotate only top 5 recipes with their names
    for i, row in top_5_recipes.iterrows():
        ax.text(row["ingredient_similarity"], row["nutrient_similarity"], row["SimilarityScore"], 
                row["Name"], fontsize=9, alpha=1.0, color='black', horizontalalignment='center')
    
    # Add a legend for top 5
    ax.legend()
    
    # Save the plot to a file
    plt.savefig("3d_plot.png", dpi=300, bbox_inches='tight')
    plt.show()
