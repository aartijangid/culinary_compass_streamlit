import pandas as pd
from sklearn.neighbors import NearestNeighbors
import pickle

# Load processed food data
df = pd.read_csv("data/preprocessed/food.csv")


# Define features (nutrient values)
nutrients = ['calcium', 'potassium', 'zinc', 'vitamin_C', 'iron', 'magnesium', 'phosphorus','sodium', 'copper',
              'vitamin_E', 'thiamin', 'riboflavin', 'cholesterol', 'Niacin', 'vitamin_B_6', 'choline_total',
              'vitamin_A', 'vitamin_K', 'folate_total', 'vitamin_B_12', 'selenium', 'vitamin_D' ]


# Prepare the feature matrix for KNN (using nutrients only)
X = df[nutrients]

# Initialize and train the KNN model
knn = NearestNeighbors(n_neighbors=40, metric='euclidean')
knn.fit(X)

# Save the trained model
with open("models/knn_model.pkl", "wb") as model_file:
    pickle.dump(knn, model_file)

print("✅ KNN model trained and saved as 'knn_model.pkl'.")
