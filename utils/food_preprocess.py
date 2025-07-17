import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import re

# Load data
df = pd.read_excel("data/food_data.xlsx")
df.rename(columns={'vitamin_K_ UG': 'vitamin_K_UG', 'vitamin D _UG' : 'vitamin_D_UG', 'vitamin B_12_UG' : 'vitamin_B_12_UG'}, inplace=True)
df.fillna(0, inplace=True)

# Cleaning
df['description'] = df['description'].apply(lambda x: x[:-5] if x.endswith(", raw") else x)
df['main_category'] = df['main_category'].apply(lambda x: "Veg" if x == "Non Alcoholic" else x)
df['description'] = df['description'].apply(lambda x: re.sub(r"^Game meat,\s*", "", x).capitalize())



in_mg = ['calcium_MG', 'potassium_MG', 'zinc_MG', 'vitamin_C_MG', 'iron_MG', 'magnesium_MG', 'phosphorus_MG',
          'sodium_MG', 'copper_MG', 'vitamin_E_MG', 'thiamin_MG', 'riboflavin_MG', 'cholesterol_MG', 'Niacin_MG', 
          'vitamin_B_6_MG', 'choline_total_MG']

in_grams = ['carbohydrate_G', 'water_G', 'total_lipid_fat_G', 'protein_G', 'fatty_acids_total_saturated_G', 
            'fiber_total_dietary_G','total_sugars_G', 'fatty_acids_total_monounsaturated_G', 
            'fatty_acids_total_polyunsaturated_G' ]

in_ug = ['vitamin_A_UG', 'vitamin_K_UG', 'folate_total_UG', 'vitamin_B_12_UG', 'selenium_UG', 'vitamin_D_UG' ]

others = ['description', 'sub_category', 'main_category', 'category', 'energy (kJ)']

# Convert units (grams to milligrams, micrograms to milligrams)
df[in_grams] = df[in_grams] * 1000
df[in_ug] = df[in_ug] / 1000

df.columns = df.columns.str.replace(r'_(UG|MG|G)$', '', regex=True)

# Select relevant columns (nutrients for modeling)
nutrients = ['calcium', 'potassium', 'zinc', 'vitamin_C', 'iron', 'magnesium', 'phosphorus','sodium', 'copper',
              'vitamin_E', 'thiamin', 'riboflavin', 'cholesterol', 'Niacin', 'vitamin_B_6', 'choline_total',
              'vitamin_A', 'vitamin_K', 'folate_total', 'vitamin_B_12', 'selenium', 'vitamin_D' ]

df.to_csv("data/original/food.csv",index=False) # saving after column names have changed
#print(df.columns)

# Normalize nutrient data using MinMaxScaler
scaler = MinMaxScaler()
df[nutrients] = scaler.fit_transform(df[nutrients])

# Save the processed data
df.to_csv("data/preprocessed/food.csv", index=False)
print("✅ Data preprocessing complete! File saved as 'processed_food_data.csv'.")
