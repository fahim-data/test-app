import streamlit as st
import utils
import plotly.express as px
import plotly.graph_objects as go


def update_to_related(new_job):
    st.session_state.selected_job = new_job
    st.session_state.current_page = 'Job Details'


def render_skill_legend():
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px; padding: 10px; background-color: rgba(5, 25, 45, 0.03); border-radius: 4px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 12px; height: 12px; background-color: #03EF62; border-radius: 2px;"></div>
                <span style="font-size: 0.85em; font-weight: 600; color: #05192D;">Core Skills</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 12px; height: 12px; background-color: #05192D; border-radius: 2px;"></div>
                <span style="font-size: 0.85em; font-weight: 600; color: #05192D;">Supplementary Skills</span>
            </div>
            <div style="margin-left: auto; font-style: italic; font-size: 1em; color: #666;">
                * Hover over a skill to see its description
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_skill_pills(skills_df, canonical_title, skill_category):
    mask = (skills_df['Canonical Job Title'] == canonical_title) & \
           (skills_df['Skill_Category'] == skill_category)
    skills = skills_df[mask]

    st.markdown("""
        <style>
            .skill-container { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 25px; }
            .skill-pill { position: relative; padding: 8px 16px; border-radius: 4px; font-size: 0.9em; font-weight: 600; cursor: help; border: 1px solid rgba(5, 25, 45, 0.1); }
            .skill-pill .tooltiptext { 
                visibility: hidden; width: 240px; background-color: #05192D; color: #FFFFFF; 
                text-align: left; border-radius: 6px; padding: 12px; position: absolute; 
                z-index: 999; bottom: 135%; left: 50%; margin-left: -120px; opacity: 0; 
                transition: opacity 0.3s; font-size: 0.85em; font-weight: 400; line-height: 1.5; 
                border: 2px solid #03EF62; box-shadow: 0px 8px 24px rgba(0,0,0,0.2); pointer-events: none;
            }
            .skill-pill .tooltiptext::after { 
                content: ""; position: absolute; top: 100%; left: 50%; margin-left: -8px; 
                border-width: 8px; border-style: solid; border-color: #03EF62 transparent transparent transparent; 
            }
            .skill-pill:hover .tooltiptext { visibility: visible; opacity: 1; }
        </style>
    """, unsafe_allow_html=True)

    p_html = '<div class="skill-container">'
    for _, row in skills.iterrows():
        is_core = row['Skill Type'] == 'core'
        bg = '#03EF62' if is_core else '#05192D'
        txt = '#05192D' if is_core else '#FFFFFF'
        desc = str(row.get('Skill_Description',
                   'Skill details available upon request.'))

        pill = f'<div class="skill-pill" style="background-color: {bg}; color: {txt};">'
        pill += f'{row["Skill"]}<span class="tooltiptext"><strong style="color: #03EF62; display: block; margin-bottom: 5px;">{row["Skill"]}</strong>{desc}</span></div>'
        p_html += pill
    p_html += '</div>'
    st.markdown(p_html, unsafe_allow_html=True)


def show_job_details(job_title, data_dict):
    if not job_title:
        st.info('No job selected.')
        return

    st.markdown(f'''<h1 style='text-align: center; color: #05192D;'>Job Details</h1>''',
                unsafe_allow_html=True)
    title_df, skills_df = data_dict['titles'], data_dict['skills']
    jds_df, ts_df = data_dict['descriptions'], data_dict['timeseries']
    trends_df = data_dict['skill_trends']
    
    # Extract map and geo/employer data
    map_df = data_dict.get('job_map')
    skill_map_df = data_dict.get('skill_map')

    st.header(job_title, divider='green')
    can_title = utils.get_canonical_title(job_title, title_df)
    jd_mask = jds_df['Canonical Job Title'] == can_title
    raw_jd = jds_df[jd_mask]['Description'].iloc[0] if not jds_df[jd_mask].empty else None

    # --- JOB OVERVIEW & TS ---
    col_jd, col_ts = st.columns([1, 1])
    with col_jd:
        if raw_jd:
            st.subheader('Job Overview')
            st.write_stream(utils.get_llm_overview(raw_jd))
            st.markdown('<br>', unsafe_allow_html=True)
            st.subheader('Key Tasks')
            st.write_stream(utils.get_llm_tasks(raw_jd))
        else:
            st.warning('Description data unavailable.')

    with col_ts:
        st.subheader('Job Growth Over Time')
        job_ts = ts_df[ts_df['Canonical Job Title'] == can_title]
        if not job_ts.empty:
            fig_ts = px.line(job_ts, x='Year-Month',
                             y='Posting_Count', template='plotly_white')
            fig_ts.update_traces(line_color='#03EF62', line_width=3)
            fig_ts.update_layout(xaxis_title='', yaxis_title='', margin=dict(
                l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig_ts, width="stretch")

    st.divider()

    # --- DEMAND BY GEO & TOP EMPLOYERS ---
    col_geo, col_emp = st.columns(2)
    
    with col_geo:
        st.subheader('Demand by Geography')
        geo_df = data_dict.get('geo')
        if geo_df is not None and not geo_df.empty:
            geo_data = geo_df[geo_df['Canonical Job Title'] == can_title]
            if not geo_data.empty:
                count_col = 'Posting_Count' if 'Posting_Count' in geo_data.columns else 'Count'
                loc_col = 'Location' if 'Location' in geo_data.columns else geo_data.columns[1]
                
                geo_data = geo_data.sort_values(by=count_col, ascending=False).head(10)
                
                fig_geo = px.bar(geo_data, x=count_col, y=loc_col, orientation='h', template='plotly_white')
                fig_geo.update_traces(marker_color='#05192D') 
                fig_geo.update_layout(xaxis_title='', yaxis_title='', yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
                st.plotly_chart(fig_geo, width="stretch")
            else:
                st.info('Geography data unavailable for this role.')
        else:
            st.info('Geography data unavailable.')

    with col_emp:
        st.subheader('Top Employers')
        employers_df = data_dict.get('employers')
        if employers_df is not None and not employers_df.empty:
            emp_data = employers_df[employers_df['Canonical Job Title'] == can_title]
            if not emp_data.empty:
                count_col = 'Posting_Count' if 'Posting_Count' in emp_data.columns else 'Count'
                comp_col = 'Company' if 'Company' in emp_data.columns else emp_data.columns[1]
                
                emp_data = emp_data.sort_values(by=count_col, ascending=False).head(10)
                
                # Reverted back to horizontal bar chart
                fig_emp = px.bar(emp_data, x=count_col, y=comp_col, orientation='h', template='plotly_white')
                fig_emp.update_traces(marker_color='#03EF62')
                fig_emp.update_layout(xaxis_title='', yaxis_title='', yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
                st.plotly_chart(fig_emp, width="stretch")
            else:
                st.info('Employer data unavailable for this role.')
        else:
            st.info('Employer data unavailable.')

    st.divider()

    # --- 1. THE JOB LANDSCAPE MAP ---
    st.subheader('The Job Landscape')
    st.markdown(
        f"A map showing where **{job_title}** sits relative to all other roles in the Data/AI ecosystem.")

    if map_df is not None and not map_df.empty:
        # Separate the selected job from the rest
        selected_df = map_df[map_df['title'] == job_title]
        background_df = map_df[map_df['title'] != job_title]

        fig_map = go.Figure()

        # Add background dots (Greyed out)
        fig_map.add_trace(go.Scatter(
            x=background_df['x'],
            y=background_df['y'],
            mode='markers',
            marker=dict(color="#C6D8C3", size=9, opacity=0.55),
            text=background_df['title'],
            hovertemplate="<b>%{text}</b><extra></extra>",
            hoverlabel=dict(font=dict(size=14)),
            name='Other Roles'
        ))

        # Add the highlighted selected job
        if not selected_df.empty:
            fig_map.add_trace(go.Scatter(
                x=selected_df['x'],
                y=selected_df['y'],
                mode='markers',
                marker=dict(
                    color='#03EF62',
                    size=12,
                    line=dict(color='#05192D', width=1)
                ),
                text=selected_df['title'],
                hoverinfo='text',
                hovertemplate="<b>%{text}</b><extra></extra>",
                hoverlabel=dict(font=dict(size=14)),
                name='Selected Role'
            ))

        # Hide axes and clean up layout to look like a pure map
        fig_map.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=400,
            hovermode='closest'
        )
        st.plotly_chart(fig_map, width="stretch")
    else:
        st.info(
            "Landscape map data not available. Please ensure 'job_map_data.csv' is loaded in data_manager.")

    st.divider()

    # --- 2. SKILL PILLS ---
    st.markdown('### Technical Skills')
    render_skill_pills(skills_df, can_title, 'tech')
    st.markdown('### Soft Skills')
    render_skill_pills(skills_df, can_title, 'soft')

    render_skill_legend()  # Added the legend here

    st.divider()
    
    # --- 3. IN DEMAND SKILLS (Trends) ---
    col_freq, col_sk_ts = st.columns(2)
    job_trends = trends_df[trends_df['Canonical Job Title'] == can_title]
    if not job_trends.empty:
        f_data = job_trends.groupby('Skill')['Skill_Posting_Count'].sum(
        ).reset_index().sort_values('Skill_Posting_Count', ascending=False).head(10)
        t_skills = f_data['Skill'].tolist()[:5]
        with col_freq:
            st.subheader('In-Demand Skills')
            fig_f = px.bar(f_data, x='Skill_Posting_Count',
                           y='Skill', orientation='h', template='plotly_white')
            fig_f.update_traces(marker_color='#03EF62')
            fig_f.update_layout(xaxis_title='', yaxis_title='', yaxis={'categoryorder': 'total ascending'}, margin=dict(
                l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig_f, width="stretch")
        with col_sk_ts:
            st.subheader('In-Demand Skills Over Time')
            t_data = job_trends[job_trends['Skill'].isin(t_skills)]
            pal = ['#03EF62', '#05192C', '#007A33', '#00FFB2', '#798086']
            fig_s = px.line(t_data, x='Year-Month', y='Skill_Posting_Count',
                            color='Skill', template='plotly_white', color_discrete_sequence=pal)
            fig_s.update_layout(xaxis_title='', yaxis_title='', margin=dict(l=0, r=0, t=20, b=0), paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)', height=350, legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
            st.plotly_chart(fig_s, width="stretch")

    st.divider()

    # --- 4. THE SKILL LANDSCAPE MAP ---
    st.subheader('The Skill Landscape')
    st.markdown(f"A map of the entire skill universe. Skills required for **{job_title}** are highlighted.")
    
    if skill_map_df is not None and not skill_map_df.empty:
        job_skills_df = skills_df[skills_df['Canonical Job Title'] == can_title]
        core_skills = job_skills_df[job_skills_df['Skill Type'] == 'core']['Skill'].tolist()
        supp_skills = job_skills_df[job_skills_df['Skill Type'] != 'core']['Skill'].tolist()
        all_job_skills = core_skills + supp_skills

        bg_skills_df = skill_map_df[~skill_map_df['Skill'].isin(all_job_skills)]
        core_map_df = skill_map_df[skill_map_df['Skill'].isin(core_skills)]
        supp_map_df = skill_map_df[skill_map_df['Skill'].isin(supp_skills)]

        fig_sk_map = go.Figure()

        # Format Categories and Types for the background tooltips
        bg_cats = bg_skills_df['Category'].fillna('').str.capitalize()
        bg_types = bg_skills_df['Type'].fillna('').str.title().replace({'Supp': 'Supplementary'})
        
        # Background Skills (Grey)
        fig_sk_map.add_trace(go.Scatter(
            x=bg_skills_df['x'], y=bg_skills_df['y'], mode='markers',
            marker=dict(color="#C6D8C3", size=9, opacity=0.55),
            text=bg_skills_df['Skill'],
            customdata=list(zip(bg_cats, bg_types)),  # Passing both columns
            hovertemplate="<b>%{text}</b><br>%{customdata[0]} Skill | %{customdata[1]}<extra></extra>", 
            hoverlabel=dict(font=dict(size=14)),           
            name='Other Skills'
        ))

        # Supplementary Skills (Navy)
        if not supp_map_df.empty:
            fig_sk_map.add_trace(go.Scatter(
                x=supp_map_df['x'], y=supp_map_df['y'], mode='markers',
                marker=dict(color='#05192D', size=12, line=dict(color='#03EF62', width=1)),
                text=supp_map_df['Skill'],
                customdata=supp_map_df['Category'].fillna('').str.capitalize(),
                hovertemplate="<b>%{text}</b><br>%{customdata} Skill | Supplementary<extra></extra>", 
                hoverlabel=dict(font=dict(size=14)),        
                name='Supplementary Skills'
            ))

        # Core Skills (Green)
        if not core_map_df.empty:
            fig_sk_map.add_trace(go.Scatter(
                x=core_map_df['x'], y=core_map_df['y'], mode='markers',
                marker=dict(color='#03EF62', size=12, line=dict(color='#05192D', width=1)),
                text=core_map_df['Skill'],
                customdata=core_map_df['Category'].fillna('').str.capitalize(),
                hovertemplate="<b>%{text}</b><br>%{customdata} Skill | Core<extra></extra>", 
                hoverlabel=dict(font=dict(size=14)),        
                name='Core Skills'
            ))

        fig_sk_map.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            showlegend=False, margin=dict(l=0, r=0, t=10, b=0), height=400, hovermode='closest'
        )
        st.plotly_chart(fig_sk_map, width="stretch")
    else:
        st.info("Skill landscape map data not available.")

    st.divider()

    # --- 5. RELATED ROLES (Reverted to Jaccard/Skill Overlap) ---
    st.subheader('Related Roles')
    
    # Reverted to using skills_df instead of map_df
    roles = utils.get_related_titles(can_title, skills_df)[:6]

    for i in range(0, len(roles), 2):
        c1, c2 = st.columns(2)
        with c1:
            rn1 = roles[i][0]
            st.button(rn1, key=f'rel_{rn1}_{i}', width="stretch",
                      on_click=update_to_related, args=(rn1,))
        if i + 1 < len(roles):
            with c2:
                rn2 = roles[i+1][0]
                st.button(rn2, key=f'rel_{rn2}_{i+1}', width="stretch",
                          on_click=update_to_related, args=(rn2,))