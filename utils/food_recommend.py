import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pickle

def load_data():
    """Load processed food data and trained KNN model."""
    df = pd.read_csv("data/preprocessed/food.csv")
    original_df = pd.read_csv("data/original/food.csv") #loading original data 
    with open("models/knn_model.pkl", "rb") as model_file:
        knn = pickle.load(model_file)
    return df, knn, original_df





def format_recommendations(recommended_items, selected_deficiencies):
    """
    Format the recommendations into a structured list of categories and food items.
    Args:
        recommended_items (DataFrame): DataFrame containing food recommendations
        selected_deficiencies (list): List of nutrient deficiencies
    Returns:
        list: Formatted list of recommendations grouped by main and sub categories
    """
    formatted_data = {}

    # Iterate through each row in the DataFrame
    for _, row in recommended_items.iterrows():
        main_cat = row['main_category']
        sub_cat = row['sub_category']
        food_name = row['description']
        nutrient_values = {nutrient: row[nutrient] for nutrient in selected_deficiencies}  # Extract deficiencies

        # Create main category if it doesn't exist
        if main_cat not in formatted_data:
            formatted_data[main_cat] = {}

        # Create sub category if it doesn't exist
        if sub_cat not in formatted_data[main_cat]:
            formatted_data[main_cat][sub_cat] = []

        # Add food name and nutrients under the sub-category
        formatted_data[main_cat][sub_cat].append({
            "food_name": food_name,
            "nutrients": nutrient_values
        })

    # Convert structured data into a list format
    formatted_list = []
    for main_cat, sub_cats in formatted_data.items():
        main_category = {
            "main_category": main_cat,
            "sub_categories": []
        }

        for sub_cat, foods in sub_cats.items():
            sub_category = {
                "name": sub_cat,
                "foods": []  # List of food items
            }
            for food in foods:
                sub_category["foods"].append({
                    "food_name": food["food_name"],
                    "nutrients": food["nutrients"]
                })

            main_category["sub_categories"].append(sub_category)

        formatted_list.append(main_category)

    return formatted_list  # Ensure it returns a list of dictionaries


    
    

def recommend_food(deficiencies, category=None):
    #Recommend food items based on a user's nutrient deficiencies, with optional category filtering.
    df, knn,original_df = load_data()
    print("from recommend_food: deficiencies: ", deficiencies, "category: ", category)
    selected_deficiencies=deficiencies
    # Define nutrients inside the function
    nutrients = ['calcium', 'potassium', 'zinc', 'vitamin_C', 'iron', 'magnesium', 'phosphorus', 'sodium', 'copper',
                 'vitamin_E', 'thiamin', 'riboflavin', 'cholesterol', 'Niacin', 'vitamin_B_6', 'choline_total',
                 'vitamin_A', 'vitamin_K', 'folate_total', 'vitamin_B_12', 'selenium', 'vitamin_D']
    
    if not isinstance(deficiencies, list):
        return "Invalid input. Provide a list of deficiencies."
    
    # Check for invalid deficiencies
    invalid_nutrients = [d for d in deficiencies if d not in nutrients]
    if invalid_nutrients:
        return f"Invalid deficiencies: {', '.join(invalid_nutrients)}. Choose from: {', '.join(nutrients)}"
       
    # Create a query vector: 1 for deficient nutrients, 0 for others
    sample = np.zeros(len(nutrients))
    for deficiency in deficiencies:
        sample[nutrients.index(deficiency)] = 1
    
    # Use KNN to get recommendations
    distances, indices = knn.kneighbors([sample])
    
    # Extract recommendations from the full dataset first
    #recommended_items = df.iloc[indices[0] % len(df)]  # Ensure valid indices
    
    #getting original values
    #original_df= df
    #scaler = MinMaxScaler()
    #original_df[nutrients]= scaler.inverse_transform(df[nutrients])

   # Extract recommendations from the original dataset first
    #recommended_items = original_df.iloc[indices[0]][['description','main_category','sub_category']+ deficiencies] # Ensure valid indices
    recommended_items = original_df.iloc[indices[0] % len(df)] 
    #print(recommended_items)
    #print(recommended_items2)
    #print('columns in orignal df',original_df.columns)

    # If category is 'Veg', filter the recommendations
    if category == 'Veg':
        recommended_items = recommended_items[recommended_items['main_category'] == category]
    
    if recommended_items.empty:
        return {"error": f"No valid food recommendations available for the selected category: {category}"}
    
    formatted_recommendations = format_recommendations(recommended_items,selected_deficiencies)
    return formatted_recommendations 