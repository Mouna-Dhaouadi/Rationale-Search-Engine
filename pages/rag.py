import streamlit as st
import pandas as pd
import os
from utils import *


# Page setup
st.set_page_config(page_title="Rationale RAG", layout="wide")
st.title("Rationale RAG")


module = mocule_selector()
triples_file = triples_files_selector(module)
triples_file_path = os.path.join(module, triples_file)
st.write('Triples_file `%s`' % triples_file)

###################################
user_input = st.text_input("Enter your commit", value="")

#####################################
# Similar RAG - new commit
cols_llm = st.container(border=True)
cols_llm.subheader('Similar commits')
similarity_threshold = cols_llm.text_input("Enter the cosine similarity threshold:", value=0.4)

if user_input:
    relevant_decisions = get_relevant_changes(user_input, triples_file_path, similarity_threshold)
    cols_llm.write('%s similar commits' % len(relevant_decisions))
    cols_llm.write( relevant_decisions)

    cols_llm.subheader('Get ChatGPT to double check these similar commits')
    context_size = cols_llm.text_input("Enter the size of your context (number of similar commits for ChatGPT to consider):", value=5)

    prompt = construct_propmt(module, user_input, relevant_decisions[:int(context_size)])
    response = ask_llm(user_input, prompt)
    cols_llm.write(response)


#####################################
# contradictions RAG - new commit
cols_llm_2 = st.container(border=True)
cols_llm_2.subheader('Potenial conflicting commits')
contradiction_threshold = cols_llm_2.text_input("Enter the contradiction threshold:", value=0.4)

if user_input:
    with st.spinner("Wait for it...", show_time=True):
        contradictory_decisions = get_contradictory_changes(user_input, triples_file_path, contradiction_threshold)
        
    cols_llm_2.write('%s contradictory commits' % len(contradictory_decisions))
    cols_llm_2.write( contradictory_decisions)

    cols_llm_2.subheader('Get ChatGPT to double check these contradictory commits')
    context_size = cols_llm_2.text_input("Enter the size of your context (number of contradictory commits for ChatGPT to consider):", value=5)

    prompt = construct_propmt_2(module, user_input, contradictory_decisions[:int(context_size)])
    response = ask_llm(user_input, prompt)
    cols_llm_2.write(response)