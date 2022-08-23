# -*- coding: utf-8 -*-
"""Scrapping&Keywords.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1v28lRPGr9q5jw-WBcHWRhRuIXGxtPTHN
"""

# !pip install keybert[flair]
# !pip install keybert[gensim]
# !pip install keybert[spacy]
# !pip install keybert[use]
# !pip install pytrends --quiet

from flask import request
import json
import os
from bs4 import BeautifulSoup
import pprint
import requests
from keybert import KeyBERT
from collections import Counter
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
from spacy.lang.en.stop_words import STOP_WORDS as en_stop
import re
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import pandas as pd
import json
# can use any model from flair , transformer etc.
kw_model = KeyBERT("paraphrase-multilingual-MiniLM-L12-v2")

pytrends = TrendReq(hl='fr-ch', tz=60)


def bcvs_generation():
    output = {}
    subscription_key = "1efefb33177548b2b8b1c63a283c6bc1"
    endpoint = 'https://api.bing.microsoft.com/' + "v7.0/search"
    snippet = []
    url = []
    title_list = []
    sites = ['https://www.bcvs.ch/']
    # flag=int(input('1:stocks  2:funds  3:crypto'))
    for site in sites:
      query = 'Comptes cartes and Hypothèques Crédits and Gestion fortune and Prévoyance assurances'+' '+site
      mkt = ['fr']
      sortBy = 'Relevance'  # Relevance byDefault
      params = {'q': query, 'mkt': mkt, 'sortBy': sortBy}
      headers = {'Ocp-Apim-Subscription-Key': subscription_key}
      try:
          response = requests.get(endpoint, headers=headers, params=params)
          response.raise_for_status() 
          search_response = response.json()
          pages = search_response['webPages']
          # # pprint(pages)
          # print(pages.keys())
          # pprint(pages['value'])
          value = pages['value']
          for i in range(0, 5):
              # print(value[i]['snippet'])
              url1 = value[i]['url']
              data = value[i]['snippet']
              title = value[i]['name']
              data = data.replace('\n', ' ')
              data = data.replace('\t', ' ')
              # data=regex.sub(' ', data)
              data = data.strip()
              if len(data) > 0:
                  snippet.append(data.lower())
                  url.append(url1)
                  title_list.append(title)
      except Exception as es:
          pass
    url, snippet, keywords_list = file_generation(snippet, url)
    trends = trends_generation()
    output['URL'] = url
    output['title'] = title_list
    output['Snippet'] = snippet
    output['Keywords'] = keywords_list
    output['trends'] = trends
    direct = os.getcwd()
    path = os.path.join(direct, 'static/output')
    with open(os.path.join(path, 'newsoutput.json'), 'w') as outfile:
        fun = json.dump(output, outfile)

    # os.remove(path)
    return output


def word_count(str):
    counts = dict()
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts


def file_generation(snippet, url):
    final_stopwords_list = list(fr_stop) + list(en_stop)
    keywords_list = []
    for i in range(0, len(snippet)):
        # hyperparameter tuning needed
        doc = snippet[i]
        keywords = kw_model.extract_keywords(doc, use_mmr=True, keyphrase_ngram_range=(
            1, 1), diversity=0.5, stop_words=final_stopwords_list)
        temp = []
        for keys in keywords:
            word = keys[0]
            temp.append(word)
        tempstr = ", ".join(temp)
        keywords_list.append([tempstr])
        # keywords_strings=", ".join(keywords_list)

    # output['URL']=url
    # output['Snippet']=snippet
    # output['Keywords']=keywords_list
    return url, snippet, keywords_list


def trends_generation():
    time_frames = ['today 12-m']
    cat = '1138'
    geo = 'CH-VS'
    gprop = 'news'
    trends = []
    keywords = ['finance', 'investment', 'stocks market']
    pytrends.build_payload(keywords, cat, time_frames[0], geo, gprop)
    for i in keywords:
        res = pytrends.suggestions(i)
        for j in res:
            keyword = j['title']
            trends.append(keyword)
    # output['trends']=trends
    return trends

# if __name__ == "__main__" :
#   extract('Voila', 1)
