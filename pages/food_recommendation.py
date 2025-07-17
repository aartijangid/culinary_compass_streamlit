import pandas as pd
import streamlit as st
from datetime import date
import requests
from utils.food_recommend import recommend_food

API_BASE_URL = "http://127.0.0.1:8000"
SAVE_HISTORY_URL = f"{API_BASE_URL}/save-history/"
GET_RECOMMENDATION_URL = f"{API_BASE_URL}/get-recommendation/"

st.set_page_config(page_title="Food Recommendation System", layout="wide")
##logo
#st.sidebar.image("assets/logo.png", width=150)

# Add this CSS for the page header
st.markdown("""
    <style>
        .main > div:first-child {
            padding-top: 0.5rem !important;
        }
        .block-container {
            padding-top: 1.25rem !important;
            padding-bottom: 0 !important;
            margin-top: 0 !important;
        }
        h1 {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        /* Style for the header container */
        .header-container {
            display: flex;
            align-items: left;
            padding-top: 1rem;
            margin: 0;
            padding-bottom: 0.5rem;
        }
        .header{
            font-size: 2rem;
            font-weight: 600;
            color: #262730;
        }
        /* Style for the header icon */
        .header-icon {
            font-size: 2rem;
            margin-right: 0.3rem;
        }   
        .nutrient-info {
            text-align: right;
            color: #666666;
            font-size: 0.9rem;
            font-style: italic;
            opacity: 0.8;
        }
        .user-note {
            text-align: right;
            color: #1f77b4;  /* A nice blue color */
            font-size: 0.85rem;
            font-style: italic;
            border-radius: 4px;
        }
        .recommendation-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #262730;
            margin-bottom: 0.2rem;
            padding-bottom: 0.2rem;
            border-bottom: 2px solid #f0f2f6;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        /* Style for the page link button */
        [data-testid="stPageLink"] {
            background-color: transparent;
            border: 1px solid #e0e0e0;  
            padding: 0.5rem 1rem;
            border-radius: 0.25rem;
            color: #262730 !important; 
            font-weight: 500;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            margin-top: 1rem;
            cursor: pointer;
        }

        [data-testid="stPageLink"]:hover {
            background-color: transparent; 
            border-color: #ff4b4b; 
            color: #ff4b4b !important; 
        }

        [data-testid="stPageLink"] p {
            color: inherit !important;
            margin: 0;
            font-size: 1rem;
            font-family: 'Source Sans Pro', sans-serif;
        }

        [data-testid="stPageLink"]:hover p {
            color: #ff4b4b !important; 
        }
    </style>
""", unsafe_allow_html=True)

# st.markdown("""
#         <div class="header-container">
#             <span class="header-icon">🍽️</span>
#             <h1>Culinary Compass <span style="font-size: 1.5rem; font-weight: 900;">- Flavor Meets Wellness</span></h1>
#         </div> 
#     """, unsafe_allow_html=True)

def load_data():
    """Load processed food data and extract unique categories."""
    df = pd.read_csv("data/preprocessed/food.csv")
    original_df = pd.read_csv("data/original/food.csv")
    categories = df["main_category"].unique().tolist()
    deficiencies = [
        'vitamin_D', 'calcium',  'vitamin_C', 'iron', 'potassium', 
        'vitamin_B_6', 'vitamin_B_12', 'vitamin_A', 'riboflavin', 'vitamin_E', 'folate_total',
        'vitamin_K', 'zinc', 'magnesium','sodium',  'thiamin', 'Niacin',  'selenium'
    ]
    return df, original_df, categories, deficiencies

def calculate_bmi(weight, height):
    """Calculate and categorize BMI."""
    bmi = round(weight / (height ** 2), 2)
    if bmi < 18.5:
        category = "Underweight - Increase nutrient-dense meals."
    elif 18.5 <= bmi < 24.9:
        category = "Normal weight - Maintain a balanced diet and exercise."
    elif 25 <= bmi < 29.9:
        category = "Overweight - Focus on portion control and active lifestyle."
    else:
        category = "Obese - Consider a structured diet and exercise plan."
    return bmi, category

def get_recommendation(preference, deficiencies):
    # try:
    #     response = requests.get(
    #         GET_RECOMMENDATION_URL,
    #         json={"food_preference": preference, "deficiencies": deficiencies},
    #         timeout=5
    #     )
    #     if response.status_code == 200:
    #         return response.json()["recommendation"]
    #     else:
    #         st.error(f"API Error: {response.text}")
    #         return None
    # except requests.exceptions.RequestException as e:
    #     st.error(f"API Connection Error: {str(e)}")
    #     return None
    recommendations = recommend_food(deficiencies, preference)
    return recommendations

def save_to_api(user_data: dict, recommendation: list):
    """Save user data and recommendations to API."""
    try:
        # Convert recommendation list to formatted string
        recommendation_str = ""
        for main_cat in recommendation:
            recommendation_str += f"\n{main_cat['main_category']}\n"
            for sub_cat in main_cat['sub_categories']:
                recommendation_str += f"{sub_cat['name']}\n"
                for food in sub_cat['foods']:
                    food_name = food['food_name']
                    nutrients = food['nutrients']
            
                    # Format nutrient values as a comma-separated string
                    nutrient_str = ", ".join([f"{key}: {value}" for key, value in nutrients.items()])
            
                    # Append food name with its nutrients
                    recommendation_str += f"  - {food_name} ({nutrient_str})\n"
                    #recommendation_str += f"  - {food}\n"
                    
        # Prepare data to match UserHistory model
        history_data = {
            "name": str(user_data['name']),
            "age": int(user_data['age']),
            "gender": str(user_data['gender']),
            "height": float(user_data['height']),
            "weight": float(user_data['weight']),
            "bmi": float(user_data['bmi']),
            "bmi_category": str(user_data['bmi_category']),
            "food_preference": str(user_data['food_preference']),
            "deficiencies": list(user_data['deficiencies']),
            "recommendations": recommendation_str
        }
        
        # Make API call to save history
        response = requests.post(SAVE_HISTORY_URL, json=history_data)
        if response.status_code == 200:
            print("History saved successfully!")
        else:
            print(f"Failed to save history. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            st.error("Failed to save history.")
            
    except Exception as e:
        print(f"Error saving to API: {str(e)}")
        st.error("Failed to save data to API. Please try again.")

def display_selected_foods(selected_foods):
    """
    Display selected foods in styled capsules within a scrollable container
    """
    st.markdown("""
        <style>
            .selected-foods-container {
                max-height: 200px;
                overflow-y: auto;
                border: 1px solid #f0f2f6;
                border-radius: 0.5rem;
                padding: 0.5rem;
                background-color: white;
                margin: 0.3rem 0;
                margin-bottom: 0.5rem;
                scrollbar-width: thin;
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }
            .selected-foods-container::-webkit-scrollbar {
                width: 6px;
                background-color: #f0f2f6;
            }
            .selected-foods-container::-webkit-scrollbar-thumb {
                background-color: #ccc;
                border-radius: 3px;
            }
            .selected-foods-header {
                display: flex;
                font-size: 1rem;
                font-weight: 600;
                font-size: 1.3em;
                font-weight: bold;
                color: #262730;
            }
            .food-capsule {
                display: inline-flex;
                align-items: center;
                font-size: 0.85rem;
                color: #262730;
                background-color: #e8ecf0;
                border-radius: 1rem;
                padding: 0.35rem 0.8rem;
                font-family: 'Source Sans Pro', sans-serif;
                transition: all 0.2s;
            }
            .food-capsule:hover {
                background-color: #e1e4eb;
                transform: translateY(-1px);
            }
        </style>
    """, unsafe_allow_html=True)

    # Display header
    if selected_foods:
        st.markdown('<div class="selected-foods-header">Selected Foods:</div>', unsafe_allow_html=True)
        # Create container with capsule items
        foods_html = '<div class="selected-foods-container">'
        for food in selected_foods:
            foods_html += f'<div class="food-capsule">{food}</div>'
        foods_html += '</div>'
        # Display the container
        st.markdown(foods_html, unsafe_allow_html=True)

def main():
    """Main function to run the Streamlit app."""
    # Place the logo at the top-right
    # Create columns for title + logo
    col1, col2 = st.columns([4, 2])  # Adjust column width

    with col1:
        st.markdown("""
        <div class="header-container"></div> 
        """, unsafe_allow_html=True)
        st.image("assets/CulinaryCompass.png")  # logo with banner
    with col2:
        st.markdown("""
        <div class="header-container"></div> 
        """, unsafe_allow_html=True)
        #st.title(f"Culinary Compass : Flavor Meets Wellness | {date.today().year}")  # Main title

    # Clear session state when the page is loaded
    if 'user_data' not in st.session_state:
        st.session_state['user_data'] = None
    if 'recommendation' not in st.session_state:
        st.session_state['recommendation'] = None
    if 'selected_foods' not in st.session_state:
        st.session_state['selected_foods'] = set()
    if 'previous_preference' not in st.session_state:
        st.session_state['previous_preference'] = None
    if 'previous_deficiencies' not in st.session_state:
        st.session_state['previous_deficiencies'] = []

    # Load Data
    df, original_df, categories, deficiencies = load_data()

    # Sidebar Input
    
    st.sidebar.header("User Information")
    name = st.sidebar.text_input("Enter your name:")
    age = st.sidebar.number_input("Age:", min_value=1, value=25)
    gender = st.sidebar.radio("Gender:", ("Male", "Female", "Other"))
    
    col1, col2 = st.sidebar.columns(2)
    weight = col1.number_input("Weight (kg):", min_value=1.0, value=50.0)
    height = col2.number_input("Height (m):", min_value=0.5, max_value=2.5, value=1.50)

    # Get current food preference selection
    food_preference = st.sidebar.selectbox("Diet Preference:", categories)
    
    # Check if food preference changed
    if food_preference != st.session_state['previous_preference']:
        # Clear session state values
        st.session_state['user_data'] = None
        st.session_state['recommendation'] = None
        st.session_state['selected_foods'] = set()
        # Update the previous preference
        st.session_state['previous_preference'] = food_preference
        # Force a rerun to update the UI
        st.rerun()

    # st.sidebar.write("Select Deficiencies:")
    # cols = st.sidebar.columns(2)
    
    # # Check if any deficiency checkbox was clicked
    # any_deficiency_clicked = False
    # selected_deficiencies = []
    
    # # Handle deficiency selection and detect changes
    # for i, d in enumerate(deficiencies):
    #     # Create checkbox in appropriate column
    #     was_selected = d in st.session_state.get('previous_deficiencies', [])
    #     is_selected = cols[i % 2].checkbox(d, key=f"def_{d}", value=was_selected)
        
    #     # Check if this deficiency's state changed
    #     if is_selected != was_selected:
    #         any_deficiency_clicked = True
        
    #     # Add to selected deficiencies if checked
    #     if is_selected:
    #         selected_deficiencies.append(d)
    
    # # Clear session state if any deficiency was clicked
    # if any_deficiency_clicked:
    #     # Store current deficiency selection before clearing
    #     st.session_state['previous_deficiencies'] = selected_deficiencies
        
    #     # Clear other session state values
    #     st.session_state['user_data'] = None
    #     st.session_state['recommendation'] = None
    #     st.session_state['selected_foods'] = set()
        
    #     # Force a rerun to update the UI
    #     st.rerun()

    ##added
        
    # Maximum number of selections allowed
    max_selections = 3

    st.sidebar.write("Select Deficiencies:")
    cols = st.sidebar.columns(2)

    # Track previously selected deficiencies from session state
    previous_deficiencies = st.session_state.get('previous_deficiencies', [])

    # Track the selected deficiencies
    selected_deficiencies = previous_deficiencies.copy()

    # Handle deficiency selection and detect changes
    any_deficiency_clicked = False

    for i, d in enumerate(deficiencies):
        # Was this deficiency previously selected?
        was_selected = d in previous_deficiencies

        # Disable all checkboxes if 3 deficiencies are selected, allow changes if one is deselected
        is_disabled = len(selected_deficiencies) >= max_selections and not was_selected

        # Create checkbox (disabled if needed)
        is_selected = cols[i % 2].checkbox(d, key=f"def_{d}", value=was_selected, disabled=is_disabled)

        # Check if this deficiency's state changed
        if is_selected != was_selected:
            any_deficiency_clicked = True

        # Add to selected deficiencies if checked and not already selected
        if is_selected and d not in selected_deficiencies:
            selected_deficiencies.append(d)

        # Remove from selected deficiencies if unchecked
        elif not is_selected and d in selected_deficiencies:
            selected_deficiencies.remove(d)

    # Store current deficiency selection in session state if any change was detected
    if any_deficiency_clicked:
        st.session_state['previous_deficiencies'] = selected_deficiencies

        # Optionally clear other session state values if you want to reset them
        st.session_state['user_data'] = None
        st.session_state['recommendation'] = None
        st.session_state['selected_foods'] = set()

        # Force a rerun to update the UI
        st.rerun()


    #######

    if st.sidebar.button("Get Recommendation"):
        if not name:
            st.warning("Please enter your name before proceeding.")
            return

        # Clear session state when the "Get Recommendation" button is clicked
        clear_session()

        bmi, bmi_category = calculate_bmi(weight, height)
        recommendation = get_recommendation(food_preference, selected_deficiencies)

        # Save user data and recommendation to session state
        st.session_state['user_data'] = {
            "name": name,
            "age": age,
            "gender": gender,
            "weight": weight,
            "height": height,
            "bmi": bmi,
            "bmi_category": bmi_category,
            "food_preference": food_preference,
            "deficiencies": selected_deficiencies
        }
        st.session_state['recommendation'] = recommendation

        # Save to API
        save_to_api(st.session_state['user_data'], recommendation)

    # Display User Info and Recommendations if available
    if not st.session_state['user_data']:
        st.markdown(
                """
                <div style="
                    padding: 10px; 
                    background-color: #ffebcc; 
                    border-radius: 5px;
                    border-left: 5px solid #ff9800;
                    font-size: 18px;
                    font-weight: bold;
                    color: #8a6d3b;
                    margin-bottom: 10px;">
                     Enter details & select deficiency to get recommendations.
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.image("assets/wellness.jpg", caption="Flavor meets wellness!", use_container_width=True)
    else: 
        user_data = st.session_state['user_data']
        st.subheader(f"Hello, {user_data['name']}!")
        st.write(f"**Age:** {user_data['age']}  |  **Gender:** {user_data['gender']}")
        st.write(f"**BMI:** {user_data['bmi']}  |  **Category:** {user_data['bmi_category']}")

        if user_data['deficiencies']:
            st.write(f"**Deficiencies:** {', '.join(user_data['deficiencies'])}")


        if st.session_state['recommendation']:
            st.markdown("""
                <div class="recommendation-header">
                    Recommended Recipes Based on Your Selection
                </div>
            """, unsafe_allow_html=True)
            #st.markdown('<div class="nutrient-info">Food nutrients are measured in milligrams per 100 grams (mg/100g)</div>', unsafe_allow_html=True)
            st.markdown('<div class="user-note">Select the foods you want to find personalized recipes for.</div>', unsafe_allow_html=True)
            for category in st.session_state['recommendation']:
                #st.markdown(f"### {category['main_category']}")  # Main category as header
                for sub_cat in category['sub_categories']:
                    with st.expander(f"**{sub_cat['name']}** ({len(sub_cat['foods'])} items)"):
                    # Split into two columns    
                        col1, col2 = st.columns(2)
                        unique_foods = list(set(food["food_name"] for food in sub_cat["foods"]))

                        # Display food items with nutrients and checkbox in the same loop
                        for i, food_name in enumerate(unique_foods):
                            col = col1 if i % 2 == 0 else col2  

                        # Now display the food name and its nutrients
                            for food in sub_cat["foods"]:
                                if food["food_name"] == food_name:
                                    nutrient_values = food["nutrients"]
                                    nutrient_str = ", ".join([f"{nutrient}: {value}" for nutrient, value in nutrient_values.items()])
                                    # Display food name and nutrients **before the checkbox**
                                    #st.write(f"**{food_name}:** {nutrient_str}")

                        # Display checkbox for selecting food
                           # selected = col.checkbox(food_name + ' ' + nutrient_str,key=f"food_{food_name}", value=food_name in st.session_state["selected_foods"])
                           
                           # # Convert nutrient_str into a dictionary
                            nutrient_dict = dict(item.split(": ") for item in nutrient_str.split(", "))

                            # Convert string values to floats
                            nutrient_dict = {key: float(value) for key, value in nutrient_dict.items()}
                            
                            ##another
                           
                            nutrient_display = "<div style='display: flex; justify-content: start;'>"  # Start the flex container for horizontal layout

                            for nutrient, value in nutrient_dict.items():

                                max_value = max(original_df[nutrient])
                                #st.write(max_value)
                                # Calculate percentage for the circular progress bar, ensuring it doesn't exceed 100%
                                percentage = int((value / max_value) * 100)  # Limit percentage to 100
                                
                                # Create a small circle (30px by 30px) with progress bar, no numbers
                                circle_html = f"""
                                <div style="width: 20px;  height: 20px; border-radius: 50%; background: conic-gradient(#ff5900 {percentage}%, #d3d3d3 {percentage}%); margin-right: 10px;"></div>
                                """
                                # Append the nutrient and its corresponding circle to the display string
                                nutrient_display += f"<div style='display: inline-block; font-size:12px;font-color: #82848f;text-align: center; margin-right: 15px;'><b>{nutrient.capitalize()}&nbsp;&nbsp;</b>{circle_html}</div>"

                            nutrient_display += "</div>"  # Close the flex container

                            # Display food name and nutrient progress indicators in a single line
                            #st.markdown(f"**{food_name}** <br>{nutrient_display}", unsafe_allow_html=True)

                            with col:
                                # Use columns inside the main column to align checkbox & nutrients in one row
                                c1, c2 = st.columns([3, 2])  # Adjust ratio for spacing
                                with c1:
                                    selected = st.checkbox(f"{food_name}", key=f"food_{food_name}")
                                with c2:
                                    st.markdown(nutrient_display, unsafe_allow_html=True) # Nutrient indicators in col
                            # Checkbox to select food (optional, this doesn't affect nutrient display)
                            # selected = st.checkbox(f"Select {food_name}", key=f"food_{food_name}")
                            # st.markdown(f"{nutrient_display}", unsafe_allow_html=True)
                            


                    # Update session state based on user selection
                            if selected:
                                st.session_state["selected_foods"].add(food_name)
                            else:
                                st.session_state["selected_foods"].discard(food_name)

        
                            
            # # Show selected foods
            # st.subheader("Your Selected Foods:")
            # if st.session_state["selected_foods"]:
            #     st.write(", ".join(st.session_state["selected_foods"]))
            # else:
            #     st.write("No foods selected yet.")

            # display the selected foods from the food recommendation page 
            if 'selected_foods' in st.session_state:
                display_selected_foods(st.session_state.selected_foods)

        # Navigation to recipe selection
        if st.session_state["selected_foods"]:
            st.page_link("pages/recipes_recommendation.py", label="Select Recipes For These Foods")

    # Footer
    st.markdown("---")
    
    st.caption(f"Culinary Compass : Flavor Meets Wellness | {date.today().year}")
    
def clear_session():
    st.session_state['user_data'] = None
    st.session_state['recommendation'] = None
    st.session_state['selected_foods'] = set()

if __name__ == "__main__":
    main()