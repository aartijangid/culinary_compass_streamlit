"""
Streamlit web application for analyzing nutrient deficiency data.

This application provides interactive visualizations for exploring:
1. Gender-wise nutrient deficiencies
2. Top symptoms for each deficiency
3. Disease analysis based on selected deficiencies
"""

# Standard library imports
import os

# Third-party imports
import pandas as pd
import plotly.express as px
import streamlit as st

# Constants
DATA_PATH = "data/EDA/deficiency_data.xlsx"
DISEASE_COLUMNS = [
    'Age', 'Gender', 'Diet Type', 'Living Environment', 'Night Blindness',
    'Dry Eyes', 'Bleeding Gums', 'Fatigue', 'Tingling Sensation',
    'Low Sun Exposure', 'Reduced Memory Capacity', 'Shortness of Breath',
    'Loss of Appetite', 'Fast Heart Rate', 'Brittle Nails', 'Weight Loss',
    'Reduced Wound Healing Capacity', 'Skin Condition', 'Predicted Deficiency'
]

def setup_page():
    st.set_page_config(page_title="Deficiency Analysis", layout="wide")
    
    # Add CSS styling
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
            .header-container {
                display: flex;
                align-items: left;
                padding-top: 1rem;
                margin: 0;
                padding-bottom: 0.5rem;
            }
            .header {
                font-size: 2rem;
                font-weight: 600;
                color: #262730;
            }
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
                color: #1f77b4;
                font-size: 0.85rem;
                font-style: italic;
                border-radius: 4px;
            }
            .recommendation-header {
                font-size: 1.3rem;
                font-weight: 600;
                color: #262730;
                margin-bottom: 0.2rem;
                padding-bottom: 0.2rem;
                border-bottom: 2px solid #f0f2f6;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .stMarkdown div.css-1629p8f.e16nr0p31 h3 {
                color: #ff5900;  
                font-weight: 600;
            }
        </style>
    """, unsafe_allow_html=True)

def create_header():
    col1, col2 = st.columns([4, 2])
    with col1:
        st.markdown("""
        <div class="header-container"></div> 
        """, unsafe_allow_html=True)
        st.image("assets/CulinaryCompass.png")
    with col2:
        st.markdown("""
        <div class="header-container"></div> 
        """, unsafe_allow_html=True)

def load_data(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def plot_gender_deficiencies(df: pd.DataFrame) -> None:
    st.markdown("""
        <div class="recommendation-header">
            Gender-wise Nutrient Deficiencies
        </div>
    """, unsafe_allow_html=True)
    
    # Count occurrences of each deficiency per gender
    df_counts = df.groupby(["Predicted Deficiency", "Gender"]).size().reset_index(name="Count")
    df_counts = df_counts.sort_values(by="Count", ascending=False)
    
    # Define custom color scheme for genders
    color_map = {
        'Male': '#A4C1F3',  
        'Female': '#FD9F6E'
    }
    
    # Create interactive bar chart
    fig = px.bar(
        df_counts,
        x="Predicted Deficiency",
        y="Count",
        color="Gender",
        barmode="group",
        color_discrete_map=color_map,
        height=400  # Set consistent height
    )
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=30, b=0)  # Adjust margins
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_disease_analysis(df: pd.DataFrame) -> None:
    """Create and display disease analysis visualization.
    
    Args:
        df (pd.DataFrame): Input data containing disease information
    """
    st.markdown("""
        <div class="recommendation-header">
            Deficiency & Disease Analysis
        </div>
    """, unsafe_allow_html=True)
    
    # Add custom CSS for multiselect colors
    st.markdown("""
        <style>
            .stMultiSelect [data-baseweb="tag"] {
                background-color: #C0A6CA !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Multiselect filter for deficiencies
    selected_deficiencies = st.multiselect(
        "Select nutrient deficiencies:",
        df["Predicted Deficiency"].unique(),
        default=df["Predicted Deficiency"].unique()
    )
    
    # Filter dataset based on selected deficiencies
    filtered_df = df[df["Predicted Deficiency"].isin(selected_deficiencies)]
    
    # Compute gender-wise disease counts
    columns_to_drop = ["Predicted Deficiency", "Age", "Diet Type", "Living Environment", "Low Sun Exposure"]
    genderwise_counts = filtered_df.drop(columns=columns_to_drop).groupby("Gender").sum().reset_index()
    
    # Melt DataFrame for Plotly
    melted_df = genderwise_counts.melt(
        id_vars=["Gender"],
        var_name="Disease",
        value_name="Count"
    )
    
    # Define custom color scheme for genders
    color_map = {
        'Male': '#A4C1F3',  # light blue for male
        'Female': '#FD9F6E'  # orange for female
    }
    
    # Create interactive bar chart
    fig = px.bar(
        melted_df,
        x="Disease",
        y="Count",
        color="Gender",
        barmode="group",
        color_discrete_map=color_map,
        labels={"Count": "Number of Cases", "Disease": "Disease"},
        text="Count"
    )
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_symptoms_deficiencies(df: pd.DataFrame) -> None:
    """Create and display visualization of top symptoms for each deficiency."""
    st.markdown("""
        <div class="recommendation-header">
            Top 5 Symptoms for Each Deficiency
        </div>
    """, unsafe_allow_html=True)
    
    # Define symptom columns (excluding non-symptom columns)
    symptom_columns = [
        'Night Blindness', 'Dry Eyes', 'Bleeding Gums', 'Fatigue', 
        'Tingling Sensation', 'Reduced Memory Capacity', 'Shortness of Breath',
        'Loss of Appetite', 'Fast Heart Rate', 'Brittle Nails', 'Weight Loss',
        'Reduced Wound Healing Capacity', 'Skin Condition'
    ]
    
    # Define custom color scheme for deficiencies
    color_map = {
        'Vitamin A': '#FD9F6E',  # orange
        'Vitamin C': '#CBCE54',  # yellow-green
        'Vitamin B12': '#FDD526',  # yellow
        'Zinc': '#A4C1F3',  # light blue
        'Vitamin D': '#B0927A',  # brown
        'Iron': '#C0A6CA',  # purple
    }
    
    # Create a dictionary to store symptom counts for each deficiency
    deficiency_symptoms = {}
    
    # Calculate symptom frequencies for each deficiency
    for deficiency in df['Predicted Deficiency'].unique():
        deficiency_df = df[df['Predicted Deficiency'] == deficiency]
        # Convert symptom columns to numeric and sum
        symptom_counts = deficiency_df[symptom_columns].apply(pd.to_numeric, errors='coerce').sum()
        # Convert to DataFrame for proper sorting
        symptom_df = pd.DataFrame({
            'Symptom': symptom_counts.index,
            'Count': symptom_counts.values.astype(int)  # Convert to integer
        })
        # Sort by count and get top 5
        top_symptoms = symptom_df.nlargest(5, 'Count')
        deficiency_symptoms[deficiency] = top_symptoms
    
    # Create a DataFrame for visualization
    plot_data = []
    for deficiency, symptoms_df in deficiency_symptoms.items():
        for _, row in symptoms_df.iterrows():
            plot_data.append({
                'Deficiency': deficiency,
                'Symptom': row['Symptom'],
                'Count': int(row['Count'])  # Ensure Count is integer
            })
    
    plot_df = pd.DataFrame(plot_data)
    
    # Create interactive bar chart
    fig = px.bar(
        plot_df,
        x='Count',
        y='Symptom',
        color='Deficiency',
        orientation='h',
        # title='Top 5 Symptoms for Each Deficiency',
        color_discrete_map=color_map,
        labels={'Count': 'Number of Cases', 'Symptom': 'Symptom'},
        height=500
    )
    
    # Update layout for better readability
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.85,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_diet_deficiencies(df: pd.DataFrame) -> None:
    st.markdown("""
        <div class="recommendation-header">
            Deficiency Prevalence by Diet Type
        </div>
    """, unsafe_allow_html=True)
    
    # Group data by diet type and deficiency
    diet_deficiency = df.groupby(['Diet Type', 'Predicted Deficiency']).size().reset_index(name='Count')
    
    # Define custom color scheme for deficiencies
    color_map = {
        'Vitamin A': '#FD9F6E',  # orange
        'Vitamin C': '#CBCE54',  # yellow-green
        'Vitamin B12': '#FDD526',  # yellow
        'Zinc': '#A4C1F3',  # light blue
        'Vitamin D': '#B0927A',  # brown
        'Iron': '#C0A6CA'  # purple
    }
    
    # Create interactive bar chart
    fig = px.bar(
        diet_deficiency,
        x='Diet Type',
        y='Count',
        color='Predicted Deficiency',
        barmode='group',
        color_discrete_map=color_map,
        labels={'Count': 'Number of Cases', 'Diet Type': 'Diet Type', 'Predicted Deficiency': 'Predicted Deficiency'},
        height=400  # Set consistent height
    )
    
    # Update layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            title_text='',
            orientation="h",
            yanchor="bottom",
            y=1.15,  # Adjusted for better alignment
            xanchor="left",
            x=0,
            bgcolor='rgba(255, 255, 255, 0.8)'
        ),
        margin=dict(t=100, b=0)  # Adjust margins
    )
    
    # Update bar opacity
    fig.update_traces(opacity=0.8)
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main function to run the Streamlit application."""
    # Setup page configuration and styling
    setup_page()
    
    # Create header
    create_header()
    
    # Main title with custom color
    st.markdown("<h3 style='color: #ff5900;'>Study on Hidden Hunger</h3>", unsafe_allow_html=True)
    
    # Load data
    df = load_data(DATA_PATH)
    if df.empty:
        return
    
    # Create a 2x2 grid layout
    col1, col2 = st.columns(2)
    
    # Display visualizations in first column of each row
    with col1:
        plot_gender_deficiencies(df)
    with col2:
        plot_diet_deficiencies(df)
    
    plot_disease_analysis(df)
    
    # Footer
    st.markdown("---")
    st.caption("Culinary Compass : Flavor Meets Wellness")

if __name__ == "__main__":
    main()