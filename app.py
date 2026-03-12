import streamlit as st
import data_manager
import home
import details
import compare

# --- 1. CONFIG & DATA ---
st.set_page_config(
    page_title="Job Explorer", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

data = data_manager.load_data()

title_df = data["titles"]
skills_df = data["skills"]
jds_df = data["descriptions"]

# --- 2. INITIALIZE STATE ---
if 'selected_job' not in st.session_state:
    st.session_state.selected_job = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Job Search"
# Track the previous page to detect transitions
if 'previous_page' not in st.session_state:
    st.session_state.previous_page = "Job Search"

# Add this inside your app.py, ideally at the top of the Router section
st.markdown(
    """
    <style>
    /* Target the search bar container */
    div[data-baseweb="select"] {
        border-radius: 4px !important;
    }

    /* Target the border color when the search bar is active/focused */
    div[data-baseweb="select"] > div:focus-within {
        border-color: #03EF62 !important;
        box-shadow: 0 0 0 1px #03EF62 !important;
    }

    /* Target the hover state of the search bar */
    div[data-baseweb="select"]:hover {
        border-color: #03EF62 !important;
    }

    /* Styling for the dropdown list items to match Navy/Green */
    ul[role="listbox"] li {
        color: #05192D !important;
    }
    
    ul[role="listbox"] li:hover {
        background-color: rgba(3, 239, 98, 0.1) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. SIDEBAR NAVIGATION (Button Style) ---
st.sidebar.title("Navigation")

# Updated list with your new name
nav_options = ["Job Search", "Job Details", "Compare Jobs"]

# --- NEW SAFETY CHECK ---
# If the stored page name isn't in our current list, reset it to the default
if st.session_state.current_page not in nav_options:
    st.session_state.current_page = "Job Search"

# Now it is guaranteed to find the index without throwing a ValueError
current_idx = nav_options.index(st.session_state.current_page)

for i, option in enumerate(nav_options):
    # DataCamp Design System: Navy (#05192D) and Green (#03EF62)
    if i == current_idx:
        bg_color = "#03EF62"
        text_color = "#05192D"
        border_color = "#03EF62"
    else:
        bg_color = "#05192D"
        text_color = "#FFFFFF"
        border_color = "#444455"

    st.sidebar.markdown(
        f"""
        <style>
        div[data-testid="stSidebar"] button[key="nav_btn_{i}"] {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
            border: 2px solid {border_color} !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # UPDATED: Replaced use_container_width=True with width="stretch"
    if st.sidebar.button(option, key=f"nav_btn_{i}", width="stretch"):
        # FRESH LOAD LOGIC: If entering Compare Jobs, reset its internal state
        if option == "Compare Jobs":
            st.session_state.compare_active = False
            if 'compare_job_a' in st.session_state:
                st.session_state.compare_job_a = None
            if 'compare_job_b' in st.session_state:
                st.session_state.compare_job_b = None
        
        st.session_state.current_page = option
        st.rerun()

# --- 4. ROUTER ---
if st.session_state.current_page == "Job Search":
    print('in')
    home.show_job_search(title_df, skills_df, jds_df)
elif st.session_state.current_page == "Compare Jobs":
    compare.show_compare_page(data)
else:
    print(st.session_state.selected_job)
    details.show_job_details(st.session_state.selected_job, data)