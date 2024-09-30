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
    column_names = ['volume', 'part', 'chapter', 'paragraph', 'num_sent', 'num_interturn', 'num_intersent',
                                    'tokens', 'len_sent', 'cs', 'cs_indices', 'num_intrasent', 'maj_lang', 'first_lang', 'last_lang', 'embedded']
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
            for j, c in enumerate(chapters):
                # prevent 0-indexing
                chapter_number = j + 1
                lines = c.split('\n\n')
                for i, l in enumerate(lines):
                    num_interturn = 0
                    sents, num_sent, num_intersent = parse_sents(l.strip())
                    # tokens, cs, num_intrasent, num_intraword, num_sent, len_sents, len_cs_fr, len_cs_ru, no_tokens = parse_line(l)
                    # include CS instances only
                    for j, sent in enumerate(sents):
                        tokens, cs, cs_indices, maj_lang, len_sent, first_lang, last_lang, num_intrasent = sent
                        if j == 0 and data:
                            # check last language of previous turn to detect
                            # inter-turn switches
                            if data[-1][-1] != first_lang:
                                num_interturn += 1
                        if first_lang == last_lang and num_intrasent > 1:
                            embedded = True
                        else:
                            embedded = False
                        data.append([volume_number, part_number, chapter_number, i, num_sent, num_interturn, num_intersent,
                                    tokens, len_sent, cs, cs_indices, num_intrasent, maj_lang, first_lang, last_lang, embedded])
    create_df(data, volume_number)
    return data


def parse_sents(s, nlp=nlp_mul):
    tokens, cs, cs_indices = [], [], []
    sents = []
    # remove footnote markers, e.g. [8]
    s = re.sub(r"\[\d+\]", "", s)
    parsed = nlp(s)
    num_sent = 0
    num_intersent = 0
    for sent in parsed.sents:
        num_intrasent = 0
        num_sent += 1
        len_sent = len(sent)
        current_lang = ''
        for i, token in enumerate(sent):
            tokens.append(token.text)
            if has_cyrillic(token.text):
                cs.append('ru')
            # TODO actual lang detect
            elif has_latin(token.text):
                cs.append('non-ru')
            else:
                cs.append('')
            if cs[-1] == '':
                continue
            if current_lang == '':
                current_lang = cs[-1]
            # intra sentential switch detected
            elif current_lang != cs[-1]:
                cs_indices.append(i)
                num_intrasent += 1
                current_lang = cs[-1]
        assert len(cs_indices) == num_intrasent
        # majority language based on count
        if cs.count('ru') > cs.count('non-ru'):
            maj_lang = 'ru'
        elif cs.count('ru') < cs.count('non-ru'):
            maj_lang = 'non-ru'
        else:  # equal
            maj_lang = 'equal'
        first_lang = next((item for item in cs if item != ''), None)
        last_lang = next((item for item in reversed(cs) if item != ''), None)
        if sents:
            # check for intersentential switch, last language of previous sent
            if first_lang != sents[-1][-2]:
                num_intersent += 1
        sents.append([tokens, cs, cs_indices, maj_lang, len_sent, first_lang, last_lang, num_intrasent])
        tokens, cs, cs_indices = [], [], []
    return sents, num_sent, num_intersent

   
# TODO cs instanzen nach länge auszählen und dann POS/DEP kombis vergleichen


if __name__ == '__main__':
    corpus_dir = '../corpus/'
    for f in sorted(os.listdir(corpus_dir)):
        print(f)
        parse_file(corpus_dir+f)
    # s = "— Ну, вот чтò, господа, — сказал Билибин, — Болконский мой гость в доме и здесь в Брюнне, и я хочу его угостить, сколько могу, всеми радостями здешней жизни. Ежели бы мы были в Вене, это было бы легко; но здесь, dans ce vilain trou morave,[290] это труднее, и я прошу у всех вас помощи. Il faut lui faire les honneurs de Brünn.[291] Вы возьмите на себя театр, я — общество, вы, Ипполит, разумеется, — женщин."
    # print(parse_sents(s))
