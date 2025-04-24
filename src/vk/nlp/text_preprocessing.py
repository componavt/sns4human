"""
    Processes a given Russian text by cleaning and normalizing it.

    The function performs the following:
    - Splits text into sentences and tokenizes each sentence.
    - Removes hashtags, emojis, URLs, and one-letter tokens.
    - Filters out stop words.
    - Normalizes words using pymorphy3 (lemmatization).
    - Optionally removes personal names (surname, name, patronymic).
    - Optionally adds a period at the end of each cleaned sentence.

    Parameters:
    ----------
    text : str
        Input text string to process.
    filter_fio : bool, optional (default=False)
        If True, removes names and surnames detected via morphological tags.
    period : bool, optional (default=False)
        If True, appends a period to the end of each cleaned sentence.

    Returns:
    -------
    str
        A cleaned, lemmatized version of the input text.


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

alphabet  = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')                    # Russian alphabet
alphabet |= set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') # Add Latin letters (A-Z, a-z)
alphabet |= set('äöåšžüÄÖÅŠŽÜ')  # ä, ö, å (Finnish); š, ž (Karelian); ü (Veps)
alphabet_dash = alphabet | {'-'} # Optionally allow hyphen (dash) as part of words

morph = pymorphy3.MorphAnalyzer(lang='ru')

def process_text(text, filter_fio=False, period=False):

    sentences = sent_tokenize(text)  # Split into sentences
    processed_sentences = []

    for sentence in sentences:
        check_hash = False
        processed_parts = []
        words = word_tokenize(sentence)

        for i, w in enumerate(words):
          if len(w) == 1:
            continue
          if w == '#':
            check_hash = True
            continue
          if check_hash:
            check_hash = False
            continue

          # skip name and surname if filter_fio
          if filter_fio:
            w_tag = morph.parse(w.strip())[0].tag
            if 'Surn' in w_tag or 'Name' in w_tag or 'Patr' in w_tag:
              # context = get_text_window(words, i)
              # print(f"Filtered name/surname: {w} | Context: {context}")  # Debug output for context
              continue

          if (set(w.lower()).issubset(alphabet_dash) and
              contains_non_dash(w) and
              ":" not in emoji.demojize(w)):  # skip emojis
    
              res = morph.parse(w.lower())[0].normal_form
              if res and (res not in stop_words):
                processed_parts.append(res)

          else:
              # If word contains >= 4 characters from the alphabet (e.g., mixed case or with punctuation)
              if sum(1 for char in w.lower() if char in alphabet) >= 4:
                  # skip words-hyperlinks
                  if ('\\' not in w) and ('/' not in w) and (":" not in emoji.demojize(w)):
                      #context = get_text_window(words, i)
                      #print(f"Filtered not subset(alphabet): {w} | Context: {context}")
                      res = morph.parse(w.lower())[0].normal_form
                      if res and (res not in stop_words):
                          processed_parts.append(res)

        if processed_parts:
            last_word = processed_parts[-1]
            if last_word[-1] not in ".!?" and period:
                processed_parts[-1] += "."    # Attach period directly to the last word

        processed_sentences.append(" ".join(processed_parts))

    return " ".join(processed_sentences).strip()


def get_text_window(words, index, window_size=3):
    """Returns a context window of words around the given index."""
    start = max(0, index - window_size)
    end = min(len(words), index + window_size + 1)
    return ' '.join(words[start:end])


def contains_non_dash(s):
    """Check if a string consists not only dash characters."""
    return s.count('-') < len(s)

# if filter_fio then remove the last names from the text.
# if period then then add a period at the end of each sentence.
# ############################################################
