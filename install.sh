#!/usr/bin/env bash

# install venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# download models
python -q -m spacy download ru_core_news_sm-3.7.0 --direct
python -q -m spacy download fr_core_news_sm-3.7.0 --direct
python -q -m spacy download de_core_news_sm-3.7.0 --direct
# multilingual model for tokenization
python -q -m spacy download xx_sent_ud_sm-3.7.0 --direct