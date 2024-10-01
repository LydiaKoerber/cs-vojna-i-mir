import ast
import os
import re

import pandas as pd

import langdetect
import spacy

# load the spaCy models
nlp_ru = spacy.load("ru_core_news_sm")
nlp_fr = spacy.load("fr_core_news_sm")
nlp_de = spacy.load("de_core_news_sm")



def process_cs(corpus):
    """compute features for all intrasentential switches in corpus"""
    column_names = ['text', 'switch_len', 'pos', 'lemma', 'dep', 'morph', 'lang', 'position']
    data = []
    corpus['cs_indices'] = corpus['cs_indices'].apply(ast.literal_eval)
    corpus['tokens'] = corpus['tokens'].apply(ast.literal_eval)
    corpus['cs'] = corpus['cs'].apply(ast.literal_eval)
    for _, line in corpus.iterrows():
        try:
            for switch in parse_line(line):
                data.append(list(switch))
        except Exception as e:
            print(line.tokens, e)
    df = pd.DataFrame(data, columns=column_names)
    return df

def split_list_at_indices(lst, indices):
    # Sort the indices to ensure they are in the correct order
    indices = sorted(indices)
    
    # Initialize the start of the first sublist
    start = 0
    sublists = []

    # Iterate over each index and split the list accordingly
    for index in indices:
        sublists.append(lst[start:index])
        start = index

    # Append the remainder of the list as the last sublist
    sublists.append(lst[start:])
    
    return sublists


def parse_line(df):
    tokens = df.tokens
    snippets = []
    # check intrasentential
    if df['cs_indices'] != []:
        i = 0
        tokenlists = split_list_at_indices(tokens, df['cs_indices'])
        cslists = split_list_at_indices(df['cs'], df['cs_indices'])
        for snippet, cs in zip(tokenlists, cslists):
            # language detection
            if 'ru' in cs:
                lang = 'ru'
            else:  # language detection
                lang = langdetect.detect(' '.join(snippet))
            if i == 0:
                position = 'bos'
            elif i == len(tokenlists) - 1:
                position = 'eos'
            else:
                position = 'mid'
            snippets.append(list(process_snippet(snippet, lang))+[position])
            i += 1
    return snippets


def process_snippet(tokens, lang):
    """extract linguistic information from a CS snippet"""
    text = ' '.join(tokens)
    if lang == 'ru':
        doc = nlp_ru(text)
    elif lang == 'fr':
        doc = nlp_fr(text)
    elif lang == 'de':
        doc = nlp_de(text)
    else:  # probably misparsed french
        doc = nlp_fr(text)
    # PoS, lemmata, dependency and morphologic information
    pos, lemma, dep, morph = [], [], [], []
    for token in doc:
        pos.append(token.pos_)
        lemma.append(token.lemma_)
        dep.append(token.dep_)
        morph.append(token.morph)
    switch_len = len(tokens)
    return tokens, switch_len, pos, lemma, dep, morph, lang


if __name__ == '__main__':
    output_dir = '../outputs/'
    dfs = []
    for f in sorted(os.listdir(output_dir)):
        if not f.startswith('cs_'):
            continue
        df = pd.read_csv(output_dir+f)
        dfs.append(process_cs(df))
        break
    combined_dfs = pd.concat(dfs)
    combined_dfs.to_csv('../outputs/features.csv')
