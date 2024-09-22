import os
import re

import pandas as pd
import spacy


nlp_mul = spacy.load("xx_sent_ud_sm")


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

def has_latin(text):
    return bool(re.search('[a-zA-Z]', text))


def create_df(data, part_number, output_dir='../outputs/'):
    column_names = ['volume', 'part', 'chapter', 'text', 'number_tokens', 'cs',
                    'num-switches-intraturn', 'num-switches-interturn',
                    'num-switches-intrasent', 'num-switches-intraword', 
                    'num_sent', 'len_sents', 'len_cs_fr', 'len_cs_ru']
    df = pd.DataFrame(data, columns=column_names)
    if output_dir:
        df.to_csv(f'{output_dir}cs_{part_number}.csv', encoding='utf-8')


def parse_file(path):
    """parse corpus file"""
    data = []
    volume_number = path.split('(Толстой)_')[1].strip('.txt')
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
        # ignore footnotes in the end
        text = text.split('↑ ')[0]
        # split by parts and chapters
        parts = re.split(r'ЧАСТЬ \w+Я\.\n', text)[1:]
        chapters = []
        for i, p in enumerate(parts):
            if p.strip() == "": 
                continue
            part_number = i + 1
            chapters = [x for x in re.split(r'\n[XVIM]+\.\n', p)
                        if re.match('\s+', x) and x.strip() != ""]
            # chapters.append(chapters_new)
            for j, c in enumerate(chapters):
                # if c.strip() == "": 
                #     continue
                # prevent 0-indexing
                chapter_number = j + 1
                lines = c.split('\n\n')
                for l in lines:
                    tokens, cs, num_intrasent, num_intraword, num_sent, len_sents, len_cs_fr, len_cs_ru, no_tokens = parse_line(l)#, speaker=speaker, letter=letter)
                    # include CS instances only
                    if 'non-ru' in cs:
                        num_intra_turn_switches = 0
                        num_inter_turn_switches = 0
                        lang = ''
                        for s in cs:
                            if not s:  # empty string, punctuation or other
                                continue
                            if s != lang:
                                if not lang == '':
                                    num_intra_turn_switches += 1
                                lang = s
                        if num_intra_turn_switches == 0:
                            num_inter_turn_switches = 1
                        data.append([volume_number, part_number, chapter_number,
                                    tokens, no_tokens, cs, num_intra_turn_switches,
                                    num_inter_turn_switches, num_intrasent,
                                    num_intraword, num_sent, len_sents,
                                    len_cs_fr, len_cs_ru])
    create_df(data, volume_number)
    return data


def parse_line(l, nlp=nlp_mul):
    tokens, cs = [], []
    # remove footnote markers, e.g. [8]
    l = re.sub(r"\[\d+\]", "", l)
    parsed = nlp(l)
    num_intrasent, num_intraword, num_sent = 0, 0, 0
    len_sents = []
    len_cs_fr, len_cs_ru = [], []
    lcsf, lcsr = 0, 0
    for sent in parsed.sents:
        num_sent += 1
        len_sents.append(len(sent))
        sent_txt = ' '.join([token.text for token in sent])
        if has_cyrillic(sent_txt) and has_latin(sent_txt):
            num_intrasent += 1
        for token in sent:
            tokens.append(token.text)
            if has_cyrillic(token.text) and has_latin(token.text):
                num_intraword += 1
                print(token.text, sent_txt)
            if has_cyrillic(token.text):
                cs.append('ru')
                lcsr += 1
                if lcsf != 0:
                    len_cs_fr.append(lcsf)
                lcsf = 0
            # TODO actual lang detect
            elif has_latin(token.text):
                cs.append('non-ru')
                lcsf += 1
                if lcsr != 0:
                    len_cs_ru.append(lcsr)
                lcsr = 0
            else:
                cs.append('')
    last_language = next((item for item in reversed(cs) if item != ''), None)
    if lcsf != 0 and last_language == 'non-ru':
        len_cs_fr.append(lcsf)
    if lcsr != 0 and last_language == 'ru':
        len_cs_ru.append(lcsr)
    no_tokens = len(tokens)

    assert sum(len_cs_fr) + sum(len_cs_ru) == no_tokens - cs.count('')
    return tokens, cs, num_intrasent, num_intraword, num_sent, len_sents, len_cs_fr, len_cs_ru, no_tokens

# TODO cs instanzen nach länge auszählen und dann POS/DEP kombis vergleichen

def detect_direct_speech(tokens):
    ds = []
    if tokens[0] == '«':
        pass
    return ds


def tokenize(line):
    return



if __name__ == '__main__':
    corpus_dir = '../corpus/'
    for f in sorted(os.listdir(corpus_dir)):
        print(f)
        parse_file(corpus_dir+f)
