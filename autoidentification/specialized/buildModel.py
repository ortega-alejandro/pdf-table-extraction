#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 12:02:07 2018

@author: jadewu
"""


import nltk
import pandas as pd
import numpy as np
import re
import codecs
import pickle
from nltk.tokenize import RegexpTokenizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression

model = 'finalized_model.sav'
cv_model = 'count_vectorizer.sav'
tfidfv_model = 'tfidf_vectorizer.sav'
training_data = 'training_data_full.csv'
input_file = codecs.open(training_data, "r",encoding='utf-8', errors='replace')
output_file = open("out.csv", "w")

def sanitize_characters(raw, clean):    
    for line in input_file:
        line = line.lower()
        output_file.write(line)

def cv(data):
    count_vectorizer = CountVectorizer()
    emb = count_vectorizer.fit_transform(data)
    return emb, count_vectorizer

def tfidf(data):
    tfidf_vectorizer = TfidfVectorizer()
    train = tfidf_vectorizer.fit_transform(data)
    return train, tfidf_vectorizer


#clean, tokenize training data
sanitize_characters(input_file, output_file)
data = pd.read_csv("out.csv")
data.columns=['text','relevancy','include']
tokenizer = RegexpTokenizer(r'\w+')
data["tokens"] = data["text"].apply(tokenizer.tokenize)


#input training data into model
list_corpus = data["text"].tolist()
list_labels = data["include"].tolist()
X_train, X_test, y_train, y_test = train_test_split(list_corpus, list_labels, test_size=0.2)
X_train_counts, count_vectorizer = cv(X_train)
X_test_counts = count_vectorizer.transform(X_test)
X_train_tfidf, tfidf_vectorizer = tfidf(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)
clf_tfidf = LogisticRegression(C=30.0, class_weight='balanced', solver='liblinear', random_state=40)
clf_tfidf.fit(X_train_tfidf, y_train)

###SAVE MODEL
pickle.dump(clf_tfidf, open(model, 'wb'))
pickle.dump(count_vectorizer, open(cv_model, 'wb'))
pickle.dump(tfidf_vectorizer, open(tfidfv_model, 'wb'))

