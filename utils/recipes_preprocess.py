import pandas as pd

# Load dataset
df = pd.read_csv("data/recipes.csv")
df =df.iloc[0:20000]
#df =df.iloc[0:3000] # For testing purposes

# convert columns in mg to g
in_mg = ['CholesterolContent', 'SodiumContent']

in_grams = ['ProteinContent', 'FatContent', 'CarbohydrateContent', 'saturatedFatContent', 'FiberContent', 'SugarContent']

# Convert units (grams to milligrams, micrograms to milligrams)
df[in_mg] = df[in_mg] / 1000

# Define non-vegetarian keywords
non_veg_keywords = set([
    # Meat & Poultry
    "chicken", "beef", "pork", "mutton", "lamb", "turkey", "duck", "quail", "goat", "veal",
    "rabbit", "boar", "venison", "bison", "kangaroo", "goose", "pheasant", "pigeon", "elk",

    # Processed Meat Products
    "bacon", "ham", "sausage", "pepperoni", "salami", "chorizo", "pastrami", "prosciutto",
    "mortadella", "hot dog", "jerky", "liverwurst", "blood sausage", "scrapple",

    # Seafood
    "fish", "tuna", "salmon", "trout", "cod", "haddock", "mackerel", "sardine", "anchovy",
    "herring", "catfish", "bass", "snapper", "grouper", "halibut", "swordfish", "mahi mahi",
    "flounder", "eel", "shark", "sturgeon", "tilapia", "tuna steaks", "swordfish steaks",

    # Shellfish
    "shrimp", "prawns", "crab", "lobster", "crawfish", "squid", "octopus", "scallops",
    "mussels", "clams", "oysters", "abalone", "conch",

    # Animal-Based Ingredients
    "egg", "eggs", "gelatin", "lard", "suet", "tallow", "bone broth", "fish sauce", "oyster sauce",
    "shrimp paste", "anchovy paste", "worcestershire sauce", "caviar", "roe", "squid ink",

    # Organ Meats (Offal)
    "liver", "kidney", "heart", "brain", "tripe", "sweetbreads", "tongue", "gizzards"
])

# Function to classify recipes
def classify_recipe(row):
    """
    Classifies a recipe as 'Vegetarian' or 'Non-Vegetarian' based on:
    - `RecipeIngredientParts`
    - `RecipeCategory`
    """
    # Extract ingredient list
    ingredients = str(row["RecipeIngredientParts"]).lower().replace('"', '').replace("c(", "").replace(")", "")
    ingredient_list = [ing.strip() for ing in ingredients.split(",")]

    # Extract category list
    categories = str(row["RecipeCategory"]).lower().replace('"', '').replace("c(", "").replace(")", "")
    category_list = [cat.strip() for cat in categories.split(",")]

    # Extract and clean keywords list
    keywords = str(row["Keywords"]).lower().replace('"', '').replace("c(", "").replace(")", "")
    keyword_list = [kw.strip() for kw in keywords.split(",")]

    # Extract recipe name
    recipe_name = str(row["Name"]).lower()

    # Combine all text sources to check for non-veg keywords
    all_text = ingredient_list + category_list + keyword_list + [recipe_name]

    # Check if any non-vegetarian keyword is found
    if any(any(non_veg in item for non_veg in non_veg_keywords) for item in all_text):
        return "Non-Veg"

    return "Veg"

# checking if all the columns have 0 as value
nutrient_columns = ["Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", 
                        "SodiumContent", "CarbohydrateContent", "FiberContent", "SugarContent", "ProteinContent"]

# separate rows where all nutrient values are 0
# This will create a DataFrame with only those rows
zero_nutrient_rows = df[nutrient_columns][(df[nutrient_columns] == 0).all(axis=1)]
# print(zero_nutrient_rows)

# print total number of rows where all nutrient values are 0
# zero_nutrient_row_count = (df[nutrient_columns] == 0).all(axis=1).sum()
# print(zero_nutrient_row_count)

# Remove rows where all nutrient values are 0
df = df[~(df[nutrient_columns] == 0).all(axis=1)]

# Apply classification
df["DietaryCategory"] = df.apply(classify_recipe, axis=1)

# Save processed data
df.to_csv("data/preprocessed/recipes.csv", index=False)
