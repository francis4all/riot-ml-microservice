import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time 

# --- Page config ---
st.set_page_config(page_title="League of Legends Data Science", layout="wide")

st.markdown("""
    <style>
        /* Ajustar el título principal para que parezca logo */
        .block-container {padding-top: 1rem; padding-bottom: 0rem;}
        h1 {font-family: 'Helvetica Neue', sans-serif; color: #C8AA6E; text-align: center;} 
        h3 {color: #F0E6D2;}
        /* Estilizar las métricas */
        [data-testid="stMetricValue"] {font-size: 2.5rem; color: #0AC8B9;}
        [data-testid="stMetricLabel"] {font-size: 1rem; color: #A09B8C;}
    </style>
""", unsafe_allow_html=True)

st.title("League of Legends Champions: Data Science Hub")
st.markdown("### Machine Learning and Champions Analysis", unsafe_allow_html=True)

# --- load data ---    
# By default we assume we are in local
url = "http://localhost:8000/champions/"

# Try to connect to the 'web' container (Docker)
# We make 5 attempts (5 seconds) to give Django time to start
for i in range(5):
    try:
        # If this works, it means we are in Docker and Django is already awake
        requests.get("http://web:8000/champions/", timeout=1)
        url = "http://web:8000/champions/"
        print(f"Connected to Docker correctly (Attempt {i+1})")
        break
    except:
        # If it fails, we wait 1 second and try again
        print(f"Waiting for Django... (Attempt {i+1})")
        time.sleep(1)

@st.cache_data
def get_latest_version():
    try:
        response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
        versions = response.json()
        return versions[0]
    except Exception as e:
        st.error(f"Error obtaining latest version: {e}")
        return "14.1.1"

latest_version = get_latest_version()
st.sidebar.write(f"Latest version: {latest_version}")

@st.cache_data
def load_data():
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data['data'])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# --- Data preprocessing and visualization ---

if not df.empty:
    # --- Data cleaning ---
    df['title'] = df['title'].str.title()
    BASE_IMAGE_URL = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/champion/"
    df['image'] = BASE_IMAGE_URL + df['image']
    # --- fast KPIs ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Champions", len(df))
    with col2:
        st.metric("Average Health", f"{df['hp'].mean():.0f} HP")
    with col3:
        st.metric("Average Attack Damage", f"{df['attackdamage'].mean():.0f} AD")

    st.divider()

    st.subheader("AI Analysis: Champion Similarity Map (PCA)")
    st.markdown("""
    This map reduces all combat statistics to 2 dimensions.
    * **Close points:** Champions with mathematically similar playstyle.
    * **Colors:** Groups detected automatically by the K-Means algorithm.
    """)

    # Verify that the backend has sent the PCA coordinates
    if 'pca_x' in df.columns and 'cluster_label' in df.columns:

        if 'cluster_name' not in df.columns:
            df['cluster_name'] = "Clase " + df['cluster_label'].astype(str)
        
        # CUSTOM COLOR PALETTE (Vibrant)
        custom_colors = [
            "#0AC8B9", # Hextech Blue
            "#FF5555", # Danger Red
            "#F0E6D2", # Gold/Bone
            "#C389E8", # Void Purple
            "#50FA7B"  # Toxic Green
        ]

        fig = px.scatter(
            df,
            x='pca_x', 
            y='pca_y',
            color='cluster_name',
            color_discrete_sequence=custom_colors, 
            hover_name="name",
            hover_data={
                'pca_x': False, 'pca_y': False, 'cluster_name': False,
                'title': True, 'hp': True, 'attackdamage': True, 
                'armor': True, 'movespeed': True
            },
            title="Similarity Map",
            template="plotly_dark",
            height=650,
            size_max=15
        )
        
        # FINE TUNING OF THE GRAPH
        fig.update_traces(
            marker=dict(
                size=14,            
                opacity=0.8,       
                line=dict(width=1, color='white') 
            )
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',  
            title_font=dict(size=24, color='#C8AA6E', family="Helvetica Neue"),
            legend=dict(
                orientation="h",   
                yanchor="bottom", y=1.02,
                xanchor="right", x=1
            ),
            font=dict(family="Courier New, monospace") 
        )
        
        # Remove axes and grid completely
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        
        st.plotly_chart(fig, use_container_width=True)

    # --- Dataframe visualization ---
    st.subheader(f"Champions Data (Version: {latest_version})")
    cols_to_show = ['image', 'name', 'title', 'hp', 'armor', 'attackdamage', 'movespeed']
    st.dataframe(
        df[cols_to_show],
        column_config={
            "image": st.column_config.ImageColumn("Image"),
            "name": st.column_config.Column("Name"),
            "title": st.column_config.Column("Title"),
            "hp": st.column_config.ProgressColumn("HP", format="%d", min_value=300, max_value=700),
            "armor": st.column_config.Column("Armor"),
            "attackdamage": st.column_config.Column("Attack Damage"),
            "movespeed": st.column_config.Column("Move Speed")
        },
        hide_index=True,
        use_container_width=True,
        height=600
    )

else:
    st.error("No data available")   