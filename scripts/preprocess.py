import os
import re

import pandas as pd
import spacy


nlp_mul = spacy.load("xx_sent_ud_sm")


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

def has_latin(text):
    return bool(re.search('[a-zA-Z]', text))


def create_df(data, output_path='../outputs/'):
    column_names = []
    df = pd.DataFrame(columns=column_names)
    if output_path:
        df.to_csv(output_path, encoding='utf-8')

def parse_file(path):
    """parse corpus file"""
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
        # ignore footnotes in the end
        text = text.split('↑ ')[0]
        # split by parts and chapters
        parts = re.split(r'ЧАСТЬ \w+Я\.\n', text)[1:]
        chapters = []
        for i, p in enumerate(parts):
            part_number = i + 1
            if not p or not re.match('\s+', p):
                continue
            chapters = [x for x in re.split(r'\n[XVIM]+\.\n', p) if re.match('\s+', x)]
            # chapters.append(chapters_new)
            print(len(chapters))
            for j, c in enumerate(chapters):
                chapter_number = j + 1
                lines = c.split('\n\n')
                for l in lines:
                    parse_line(l)


def tokenize(line):
    return

def parse_line(l):
    pass


if __name__ == '__main__':
    corpus_dir = '../corpus/'
    for f in sorted(os.listdir(corpus_dir)):
        print(f)
        parse_file(corpus_dir+f)
        break
