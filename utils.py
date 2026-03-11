import numpy as np
import streamlit as st
from openai import OpenAI

@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

def format_fallback_jd(original_jd):
    sentences = [s.strip() for s in original_jd.split('.') if s.strip()]
    text = '\n'.join([f'• {sentence}.' for sentence in sentences])
    yield text


def get_llm_overview(original_jd):
    try:
        client = get_openai_client()
        prompt = f'Provide a very short, professional one-paragraph overview (max 2 sentences) describing this role based on the following description:\n\n{original_jd}'

        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': 'You are a concise HR expert.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.5,
            max_tokens=100,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception:
        yield 'Overview currently unavailable.'


def get_llm_tasks(original_jd):
    try:
        client = get_openai_client()
        prompt = f'Extract 3 to 4 short, impactful bullet points representing the primary tasks of this role from the following description. Do not include introductory text:\n\n{original_jd}'

        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': 'You are a concise HR expert.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.3,
            max_tokens=150,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception:
        yield '• Task details currently unavailable.'


def get_all_titles(title_df):
    return title_df['Job title'].dropna().unique().tolist()


def get_canonical_title(selected_title, title_df):
    match = title_df[title_df['Job title'] == selected_title]
    if not match.empty:
        return match['Canonical Job Title'].iloc[0]
    return ''


def get_related_titles(canonical_title, skills_df, top_n=6):
    target_skills = set(
        skills_df[skills_df['Canonical Job Title'] == canonical_title]['Skill'])

    all_titles = skills_df['Canonical Job Title'].unique()

    scores = []
    for title in all_titles:
        if title == canonical_title:
            continue

        compare_skills = set(
            skills_df[skills_df['Canonical Job Title'] == title]['Skill'])
        shared_count = len(target_skills.intersection(compare_skills))

        scores.append((title, shared_count))

    scores.sort(key=lambda x: x[1], reverse=True)

    return scores[:top_n]


def get_skills(job_title, skills_df, skill_type, category):
    mask = (skills_df['Canonical Job Title'] == job_title) & \
           (skills_df['Skill_Category'] == category) & \
           (skills_df['Skill Type'] == skill_type)

    return skills_df[mask]['Skill'].tolist()


def get_related_titles_from_map(canonical_title, map_df, top_n=6):
    target = map_df[map_df['title'] == canonical_title]
    if target.empty:
        return []

    target_x = target['x'].values[0]
    target_y = target['y'].values[0]

    others = map_df[map_df['title'] != canonical_title].copy()

    others['distance'] = np.sqrt(
        (others['x'] - target_x)**2 + (others['y'] - target_y)**2)

    closest = others.sort_values('distance', ascending=True).head(top_n)

    return [(row['title'], row['distance']) for _, row in closest.iterrows()]
