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
MAX_CLUSTER=10
MIN_SCORE=0.6


CC_dict = corpora.Dictionary.load(UPDATE_DIR+BASE_ALL+'.dict')
with open(UPDATE_DIR+BASE_ALL+'.id','rb') as fhand:
    CC_id = pickle.load(fhand)
with open(UPDATE_DIR+BASE_ALL+'.cc','rb') as fhand:
    CC_cases = pickle.load(fhand)
CC_corpus = corpora.MmCorpus(UPDATE_DIR+BASE_ALL+'.mm')
#juste pour éviter un problème si on change de répertoire
CC_index = similarities.Similarity.load(UPDATE_DIR+BASE_IDX+'.idx')
CC_index.output_prefix=UPDATE_DIR+BASE_IDX+'.idx'
CC_index.check_moved()
i=0

CC_df=pd.DataFrame(columns=['source','hit','consid'])
for document in CC_corpus:
    i+=1
    if i%100==0:
       print(i)
    if i>2000000000:
           break
   
    sims= CC_index[document]
    sims= sorted(enumerate(sims), key=lambda item: -item[1])
    nb_hit=0
    list_ref = []
    text=CC_setup_class.print_clear(document,CC_dict)
    for doc_position, doc_score in sims:
        if (doc_score>MIN_SCORE):
            nb_hit+=1
            case_find = ""
            case_find=CC_id[doc_position]
            cc_find=None
            
            case_ref=CC_setup_class.get_case_file_list(CC_id,doc_position)
            consid_id=CC_setup_class.get_consid_id_list(CC_id,doc_position)
            cc_find=CC_setup_class.get_cc_by_ref(CC_cases,case_ref)
            list_ref.append(case_find)

    CC_df=CC_df.append({'source' : CC_id[i-1],'hit' : nb_hit,'consid' : list_ref},ignore_index=True)        

pickle.dump(CC_df, open(CC_setup_class.UPDATE_DIR+CC_setup_class.BASE_ALL+".df", 'wb'))