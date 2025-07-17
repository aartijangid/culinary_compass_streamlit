from food_recommend import recommend_food


# Test the model with multiple deficiencies and category filtering
print("✅ Model trained. Testing recommendations...\n")

print("🥗 Vitamin C and Iron Deficiency (Veg Only):")
print(recommend_food(["vitamin_C", "iron"], category="Non-veg"))

print("\n🥩 Calcium and Magnesium Deficiency (Veg Only):")
print(recommend_food(["calcium", "magnesium"], category="Veg"))
