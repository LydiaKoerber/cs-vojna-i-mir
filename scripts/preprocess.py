import os
import re


def parse_file(path):
    """parse corpus file"""
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
        # split by parts and chapters
        parts = re.split(r'ЧАСТЬ \w+Я\.\n', text)
        print(len(parts), [len(p) for p in parts])
        print(parts)
        chapters = []
        for p in parts:
            if not p or not re.match('\s+', p):
                continue
            chapters_new = re.split(r'\n[XVIM]+\.\n', p)
            chapters.append(chapters_new)
            for c in chapters_new:
                lines = c.split('\n\n')
                for l in lines:
                    parse_line(l)


if __name__ == '__main__':
    corpus_dir = '../corpus'
    for f in os.listdir(corpus_dir):
        print(f)
        parse_file(f)
        break
