# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 16:26:49 2021

@author: Marc Clément
"""
from gensim import corpora, similarities



UPDATE_DIR = "./" 
XML_DIR = "../CC_xml/" # Directory of corpus.
BASE_ALL="CC_all"
BASE_IDX="CC_all"
CHK_SIZE=25000

chk_list=list()

dictionary = corpora.Dictionary.load(UPDATE_DIR+BASE_ALL+'.dict')
corpus = corpora.MmCorpus(UPDATE_DIR+BASE_ALL+'.mm')
index= similarities.Similarity(UPDATE_DIR+BASE_IDX, corpus, num_features=len(dictionary))
index.save(UPDATE_DIR+BASE_IDX+'.idx')
