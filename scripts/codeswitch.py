import os
import re

import pandas as pd

import spacy

# load the spaCy models
nlp_ru = spacy.load("ru_core_news_sm")
nlp_fr = spacy.load("fr_core_news_sm")

def process_cs(corpus, output='outputs/cs_.csv'):
    df = pd.DataFrame(columns=['line_index', 'inter-turn', 'inter-sent', 'intra-sent', 'ML', 'EL'])
    for line in corpus:
        cs = corpus['cs']
        if 'non-ru' in cs:
            pass
        new_line = [line.index]


def process_line(line):
    data = []
    for i in line.len_sents:
        # iterate sentences, parse multilingual parts
        current_lang = ''
        snippet = []
        for token, cs in zip(line.text, line.cs):
            if cs == '':
                snippet.appen(token)
                continue
            if current_lang != cs:  # snippet finalized
                data.append(process_snippet(snippet, current_lang))
                snippet = []
                current_lang = cs
            snippet.append(token)
    return data


def process_snippet(tokens, lang):
    """extract linguistic information from a CS snippet"""
    text = ' '.join(tokens)
    if lang == 'ru':
        doc = nlp_ru(text)
    elif lang == 'fr':
        doc = nlp_fr(text)
    # PoS, NER
    pos, lemma, dep, morph = [] * 4
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
