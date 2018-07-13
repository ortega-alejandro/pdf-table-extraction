#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 14:08:08 2018

@author: brookeerickson
"""


from gensim.models import Word2Vec
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from matplotlib import pyplot
# define training data
#sentences = [['this', 'is', 'the', 'first', 'sentence', 'for', 'word2vec'],
#			['this', 'is', 'the', 'second', 'sentence'],
#			['yet', 'another', 'sentence'],
#			['one', 'more', 'sentence'],
#			['and', 'the', 'final', 'sentence']]


description = 'Operating power plants in Afghanistan as in 2016. Digitization based on Afghan Energy Information Center (AEIC) maps.'
s = description.lower().split('.')
sentences = []
for each in s:
    if len(each)>0:
        sentences.append(each.strip().split(' '))
print (sentences)
# train model
model = Word2Vec(sentences, min_count=1)
'''# fit a 2d PCA model to the vectors
X = model[model.wv.vocab]
pca = PCA(n_components=2)
result = pca.fit_transform(X)
# create a scatter plot of the projection
pyplot.scatter(result[:, 0], result[:, 1])
words = list(model.wv.vocab)
for i, word in enumerate(words):
	pyplot.annotate(word, xy=(result[i, 0], result[i, 1]))
pyplot.show()
'''# summarize the loaded model
print(model)
# summarize vocabulary
words = list(model.wv.vocab)
print(words)
# access vector for one word
print(model['afghan'])
# save model
model.save('model.bin')
# load model
new_model = Word2Vec.load('model.bin')
print(new_model)