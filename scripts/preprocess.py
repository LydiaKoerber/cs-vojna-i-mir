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
    column_names = ['volume', 'part', 'chapter', 'text', 'cs',
                    'num-switches-intraturn', 'num-switches-interturn',
                    'num-switches-intrasent']
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
            chapters = [x for x in re.split(r'\n[XVIM]+\.\n', p) if re.match('\s+', x)]
            # chapters.append(chapters_new)
            for j, c in enumerate(chapters):
                if c.strip() == "": 
                    continue
                speaker, letter = False, False
                chapter_number = j
                lines = c.split('\n\n')
                for l in lines:
                    tokens, cs, num_intrasent = parse_line(l)#, speaker=speaker, letter=letter)
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
                                    tokens, cs, num_intra_turn_switches,
                                    num_inter_turn_switches, num_intrasent])
    create_df(data, volume_number)
    return data


def parse_line(l, nlp=nlp_mul):
    tokens, cs = [], []
    # remove footnote markers, e.g. [8]
    l = re.sub(r"\[\d+\]", "", l)
    parsed = nlp(l)
    num_intrasent = 0
    for sent in parsed.sents:
        sent_txt = ' '.join([token.text for token in sent])
        if has_cyrillic(sent_txt) and has_latin(sent_txt):
            num_intrasent += 1
        for token in sent:
            tokens.append(token.text)
            if has_cyrillic(token.text):
                cs.append('ru')
            # TODO actual lang detect
            elif has_latin(token.text):
                cs.append('non-ru')
            else:
                cs.append('')

    no_tokens = len(tokens)
    
    return tokens, cs, num_intrasent


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
