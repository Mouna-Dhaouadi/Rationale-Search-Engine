import os
import streamlit as st
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


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
    triples_file = next((f for f in file_names if f.startswith("ChatGPT_decision_rationale")), None) 
    print(triples_file)
    return sim_file, cont_file, incon_m1_file, incon_m2_file, triples_file 


def construct_propmt(module, user_input, relevant_decisions):
    prompt = """
            You are a experienced developer of the {module} module. 
            You answer in very short sentences and do not include extra information.
            This is the proposed commit: {user_input}
            These are some relevant previous decisions: {relevant_decisions}
            Based ONLY on these relevant previous decisions and the user proposed commit, answer the following questions: 
            1. Has this exact decision been done before? If yes, provide the Github URL to the previous exact chnage.
            2. Has something similar been done before? If yes, 
                Compile a concise summary of all similar decisions together, then,  
                Write a summary for each of the similar decisions and provide its Github URL.
            """
    return prompt.format(user_input=user_input, relevant_decisions=relevant_decisions, module = module)


def ask_llm(user_input, prompt):
    secret_key = st.secrets["secret_key"]
    client = OpenAI(api_key=secret_key)
    completion = client.chat.completions.create(
      model =  "gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": prompt },
      ]
    )
    response = completion.choices[0].message.content
    return response


def get_relevant_changes(user_input, triples_file_path, similarity_threshold):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    relevant_changes = []

    triples_df = pd.read_csv(triples_file_path, sep=';', dtype=str)
    text_url_df = triples_df[['Decision','Rationale', 'url']].copy()
    text_url_df['text'] = text_url_df['Decision'].astype(str) +" "+ text_url_df["Rationale"].astype(str)
    
    corpus = list( text_url_df["text"] )
    doc_embeddings = model.encode(corpus)

    query_embedding = model.encode([user_input])
    similarities = cosine_similarity(query_embedding, doc_embeddings)

    sorted_indices = sorted(enumerate(similarities[0]), key=lambda x: x[1], reverse=True)
    relevant_changes = [text_url_df.iloc[idx]['url'] for idx, score in sorted_indices if score >= float(similarity_threshold)]

    return  relevant_changes