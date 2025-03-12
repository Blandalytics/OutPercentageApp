import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pybaseball import statcast
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Out Percentage Analysis",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        color: #0066cc;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #0066cc;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid #f0f2f6;
    }
    
    /* Data table styling */
    .dataframe-container {
        border-radius: 10px;
        padding: 1rem;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    
    /* Remove spacing between elements */
    .element-container {
        margin-bottom: 0 !important;
    }
    
    /* Remove padding from markdown elements */
    .stMarkdown {
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    
    /* Tighten up headers */
    h4 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #f0f2f6;
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Loading spinner */
    div.stSpinner > div {
        border-top-color: #0066cc !important;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton button:hover {
        background-color: #0052a3;
    }
    
    /* Compact layout */
    [data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Remove whitespace from streamlit components */
    div.block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Reduce spacing in stMarkdown */
    div.stMarkdown p {
        margin-bottom: 0.3rem !important;
    }
    
    /* Reduce spacing in plotly charts */
    .js-plotly-plot {
        margin-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1 class="main-title">⚾Out Percentage Analysis⚾</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyze MLB player out percentages by pitch type using Statcast data</p>', unsafe_allow_html=True)

# Function to load and process data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_statcast_data(start_year, end_year):
    try:
        # Get data for selected years
        start_date = f"{start_year}-03-01"
        end_date = f"{end_year}-11-30"
        
        with st.spinner("Fetching Statcast data... This may take a moment."):
            data = statcast(start_dt=start_date, end_dt=end_date)
            st.success("Data loaded successfully!")
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # If error occurs, try with a smaller date range
        try:
            # Try last 3 weeks
            from datetime import timedelta
            today = datetime.now()
            new_start_date = (today - timedelta(days=21)).strftime("%Y-%m-%d")
            new_end_date = today.strftime("%Y-%m-%d")
            with st.spinner(f"Trying with a smaller date range: {new_start_date} to {new_end_date}..."):
                data = statcast(start_dt=new_start_date, end_dt=new_end_date)
                st.success("Data loaded successfully with reduced date range!")
            return data
        except Exception as e2:
            st.error(f"Failed to load data: {e2}")
            return pd.DataFrame()

# Function to calculate out percentage based on OutPercentageNewStuff.ipynb
def calculate_out_percentage(data):
    # Create column that is a flag that shows if a pitch resulted in an out or not
    # Using the exact same out events as in the notebook
    out_events = [
        'field_out', 'strikeout', 'grounded_into_double_play', 'fielders_choice_out', 
        'force_out', 'sac_fly', 'sac_bunt', 'strikeout_double_play', 'double_play', 
        'sac_fly_double_play', 'other_out', 'triple_play', 'sac_bunt_double_play'
    ]
    
    # Add a column indicating if the event resulted in an out
    data['IsOutPitch'] = data['events'].isin(out_events).astype(bool)
    
    return data

# Function to format player names from "Last, First" to "First Last"
def format_player_name(name):
    if ',' in name:
        last_name, first_name = name.split(',', 1)
        return f"{first_name.strip()} {last_name.strip()}"
    return name

# Function to get out percentage by pitch type for a player in a specific year
def get_out_percentage_by_pitch_type(data, player_name, year, min_pitches=5):
    # Filter data for the selected player and year
    player_data = data[(data['player_name'] == player_name) & (data['game_year'] == year)]
    
    # Group by pitch type and calculate out percentage
    pitch_type_results = player_data.groupby('pitch_type')['IsOutPitch'].agg([
        ('out_pitch_count', 'sum'), 
        ('total_pitches', 'count')
    ]).reset_index()
    
    # Calculate out percentage
    pitch_type_results['out_percentage'] = (pitch_type_results['out_pitch_count'] / pitch_type_results['total_pitches'] * 100).round(2)
    
    # Filter to include only pitch types with significant sample size
    pitch_type_results = pitch_type_results[pitch_type_results['total_pitches'] >= min_pitches]
    
    # Map pitch type codes to full names
    pitch_type_map = {
        'FF': 'Four-Seam Fastball',
        'SL': 'Slider',
        'CH': 'Changeup',
        'CU': 'Curveball',
        'SI': 'Sinker',
        'FC': 'Cutter',
        'FS': 'Splitter',
        'FT': 'Two-Seam Fastball',
        'KC': 'Knuckle Curve',
        'EP': 'Eephus',
        'KN': 'Knuckleball',
        'SC': 'Screwball',
        'ST': 'Sweeper',
        'SV': 'Slurve'
    }
    
    # Add full pitch type names
    pitch_type_results['pitch_name'] = pitch_type_results['pitch_type'].map(
        lambda x: pitch_type_map.get(x, x)
    )
    
    return pitch_type_results

# Function to calculate league average out percentage by pitch type
def get_league_avg_out_percentage(data, year, min_pitches=5):
    # Filter data for the selected year
    year_data = data[data['game_year'] == year]
    
    # Group by pitch type and calculate out percentage
    league_avg = year_data.groupby('pitch_type')['IsOutPitch'].agg([
        ('out_pitch_count', 'sum'), 
        ('total_pitches', 'count')
    ]).reset_index()
    
    # Calculate out percentage
    league_avg['out_percentage'] = (league_avg['out_pitch_count'] / league_avg['total_pitches'] * 100).round(2)
    
    # Filter to include only pitch types with significant sample size
    league_avg = league_avg[league_avg['total_pitches'] >= min_pitches]
    
    # Map pitch type codes to full names
    pitch_type_map = {
        'FF': 'Four-Seam Fastball',
        'SL': 'Slider',
        'CH': 'Changeup',
        'CU': 'Curveball',
        'SI': 'Sinker',
        'FC': 'Cutter',
        'FS': 'Splitter',
        'FT': 'Two-Seam Fastball',
        'KC': 'Knuckle Curve',
        'EP': 'Eephus',
        'KN': 'Knuckleball',
        'SC': 'Screwball',
        'ST': 'Sweeper',
        'SV': 'Slurve'
    }
    
    # Add full pitch type names
    league_avg['pitch_name'] = league_avg['pitch_type'].map(
        lambda x: pitch_type_map.get(x, x)
    )
    
    return league_avg

# Sidebar for filters
with st.sidebar:
    st.markdown("## Filters")
    st.markdown("---")
    
    # Year selection
    current_year = datetime.now().year
    year = st.selectbox("Select Year:", list(range(current_year, 2014, -1)))
    
    # Minimum pitches filter
    min_pitches = st.slider(
        "Minimum pitches for analysis:",
        min_value=1,
        max_value=150,
        value=5,
        help="Only include pitch types with at least this many pitches"
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app analyzes MLB player out percentages by pitch type.")
    st.markdown("Data is sourced from the MLB Statcast database via the pybaseball package.")

# Main app
# Load data for the selected year
data = load_statcast_data(year, year)

if not data.empty:
    # Process data
    processed_data = calculate_out_percentage(data)
    
    # Get unique player names and format them
    player_names_dict = {name: format_player_name(name) for name in sorted(processed_data['player_name'].dropna().unique())}
    
    # Create a mapping from formatted names back to original names
    formatted_to_original = {format_player_name(name): name for name in player_names_dict.keys()}
    
    # Player selection using formatted names
    formatted_player_names = sorted(player_names_dict.values())
    selected_formatted_player = st.selectbox("Select a player:", formatted_player_names)
    
    # Get the original player name for data filtering
    selected_player = formatted_to_original[selected_formatted_player]
    
    if selected_player:
        # Get out percentage by pitch type for selected player and year
        pitch_results = get_out_percentage_by_pitch_type(processed_data, selected_player, year, min_pitches)
        
        # Display results
        st.markdown(f'<h2 class="section-header">Out Percentage Analysis for {selected_formatted_player} ({year})</h2>', unsafe_allow_html=True)
        
        if not pitch_results.empty:
            # Create two columns for layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Display data table with styling
                st.markdown("#### Pitch Type Breakdown")
                
                # Sort by out percentage descending
                sorted_results = pitch_results.sort_values('out_percentage', ascending=False)
                
                st.dataframe(
                    sorted_results[['pitch_name', 'total_pitches', 'out_pitch_count', 'out_percentage']]
                    .rename(columns={
                        'pitch_name': 'Pitch Type',
                        'total_pitches': 'Total Pitches',
                        'out_pitch_count': 'Outs',
                        'out_percentage': 'Out %'
                    })
                    .style.format({'Out %': '{:.2f}%'})
                    .background_gradient(subset=['Out %'], cmap='RdYlGn')
                    .set_properties(**{'text-align': 'center'})
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add summary statistics
                st.markdown("#### Summary Statistics")
                
                total_pitches = pitch_results['total_pitches'].sum()
                total_outs = pitch_results['out_pitch_count'].sum()
                overall_out_pct = (total_outs / total_pitches * 100).round(2)
                
                summary_data = {
                    'Metric': ['Total Pitches', 'Total Outs', 'Overall Out %'],
                    'Value': [f"{total_pitches:,}", f"{total_outs:,}", f"{overall_out_pct:.2f}%"]
                }
                
                st.table(pd.DataFrame(summary_data).set_index('Metric'))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Create pie chart with styling
                st.markdown(f"#### {selected_formatted_player}'s Out Percentage by Pitch Type")
                
                # Create labels with pitch name and percentage
                pitch_results['label'] = pitch_results.apply(
                    lambda row: f"{row['pitch_name']} ({row['out_percentage']:.1f}%)", axis=1
                )
                
                # Create pie chart using plotly
                fig = px.pie(
                    pitch_results,
                    values='out_pitch_count',
                    names='label',
                    color='out_percentage',
                )
                
                # Update layout
                fig.update_layout(
                    legend_title="Pitch Type (Out %)",
                    height=450,
                    margin=dict(t=10, b=10, l=10, r=10),
                    font=dict(family="Arial", size=12),
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02
                    )
                )
                
                # Display chart
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Add a comparison bar chart
                st.markdown(f"#### {selected_formatted_player} vs. League Average Out Percentage")
                
                # Get league average out percentage
                league_avg = get_league_avg_out_percentage(processed_data, year, min_pitches)
                
                # Create a dataframe for comparison
                comparison_data = []
                
                # Sort pitch types by player's out percentage
                sorted_pitch_types = pitch_results.sort_values('out_percentage', ascending=False)['pitch_type'].tolist()
                
                # For each pitch type the player throws
                for pitch_type in sorted_pitch_types:
                    player_row = pitch_results[pitch_results['pitch_type'] == pitch_type].iloc[0]
                    
                    # Find corresponding league average
                    league_row = league_avg[league_avg['pitch_type'] == pitch_type]
                    
                    if not league_row.empty:
                        league_pct = league_row.iloc[0]['out_percentage']
                    else:
                        league_pct = 0
                    
                    # Add player data
                    comparison_data.append({
                        'Pitch Type': player_row['pitch_name'],
                        'Out Percentage': player_row['out_percentage'],
                        'Category': f"{selected_formatted_player}"
                    })
                    
                    # Add league average data
                    comparison_data.append({
                        'Pitch Type': player_row['pitch_name'],
                        'Out Percentage': league_pct,
                        'Category': 'League Average'
                    })
                
                # Convert to DataFrame
                comparison_df = pd.DataFrame(comparison_data)
                
                # Create grouped bar chart
                fig2 = px.bar(
                    comparison_df,
                    x='Pitch Type',
                    y='Out Percentage',
                    color='Category',
                    barmode='group',
                    text=comparison_df['Out Percentage'].apply(lambda x: f'{x:.1f}%'),
                    color_discrete_map={
                        f"{selected_formatted_player}": '#0066cc',
                        'League Average': '#999999'
                    }
                )
                
                # Update layout
                fig2.update_layout(
                    height=450,
                    margin=dict(t=10, b=10, l=10, r=10),
                    font=dict(family="Arial", size=12),
                    xaxis_tickangle=-45,
                    yaxis_title="Out Percentage (%)",
                    xaxis_title="",
                    legend_title="",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Update bar text position
                fig2.update_traces(textposition='outside')
                
                # Display chart
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning(f"No pitch data available for {selected_formatted_player} in {year} with at least {min_pitches} pitches per type.")
else:
    st.error("Failed to load Statcast data. Please try again later.")

# Footer
st.markdown('<div class="footer">', unsafe_allow_html=True)
st.markdown("Data source: MLB Statcast via pybaseball | Created with Streamlit by @BeRett21")
st.markdown('</div>', unsafe_allow_html=True) 