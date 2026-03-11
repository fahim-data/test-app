import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    file_path = 'jobs_n_skills.xlsx'
    
    title_df = pd.read_excel(file_path, sheet_name='job-title-lookup')
    skills_df = pd.read_excel(file_path, sheet_name='skill-lookup')
    jds_df = pd.read_excel(file_path, sheet_name='job-description')
    timeseries_df = pd.read_excel(file_path, sheet_name='job-timeseries')
    geo_df = pd.read_excel(file_path, sheet_name='job-geo-demand')
    employers_df = pd.read_excel(file_path, sheet_name='job-top-employers')
    tvs_df = pd.read_excel(file_path, sheet_name='tech-vs-soft')
    trends_df = pd.read_excel(file_path, sheet_name='skill-trends')
    map_df = pd.read_csv('job_map_data.csv')
    skills_map_df = pd.read_csv('skills_map_data.csv')

    return {
        'titles': title_df,
        'skills': skills_df,
        'descriptions': jds_df,
        'timeseries': timeseries_df,
        'geo': geo_df,
        'employers': employers_df,
        'tech_vs_soft': tvs_df,
        'skill_trends': trends_df,
        'job_map': map_df,
        'skill_map': skills_map_df
    }