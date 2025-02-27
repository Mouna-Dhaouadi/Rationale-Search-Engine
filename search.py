import streamlit as st
import pandas as pd
import os
from utils import *

# Page setup
st.set_page_config(page_title="Rationale Search Engine", layout="wide")
st.title("Rationale Search Engine")

module = mocule_selector()
sim_file, cont_file, incon_m1_file, incon_m2_file = files_selector(module)
st.divider()

##### 1.  Similarities
st.subheader('Similarities')
st.write('Similarities_file `%s`' % sim_file)
sim_file_path = os.path.join(module, sim_file)

df_sim = pd.read_csv(sim_file_path, sep=';', dtype=str)
df_sim.drop("Unnamed: 0",axis=1, inplace=True)
st.write(df_sim)

col1, col2 = st.columns(2, border=True)

# Search decisions
col1_1, col1_2 = col1.columns(2)
text_search_d_sim = col1_1.text_input("Search Similar decisions (exact match)", value="")
threshold_d_sim = col1_2.text_input("Threshold for Similar decisions (Alpha)", value="0.5")
m1_d_sim = df_sim["Decision1"].str.contains(text_search_d_sim)
m2_d_sim = df_sim["Decision2"].str.contains(text_search_d_sim)
df_search_d_sim = df_sim[ (m1_d_sim | m2_d_sim)  & (df_sim["Alpha"] >= threshold_d_sim) ]
if text_search_d_sim:
    col1.write(df_search_d_sim)


# Search Rationales
text_search_r_sim = col2.text_input("Search rationales (exact match)", value="")
m1_r_sim = df_sim["Rationale1"].str.contains(text_search_r_sim)
m2_r_sim = df_sim["Rationale2"].str.contains(text_search_r_sim)
df_search_r_sim = df_sim[ m1_r_sim | m2_r_sim ]
if text_search_r_sim:
    col2.write(df_search_r_sim)


###########################################################################
st.divider()

##### 2. Contradictions
st.subheader('Contradictions')
st.write('Contradictions_file `%s`' % cont_file)
cont_file_path = os.path.join(module, cont_file)

df_cont = pd.read_csv(cont_file_path, sep=';', dtype=str)
df_cont.drop("Unnamed: 0",axis=1, inplace=True)
st.write(df_cont)

col3, col4 = st.columns(2, border=True)

# Search decisions
col3_1, col3_2 = col3.columns(2)
text_search_d_cont = col3_1.text_input("Search Contradictory decisions (exact match)", value="")
threshold_d_cont = col3_2.text_input("Threshold for Contradictory decisions (Alpha)", value="0.5")
m1_d_cont = df_cont["Decision1"].str.contains(text_search_d_cont)
m2_d_cont = df_cont["Decision2"].str.contains(text_search_d_cont)
df_search_d_cont = df_cont[ (m1_d_cont | m2_d_cont) &  (df_cont["Alpha"] >= threshold_d_cont) ]
if text_search_d_cont:
    col3.write(df_search_d_cont)

# Search Rationales
text_search_r_cont = col4.text_input("Search their rationales (exact match)", value="")
m1_r_cont = df_cont["Rationale1"].str.contains(text_search_r_cont)
m2_r_cont = df_cont["Rationale2"].str.contains(text_search_r_cont)
df_search_r_cont = df_cont[m1_r_cont | m2_r_cont]
if text_search_r_cont:
    col4.write(df_search_r_cont)



###########################################################################
st.divider()

##### 3. Inconsistencies
st.subheader('Inconsistencies')

###############
m1_container = st.container(border=True)
m1_container.subheader('M1 mechanism')
m1_container.markdown(' **Similar** Decisions But **Contradictory** Rationales')
m1_container.write('Inconsistencies_M1_file `%s`' % incon_m1_file)
incon_m1_file_path = os.path.join(module, incon_m1_file)
df_incon_m1 = pd.read_csv(incon_m1_file_path, sep=';', dtype=str)
df_incon_m1.drop(columns= {'similarity_rationales'}, inplace = True)
df_incon_m1.drop("Unnamed: 0",axis=1, inplace=True)
df_incon_m1.rename(columns= {'contradiction_rationales':'contradiction_rationales (Beta)'}, inplace = True)

col5, col6 = m1_container.columns(2)

threshold_d_sim_m1 = col5.text_input("Threshold for Similar decisions (Alpha)", value="0.8")
threshold_r_cont_m1 = col6.text_input("Threshold for Contradictory rationales (Beta)", value="0.6")

df_incon_m1 = df_incon_m1[  (df_incon_m1["Alpha"] >= threshold_d_sim_m1)  &  (df_incon_m1["contradiction_rationales (Beta)"] >= threshold_r_cont_m1)  ]

m1_container.write("Number of inconsistencies detected (M1): " + str( len(df_incon_m1))  )
m1_container.write(df_incon_m1)


###############
m2_container = st.container(border=True)
m2_container.subheader('M2 mechanism')
m2_container.markdown('**Contradictory** Decisions But **Similar** Rationales')
m2_container.write('Inconsistencies_M2_file `%s`' % incon_m2_file)
incon_m2_file_path = os.path.join(module, incon_m2_file)
df_incon_m2 = pd.read_csv(incon_m2_file_path, sep=';', dtype=str)
df_incon_m2.drop("Unnamed: 0",axis=1, inplace=True)
# Rename column for consistency
df_incon_m2.rename(columns= {'similarity_rationales':'similarity_rationales (Beta)'}, inplace = True)

col7, col8 = m2_container.columns(2)
threshold_d_cont_m2 = col7.text_input("Threshold for Contradictory decisions (Alpha)", value="0.8")
threshold_r_sim_m2 = col8.text_input("Threshold for Similar rationales (Beta)", value="0.6")

df_incon_m2 = df_incon_m2[  (df_incon_m2["Alpha"] >= threshold_d_cont_m2)  &  (df_incon_m2["similarity_rationales (Beta)"] >= threshold_r_sim_m2)  ]

m2_container.write("Number of inconsistencies detected (M2): " + str( len(df_incon_m2))  )
m2_container.write(df_incon_m2)

