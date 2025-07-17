from recipes_recommend import recommend_recipes
import pickle

# Step 7: User input for testing
user_nutrients = {
    "Calories": 500, "FatContent": 20, "SaturatedFatContent": 5,
    "CholesterolContent": 10, "SodiumContent": 500, "CarbohydrateContent": 50,
    "FiberContent": 10, "SugarContent": 10, "ProteinContent": 30
}

user_ingredients = [ "Egg, whole, raw, frozen, salted, pasteurized", "Cheese, American, restaurant",
                    "Cheese, cotija, solid", "Crustaceans, crab, alaska king, raw",
                      "Mollusks, clam, mixed species, raw",  "Seaweed, wakame, raw",
                    "Cream cheese, full fat, block"]
# Define the diet preference
diet_preference = "Non-veg"# You can set this to "Vegetarian", "Non-Vegetarian", or "Any" based on user input

# Step 8: Get recommendations
recommendations = recommend_recipes(user_nutrients, user_ingredients, diet_preference)

# Step 9: Display results
for recipe in recommendations:
    print(f"Name: {recipe['Name']}\nImage: {recipe['Images']}\nInstructions: {recipe['RecipeInstructions']}\n{'-'*50}")