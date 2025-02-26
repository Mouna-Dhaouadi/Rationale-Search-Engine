import os
import streamlit as st
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from transformers import pipeline


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


def triples_files_selector(module_path):
    file_names = os.listdir(module_path)
    triples_file = next((f for f in file_names if f.startswith("ChatGPT_decision_rationale")), None) 
    return triples_file 


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


def construct_propmt_2(module, user_input, contradictory_decisions): 
    prompt = """
            You are a experienced developer of the {module} module. 
            You answer in very short sentences and do not include extra information.
            This is the proposed commit: {user_input}
            These are some potenial contradictory previous decisions: {contradictory_decisions}
            Based ONLY on these relevant previous decisions and the user proposed commit, answer the following question: 
                Is the proposed commit conflicting with these previous decisions ? 
                Answer globally, then for each decision, write its Github URL and explain why or why not it is not conflicting with the new commit. 
            """
    return prompt.format(user_input=user_input, contradictory_decisions=contradictory_decisions, module = module)


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

    triples_df = pd.read_csv(triples_file_path, sep=';', dtype=str)
    text_url_df = triples_df[['Decision','Rationale', 'url']].copy()
    text_url_df['text'] = text_url_df['Decision'].astype(str) +" "+ text_url_df["Rationale"].astype(str)
    
    corpus = list( text_url_df["text"] )
    doc_embeddings = model.encode(corpus)

    query_embedding = model.encode([user_input])
    similarities = cosine_similarity(query_embedding, doc_embeddings)

    sorted_indices = sorted(enumerate(similarities[0]), key=lambda x: x[1], reverse=True)
    
    relevant_scores = [ score for idx, score in sorted_indices if score >= float(similarity_threshold) ]
    relevant_changes = [text_url_df.iloc[idx]['url'] for idx, score in sorted_indices if score >= float(similarity_threshold)]
    relevant_text = [text_url_df.iloc[idx]['text'] for idx, score in sorted_indices if score >= float(similarity_threshold)]

    relevant_changes_df = pd.DataFrame(data={'Commit': relevant_text, 'Url': relevant_changes , 'Alpha': relevant_scores })

    return  relevant_changes_df


def get_contradictory_changes(user_input, triples_file_path, contradiction_threshold):
    pipe = pipeline( model="roberta-large-mnli")

    triples_df = pd.read_csv(triples_file_path, sep=';', dtype=str)
    text_url_df = triples_df[['Decision','Rationale', 'url']].copy()
    text_url_df['text'] = text_url_df['Decision'].astype(str) +" "+ text_url_df["Rationale"].astype(str)
    previous_commits_list = list (text_url_df['text'])

    # Concatenate the sentences and get predictions
    # sentence_pairs = str(sentence1 + sentence2)
    decision_pairs = [ str(text + user_input) for text in previous_commits_list]
    predictions = pipe(decision_pairs)

    contradictory_commits = []
    contradictory_changes = []
    contradictions_scores = []
    for ind, pair in enumerate(decision_pairs):
    # Extract prediction +  score
      label = predictions[ind]['label']
      score = predictions[ind]['score']
      commit = pair.removesuffix(user_input)

      if label == 'CONTRADICTION' and score >= float(contradiction_threshold):
          contradictory_changes.append(text_url_df['url'][ind])   
          contradictions_scores.append(float(score))
          contradictory_commits.append(commit)

    contradictory_changes_df = pd.DataFrame(data= {'Commit' : contradictory_commits , 'Url':contradictory_changes, 'Alpha':contradictions_scores} )
    sorted_df = contradictory_changes_df.sort_values(by=['Alpha'], ascending=False) 
    return  sorted_df
      