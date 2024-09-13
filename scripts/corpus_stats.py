import nltk

nltk.download('stopwords')

from nltk.corpus import stopwords

from preprocess import parse_file

stopwords_ru = set(stopwords.words('russian'))
stopwords_fr = set(stopwords.words('french'))


tokens = parse_file()
unigram_frequencies = {x: tokens.count(x) for x in tokens}
