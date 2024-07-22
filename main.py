import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import duckdb
import matplotlib as mpl
import streamlit_shadcn_ui as ui

from streamlit_timeline import st_timeline


from matplotlib.cm import ScalarMappable
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from textwrap import wrap
from matplotlib.colors import ListedColormap


st.set_page_config(layout="wide")


con = duckdb.connect(database = "./data/my-db.db", read_only = False)


aggregate_string = """
                                   avg(rage) AS rage, 
                                   avg(physical) AS physical, 
                                   avg(creativity) AS creativity, 
                                   avg(focus) AS focus, 
                                   avg(drive) AS drive,
                                   avg(resilience) AS resilience
                    """


st.markdown(f"""
            <style>
            body* {{
                font-family: serif;
            }}
            .stDeployButton {{
                visibility: hidden;
            }}
            img{{
                border-radius: 6px;
            }}
            </style>
            """, unsafe_allow_html=True)


plt.rcParams["font.family"] = "serif" 

col1, col2, col3, = st.columns([1, 2, 1])
with col2:
    # year = ui.select(options=["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2014", "2012"])
    year = st.selectbox("",options=["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2014", "2012"])
    events_rel = con.sql("SELECT * FROM events").set_alias("events_rel")
    events_rel_filtered = events_rel.filter("date <= %s" % "'%s-01-01'" % str(int(year) + 1))
    events_df = events_rel.df()
    events_filtered_df = events_rel_filtered.df()
    events_df = events_df.drop(['id'], axis=1)
    events_df['date'] = events_df['date'].dt.strftime('%Y-%m-%d')
    events_filtered_df['date'] = events_filtered_df['date'].dt.strftime('%Y-%m-%d')
    attrs_rel = con.sql("SELECT * FROM attributes").set_alias("attrs_rel")
    attrs_joined = events_rel.join(attrs_rel, "events_rel.id = attrs_rel.event_id")
    attrs_filtered = attrs_joined.filter("date BETWEEN %s AND %s" % ("'%s-01-1'" % year, "'%s-01-01'" % str(int(year) + 1)))
    attrs_avg_df_overall = attrs_joined.aggregate(aggregate_string).df()
    attrs_avg_df = attrs_filtered.aggregate(aggregate_string).df()

    skills_joined = con.execute("""WITH ranked_skills AS ( 
                            SELECT s.id, s.name, s.level, e.date, ROW_NUMBER() OVER (PARTITION BY s.name ORDER BY e.date DESC) AS rn 
                            FROM skills s 
                            JOIN events e 
                            ON s.event_id = e.id WHERE e.date <= DATE '%s-06-30' 
                            ) 
                            SELECT id, name, level, date 
                            FROM ranked_skills 
                            WHERE rn = 1 
                            ORDER BY name""" % str(int(year) + 1)).df()

    level_dict = {'Beginner': 0, 'Advanced Beginner': 1, 'Competent': 2, 'Proeficient': 3, 'Expert': 4}

    skills_joined['level_num'] = skills_joined['level'].map(level_dict)


    matrix = np.pad(skills_joined['level_num'].values.astype(float), (0, 25 - len(skills_joined.values)), mode='constant', constant_values=np.nan).reshape(5, 5)
    # matrix = np.pad(skills_joined['level_num'].values, (25 - len(skills_joined.values), 0), mode='empty').reshape(5, 5)


    # df_merged = pd.concat(np.array_split(skills_joined, 5), ignore_index=True, sort=False)


    # events_df = events_df.rename(columns={"date": "start", "description": "content"})



    def get_color(attribute, value):
        if attribute == 'rage':
            if value < 20:
                return '#FF2400'
            elif value > 80:
                return '#CC0000'
            else:
                return '#B7410E'
        else:
            if value < 20:
                return colors[0]
            elif value > 60:
                return colors[1]
            else:
                return colors[2]

    events_list = []

    for event in  events_filtered_df.values.tolist():
        events_list.append({"start": event[1], "content": event[2]})


    # st.write("## My timeline")
    timeline_expander = st.expander("## Timeline")
    timeline_expander.write('''
                            My timeline. These moments are the "peaks" of my life. 
                            ''')
    timeline = st_timeline(events_list, groups=[], options={}, style='timeline.css', height="300px")
    # timeline = st_timeline(events_list, groups=[], options={}, height="300px")

    

    colors = ['#EA580C', '#CCFBFE', '#CDD6DD', '#CDCACC', '#3D405B']

    custom_cmap = ListedColormap(colors)

    cmap = mpl.colors.LinearSegmentedColormap.from_list("my color", colors, N=256)

    norm = mpl.colors.Normalize(vmin=5, vmax=5)

    # colors_normalized = cmap(norm())


    cmap = plt.cm.get_cmap('flare', 5)  # 5 discrete colors


    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(matrix, annot=False, cmap=custom_cmap, cbar=False, ax=ax)


    sm = plt.cm.ScalarMappable(cmap=custom_cmap, norm=plt.Normalize(vmin=0.5, vmax=5.5))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, ticks=[1, 2, 3, 4, 5])
    cbar.set_ticklabels(['Beginner', 'Advanced Beginner', 'Competent', 'Proficient', 'Expert'])
    cbar.set_label('Expertise Level')


    for i in range(5):
        for j in range(5):
            idx = i * 5 + j
            if idx < len(skills_joined):
                ax.text(j + 0.5, i + 0.5, skills_joined.iloc[idx]['name'], 
                        ha='center', va='center', fontsize=8)

    # plt.title('Skills Level')

    ax.set_xticks([])
    ax.set_yticks([])
    heatmap_expander = st.expander("Skill levels")
    heatmap_expander.write('''
                           The accumulation of my skills through time. The levels are also listed. Only the last 25 skills are shown.
                           ''')
    st.pyplot(fig)
    ## Variable setup for attrs
    num_attributes = len(attrs_avg_df.columns)



    angles = np.linspace(0, 2 * np.pi, num_attributes, endpoint=False).tolist()
    values = attrs_avg_df.values.tolist()[0]
    values_avg = attrs_avg_df_overall.values.tolist()[0]
    bar_colors = [get_color(attr, value) for attr, value in zip(attrs_avg_df.columns.tolist(), values)]
    values += values[:1]
    values_avg += values_avg[:1]
    angles += angles[:1]







    radarFig, radarAx = plt.subplots(figsize=(9, 6), subplot_kw={"projection": "polar"})

    radarFig.patch.set_facecolor("white")
    radarAx.set_facecolor("white")



    # radarAx.set_theta_offset(1.2 * np.pi / 2)
    radarAx.set_ylim(0, 100)

    radarAx.bar(angles, values, color=bar_colors, bottom=20, alpha=0.9, width=0.9, zorder=10)
    radarAx.vlines(angles, 0, 100, color='grey', ls=(0, (4, 4)), zorder=11)
    radarAx.scatter(angles, values_avg, s=60, color="#1f1f1f", zorder=11)


    radarAx.set_yticklabels([])
    radarAx.set_xticks(angles[:-1])


    regions = ["\n".join(wrap(r, 5, break_long_words=False)) for r in attrs_avg_df.columns]
    radarAx.set_xticklabels(regions)



    radial_expander = st.expander("Attributes")
    radial_expander.write('''
                          A collective list of my attributes through out time. The rating is pretty arbitrary but I feel are fairly accurate if not looked
                          at as numbers & more as levels.
                          ''')
    st.pyplot(radarFig)

   



 