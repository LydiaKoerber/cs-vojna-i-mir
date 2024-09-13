import nltk

nltk.download('stopwords')

from nltk.corpus import stopwords

stopwords_ru = set(stopwords.words('russian'))
stopwords_fr = set(stopwords.words('french'))