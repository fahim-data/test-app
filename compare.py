import streamlit as st
import utils
from details import render_skill_legend

def navigate_to_details(job_title):
    st.session_state.selected_job = job_title
    st.session_state.current_page = 'Job Details'

def render_compare_pills(skills_df, canonical_title, skill_category):
    mask = (skills_df['Canonical Job Title'] == canonical_title) & \
           (skills_df['Skill_Category'] == skill_category)
    skills = skills_df[mask]
    
    st.markdown("""
        <style>
            .skill-container { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
            .skill-pill { position: relative; padding: 6px 14px; border-radius: 4px; font-size: 0.9em; font-weight: 600; cursor: help; border: 1px solid rgba(5, 25, 45, 0.1); }
            .skill-pill .tooltiptext { 
                visibility: hidden; width: 200px; background-color: #05192D; color: #FFFFFF; 
                text-align: left; border-radius: 6px; padding: 10px; position: absolute; 
                z-index: 999; bottom: 125%; left: 50%; margin-left: -100px; opacity: 0; 
                transition: opacity 0.3s; font-size: 0.8em; line-height: 1.4; border: 1px solid #03EF62;
            }
            .skill-pill:hover .tooltiptext { visibility: visible; opacity: 1; }
        </style>
    """, unsafe_allow_html=True)
    
    p_html = '<div class="skill-container">'
    for _, row in skills.iterrows():
        bg = '#03EF62' if row['Skill Type'] == 'core' else '#05192D'
        txt = '#05192D' if row['Skill Type'] == 'core' else '#FFFFFF'
        desc = str(row.get('Skill_Description', 'Details available upon request.'))
        pill = f'<div class="skill-pill" style="background-color: {bg}; color: {txt};">{row["Skill"]}<span class="tooltiptext"><strong>{row["Skill"]}</strong><br>{desc}</span></div>'
        p_html += pill
    p_html += '</div>'
    st.markdown(p_html, unsafe_allow_html=True)

def show_compare_page(data_dict):
    st.markdown('''<h1 style='text-align: center; color: #05192D;'>Compare Jobs</h1>''', unsafe_allow_html=True)
    title_df, skills_df = data_dict['titles'], data_dict['skills']
    jds_df = data_dict['descriptions']
    all_titles = utils.get_all_titles(title_df)
    
    c1, c2 = st.columns(2)
    with c1: job_a = st.selectbox('', all_titles, index=None, placeholder='Select First Job', key='compare_job_a')
    with c2: job_b = st.selectbox('', all_titles, index=None, placeholder='Select Second Job', key='compare_job_b')
    
    if st.button('Compare', use_container_width=True):
        if job_a and job_b: st.session_state.compare_active = True
        else: st.warning('Please select two jobs.')

    if st.session_state.get('compare_active'):
        st.divider()
        can_a, can_b = utils.get_canonical_title(job_a, title_df), utils.get_canonical_title(job_b, title_df)
        mask_a, mask_b = jds_df['Canonical Job Title'] == can_a, jds_df['Canonical Job Title'] == can_b
        raw_jd_a = jds_df[mask_a]['Description'].iloc[0] if not jds_df[mask_a].empty else None
        raw_jd_b = jds_df[mask_b]['Description'].iloc[0] if not jds_df[mask_b].empty else None

        jd_col1, jd_col2 = st.columns(2)
        with jd_col1:
            st.markdown(f'<h2 style="color: #05192D; border-bottom: 2px solid #03EF62; padding-bottom: 5px;">{job_a}</h2>', unsafe_allow_html=True)
            if raw_jd_a:
                st.markdown('**Overview**'); st.write_stream(utils.get_llm_overview(raw_jd_a))
                st.markdown('**Key Tasks**'); st.write_stream(utils.get_llm_tasks(raw_jd_a))
        with jd_col2:
            st.markdown(f'<h2 style="color: #05192D; border-bottom: 2px solid #03EF62; padding-bottom: 5px;">{job_b}</h2>', unsafe_allow_html=True)
            if raw_jd_b:
                st.markdown('**Overview**'); st.write_stream(utils.get_llm_overview(raw_jd_b))
                st.markdown('**Key Tasks**'); st.write_stream(utils.get_llm_tasks(raw_jd_b))

        st.divider()
        sk1, sk2 = st.columns(2)
        with sk1:
            st.markdown('#### Technical Skills'); render_compare_pills(skills_df, can_a, 'tech')
            st.markdown('#### Soft Skills'); render_compare_pills(skills_df, can_a, 'soft')
        with sk2:
            st.markdown('#### Technical Skills'); render_compare_pills(skills_df, can_b, 'tech')
            st.markdown('#### Soft Skills'); render_compare_pills(skills_df, can_b, 'soft')
        
        render_skill_legend()
            
        st.divider()
        st.subheader('Related Roles')
        rel1, rel2 = st.columns(2)
        def render_rel(can, suf):
            roles = utils.get_related_titles(can, skills_df)[:5]
            for i, (rn, _) in enumerate(roles):
                st.button(rn, key=f'comp_btn_{suf}_{i}', use_container_width=True, on_click=navigate_to_details, args=(rn,))
        with rel1: 
            st.markdown(f'Roles related to **{job_a}**')
            render_rel(can_a, 'a')
        with rel2:
            st.markdown(f'Roles related to **{job_b}**')
            render_rel(can_b, 'b')