import os
import streamlit as st


def mocule_selector(folder_path='./Sources_with_URL/Modules'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a Module', filenames)
    return os.path.join(folder_path, selected_filename)


def files_selector(module_path):
    file_names = os.listdir(module_path)
    sim_file = next((f for f in file_names if f.startswith("similarities")), None)
    cont_file = next((f for f in file_names if f.startswith("contradictions")), None)
    incon_m1_file = next((f for f in file_names if f.startswith("inconsistencies_mechanism1")), None)
    incon_m2_file = next((f for f in file_names if f.startswith("inconsistencies_mechanism2")), None)
    return sim_file, cont_file, incon_m1_file, incon_m2_file  
