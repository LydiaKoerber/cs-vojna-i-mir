import ast
import os
import re

import pandas as pd

import langdetect
import spacy

# load the spaCy models
nlp_ru = spacy.load("ru_core_news_sm")
nlp_fr = spacy.load("fr_core_news_sm")
nlp_mul = spacy.load("xx_sent_ud_sm")



def process_cs(corpus, output='outputs/cs_.csv'):
    column_names = ['text', 'switch_len', 'pos', 'lemma', 'dep', 'morph']
    data = []
    corpus['cs_indices'] = corpus['cs_indices'].apply(ast.literal_eval)
    corpus['tokens'] = corpus['tokens'].apply(ast.literal_eval)
    corpus['cs'] = corpus['cs'].apply(ast.literal_eval)
    for i, line in corpus.iterrows():
        try:
            for switch in parse_line(line):
                data.append([line.tokens] + list(switch))
        except Exception as e:
            print(line.tokens, e)
    df = pd.DataFrame(data, columns=column_names)

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
    if df['cs_indices'] != []:
        for snippet, cs in zip(split_list_at_indices(tokens, df['cs_indices']),
                            split_list_at_indices(df['cs'], df['cs_indices'])):
            # language detection
            if 'ru' in cs:
                lang = 'ru'
            else:  # language detection
                lang = langdetect.detect(' '.join(snippet))
                if not lang == 'fr':
                    # language other than french
                    print(lang, snippet, cs)
                    continue
            snippets.append(process_snippet(snippet, lang))
    else:
        if df['maj_lang'] == 'ru':
            lang = 'ru'
        else:  # language detection
            lang = langdetect.detect(' '.join(tokens))
            if not lang == 'fr':
                # language other than french
                print(lang, tokens, df.cs)
        snippets.append(process_snippet(tokens, lang))
    return snippets


def process_snippet(tokens, lang):
    """extract linguistic information from a CS snippet"""
    text = ' '.join(tokens)
    if lang == 'ru':
        doc = nlp_ru(text)
    elif lang == 'fr':
        doc = nlp_fr(text)
    else:
        doc = nlp_fr(text)
    # PoS, NER
    pos, lemma, dep, morph = [], [], [], []
    for token in doc:
        pos.append(token.pos_)
        lemma.append(token.lemma_)
        dep.append(token.dep_)
        morph.append(token.morph)
    switch_len = len(tokens)
    return switch_len, pos, lemma, dep, morph


if __name__ == '__main__':
    output_dir = '../outputs/'
    for f in sorted(os.listdir(output_dir)):
        df = pd.read_csv(output_dir+f)
        process_cs(df)
        break
