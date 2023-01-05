# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 16:26:49 2021

@author: Marc Clément
"""
from gensim import corpora, similarities
import pickle
import CC_setup_class
import pandas as pd

UPDATE_DIR = "./" 
XML_DIR = "../CC_xml/" # Directory of corpus.
BASE_ALL="CC_all"
BASE_IDX="CC_all"



CC_dict = corpora.Dictionary.load(UPDATE_DIR+BASE_ALL+'.dict')
with open(UPDATE_DIR+BASE_ALL+'.id','rb') as fhand:
    CC_id = pickle.load(fhand)
with open(UPDATE_DIR+BASE_ALL+'.cc','rb') as fhand:
    CC_cases = pickle.load(fhand)
CC_corpus = corpora.MmCorpus(UPDATE_DIR+BASE_ALL+'.mm')
with open(UPDATE_DIR+BASE_ALL+'.df','rb') as fhand:
    CC_df = pickle.load(fhand)
#juste pour éviter un problème si on change de répertoire
CC_index = similarities.Similarity.load(UPDATE_DIR+BASE_IDX+'.idx')
CC_index.output_prefix=UPDATE_DIR+BASE_IDX+'.idx'
CC_index.check_moved()

CC_df=CC_df.sort_values(by=['hit'], ascending=False)

for c in CC_df['source']:
    print(CC_setup_class.get_text_consid_clear(CC_cases, c)) 
    input_value = input("Stop")         
   