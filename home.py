import streamlit as st
import utils

def trigger_search():
    # 1. Terminal Check
    print("DEBUG: trigger_search function CALLED") 
    
    search_value = st.session_state.get('home_search_selectbox')
    
    if search_value:
        st.session_state.selected_job = search_value
        st.session_state.current_page = "Job Details"
        print(f"DEBUG: Redirecting to Details for: {search_value}")
    else:
        st.error("Selectbox is empty!")

def show_job_search(title_df, skills_df, jds_df):
    st.markdown('''
        <style>
        div[data-baseweb="select"] > div:nth-child(2) { display: none !important; }
        div[data-baseweb="select"] svg { display: none !important; }
        </style>
    ''', unsafe_allow_html=True)

    st.markdown('''<h1 style='text-align: center;'>Job Explorer</h1>''', unsafe_allow_html=True)
    
    all_titles = utils.get_all_titles(title_df)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.selectbox(
            'Search', 
            all_titles, 
            index=None, 
            placeholder='Search for a job title', 
            label_visibility='collapsed',
            key='home_search_selectbox'
        )
        
        # We use the 'key' here to ensure Streamlit tracks this specific button
        st.button(
            'Search', 
            use_container_width=True, 
            on_click=trigger_search,
            key='home_search_button' 
        )