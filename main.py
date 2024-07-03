import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import duckdb

import matplotlib.cm
from streamlit_timeline import st_timeline

st.set_page_config(layout="wide")


con = duckdb.connect(database = "./data/my-db.db", read_only = False)


events_rel = con.sql("SELECT * FROM events").set_alias("events_rel")
events_df = events_rel.df()
events_df = events_df.drop(['id'], axis=1)
events_df['date'] = events_df['date'].dt.strftime('%Y-%m-%d')

attrs_rel = con.sql("SELECT * FROM attributes").set_alias("attrs_rel")
attrs_joined = events_rel.join(attrs_rel, "events_rel.id = attrs_rel.event_id")

skills_joined = con.execute("""WITH ranked_skills AS ( 
                           SELECT s.id, s.name, s.level, e.date, ROW_NUMBER() OVER (PARTITION BY s.name ORDER BY e.date DESC) AS rn 
                           FROM skills s 
                           JOIN events e 
                           ON s.event_id = e.id WHERE e.date <= DATE '2024-06-30' 
                           ) 
                           SELECT id, name, level, date 
                           FROM ranked_skills 
                           WHERE rn = 1 
                           ORDER BY name""").df()

level_dict = {'Beginner': 0, 'Advanced Beginner': 1, 'Competent': 2, 'Proeficient': 3, 'Expert': 4}

skills_joined['level_num'] = skills_joined['level'].map(level_dict)


# heatmap_data = skills_joined.pivot(index='name', columns='level', values='num_level')

matrix = skills_joined['level_num'].values.reshape(5, 5)


# df_merged = pd.concat(np.array_split(skills_joined, 5), ignore_index=True, sort=False)


# events_df = events_df.rename(columns={"date": "start", "description": "content"})



events_list = []

for event in  events_df.values.tolist():
    events_list.append({"start": event[0], "content": event[1]})




cmap = plt.cm.get_cmap('flare', 5)  # 5 discrete colors


fig, ax = plt.subplots(figsize=(6, 5))

sns.heatmap(matrix, annot=False, cmap=cmap, cbar=False, ax=ax)


sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0.5, vmax=5.5))
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

plt.title('Skills Level')

ax.set_xticks([])
ax.set_yticks([])

# st.pyplot(fig)


col1, col2, col3, = st.columns([1, 2, 1])
with col2:
    st.write("## My timeline")
    timeline = st_timeline(events_list, groups=[], options={}, style='timeline.css', height="300px")
    st.pyplot(fig)


# st.subheader("event")

# st.write(timeline)
