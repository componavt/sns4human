"""

This script preprocesses Russian-language text:
Splits the text into sentences and words (removing hashtags)

*   Removes characters outside the Russian alphabet
*   Excludes stop words (built-in + custom lists from GitHub)
*   Filters out emoji, URLs and single-letter tokens

*   Normalizes words via PyMorphy3 (reduces to the initial form)
*   Optionally adds punctuation marks (dots)
*   Returns a cleaned and lemmatized string.



Этот скрипт выполняет предобработку русскоязычного текста:
Разбивает текст на предложения и слова (удаляя хэштеги)

*    Удаляет символы вне русского алфавита

*   Исключает стоп-слова (встроенные + кастомные списки с GitHub)
*  Отфильтровывает эмодзи, URL и однобуквенные токены
*  Нормализует слова через PyMorphy3 (приводит к начальной форме)
*  Опционально добавляет знаки препинания (точки)
*  Возвращает очищенную и лемматизированную строку.

"""

import pandas as pd
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import pymorphy3
import requests
import csv
import emoji
from nltk.corpus import stopwords
import re

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)


stop_words = stopwords.words("russian")
stop_words += requests.get('https://raw.githubusercontent.com/componavt/sns4human/refs/heads/main/src/vk/nlp/RussianStopWords.txt').text.split('\n')
stop_words += requests.get('https://raw.githubusercontent.com/componavt/sns4human/refs/heads/main/src/vk/nlp/stopwords-ru.txt').text.split()

alphabet = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя-.')
morph = pymorphy3.MorphAnalyzer(lang='ru')

def process_text(text, filter_fio=False, points=False):
    sentences = sent_tokenize(text)
    processed_sentences = []

    for sentence in sentences:
        processed_parts = []
        sentence = re.sub(r'#\w+', '', sentence)
        for w in word_tokenize(sentence):
            if (len(w) == 1 or
                ":" in emoji.demojize(w) or
                not set(w.lower()).issubset(alphabet) or
                not w[0:2].lower().isalpha() or
                '\\' in w or
                '/' in w):
                continue
            if filter_fio:
                w_tag = morph.parse(w.strip())[0].tag
                if  'Surn' in w_tag or 'Name' in w_tag or 'Patr' in w_tag:
                    continue
            res = morph.parse(w.lower())[0].normal_form
            if res and (res not in stop_words):
                processed_parts.append(res)

        if points and processed_parts:
            processed_parts[-1] += "."

        processed_sentences.append(" ".join(processed_parts))

    return " ".join(processed_sentences)
