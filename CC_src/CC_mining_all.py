# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 16:26:49 2021

@author: Marc Clément
"""

# -*- coding: utf-8 -*-
# Importing necessary library


import nltk
import re
import os
import pickle
from datetime import datetime


import xml.etree.ElementTree as ET
from gensim import corpora, similarities
import CC_setup_class
import logging  # Setting up the loggings to monitor gensim
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

stopwords = nltk.corpus.stopwords.words('french')
stopwords.append('considérant')
stopwords.append('qu')

codes = CC_setup_class.CC_cod()
patt = CC_setup_class.CC_pattern()
rw_list = CC_setup_class.CC_rewrite()
 
def merge_token(match_obj,tk):
    repl=""
    txt=match_obj.group().strip()
    txt=re.sub(r'\s{1,20}'," ",txt)
    #on supprime les citations"
    if tk=="QOT":
        #pour les sommaires on n'enlève pas les citations
        repl=txt
    elif tk=="PCJA":
        #on doit enlever les 2 derniers caractères qui sont du token suivant puis les restituer
        last=txt[len(txt)-2:len(txt)]
        txt=txt[0:len(txt)-2].strip()
        
        txt=re.sub(",","",txt)
        pcja=txt.split(" ")
        for p in pcja:
            repl+="PCJA_"+p.strip()+" "
        repl+=last
        repl=txt
    else:
        repl=tk+"_"+re.sub(" ","_",txt)
        repl=re.sub("'","_",repl)+" "
    return repl
    
def tokenize_entities(codes, patt, rw_list, text):
    #il faut éviter les blancs en début pour les regex
    text=text.strip()
    #on reprend certaines expressions ex: CGI pour code général des impôts
    for rw, rw_rep in rw_list.rw_par:
        raw_s = r'{0}'.format(rw)
        text=re.sub(raw_s,rw_rep,text,flags=re.I)
    for cod, cod_tk in codes.cod_par:
        text=re.sub(cod,lambda m: merge_token(m,cod_tk),text,flags=re.I)
    for pat, pat_tk in patt.pat_par:
        raw_s = r'{0}'.format(pat)
        text=re.sub(raw_s,lambda m: merge_token(m,pat_tk),text,flags=re.I)
    return text


def tokenize_only(text):

    text=tokenize_entities(codes, patt, rw_list,text)
    text = text.replace("'"," ")
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
    filtered_tokens_stop = [w for w in filtered_tokens if not w in stopwords]

    
    return filtered_tokens_stop

def read_corpus(doc_list):

    i=0

    cases=[]
    cases_id=[]
    CCdec=[]

    for doc in doc_list:
        i+=1
        if i%100==0:
           print(i)
        if i>1000000000:
               break
        CCcase=CC_setup_class.CC_case(doc)
        CCdec.append(CCcase)
        for c, csd_id in zip(CCcase.considerant, CCcase.cons_id):
            csd = tokenize_only(c)
            cases.append(csd)
            cases_id.append(csd_id)
    return CCdec, cases, cases_id
    
corpusdir = CC_setup_class.XML_DIR # Directory of corpus.

doc_list=list()
for f in os.listdir(corpusdir):
           doc_list.append(f)

CCdec, cases, cases_id =read_corpus(doc_list)
pickle.dump(cases_id, open(CC_setup_class.UPDATE_DIR+CC_setup_class.BASE_ALL+".id", 'wb'))
pickle.dump(CCdec, open(CC_setup_class.UPDATE_DIR+CC_setup_class.BASE_ALL+".cc", 'wb'))
dictionary = corpora.Dictionary(cases,  prune_at=4000000)
dictionary.save(CC_setup_class.UPDATE_DIR+CC_setup_class.BASE_ALL+'.dict')  # store the dictionary, for future reference
for c in range(len(cases)):
        cpbow=dictionary.doc2bow(cases[c])           
        cases[c]=cpbow
        if c%1000==0:
               print(c)
corpora.MmCorpus.serialize(CC_setup_class.UPDATE_DIR+CC_setup_class.BASE_ALL+'.mm', cases)  
corpus = corpora.MmCorpus(CC_setup_class.UPDATE_DIR+CC_setup_class.BASE_ALL+'.mm')
index= similarities.Similarity(CC_setup_class.UPDATE_DIR+CC_setup_class.BASE_ALL, corpus, num_features=len(dictionary))
index.save(CC_setup_class.UPDATE_DIR+CC_setup_class.BASE_ALL+'.idx')


