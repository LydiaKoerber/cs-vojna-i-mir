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
    column_names = ['volume', 'part', 'chapter', 'text', 'cs', 'ds']
    df = pd.DataFrame(data, columns=column_names)
    if output_dir:
        df.to_csv(f'{output_dir}part_{part_number}.csv', encoding='utf-8')


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
                    tokens, ds, cs, speaker, letter = parse_line(l, speaker=speaker, letter=letter)
                    data.append([volume_number, part_number, chapter_number,
                                 tokens, cs, ds])
    create_df(data, volume_number)
    return data


def parse_line(l, speaker=False, letter=False, nlp=nlp_mul):
    tokens, ds, cs = [], [], []
    # simple white space tokenization?
    parsed = nlp(l)
    for sent in parsed.sents:
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
    # detect direct speech
    if '—' in tokens and (not ' — ' in l or ', — ' in l):  # ignore hyphen for emphasis
        switches = tokens.count('—')
        if switches == 1 and l.startswith('— '):
            # turn is direct speech only
            ds = ['—'] + [1 for i in range(no_tokens - 1)]
        else:
            # bool to keep track
            speaker = False
            # iterate tokens
            for i, t in enumerate(tokens):
                if t == '—' and (i == 0 or tokens[i-1] == ','):
                    ds.append('—')
                    # change bool
                    speaker = not speaker
                else:
                    if speaker:  # speaker
                        ds.append(1)
                    else:  # narrator
                        ds.append(0)

    if '«' in l:
        # start of a letter / written correspondence
        # OR singing
        # whole line correspondence
        if l.startswith('«') and (l.endswith('»') or '»' not in l):
            ds = ['«'] + [2 for i in range(no_tokens - 1)]
            if '»' in l:
                letter = False
            else:
                # letter continues in next line
                letter = True
        # switch to narrator
        elif '»,' in l:
            letter = False
            for t in tokens:
                if t == '«':
                    ds.append('«')
                    letter = True
                elif t == '»':
                    ds.append('»')
                    letter = False
                else:
                    if letter:
                        ds.append(2)
                    else:
                        ds.append(0)
    # narrator voice only
    if not ds:
    # any(x in l for x in {'—','«', '»'}) and not speaker and not letter:
        ds = [0 for i in range(no_tokens)]

    # detect direct speech
    if not len(tokens) == len(ds) == len(cs):
        print(l)
    return tokens, ds, cs, speaker, letter



def tokenize(line):
    return



if __name__ == '__main__':
    corpus_dir = '../corpus/'
    for f in sorted(os.listdir(corpus_dir)):
        print(f)
        parse_file(corpus_dir+f)
        break
