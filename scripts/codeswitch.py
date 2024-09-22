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

def process_snippet(tokens, lang):
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

