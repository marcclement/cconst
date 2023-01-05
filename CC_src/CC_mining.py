# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 10:02:38 2022

@author: mclement
"""


# -*- coding: utf-8 -*-
# Importing necessary library


import nltk
import re
import os
import codecs
from sklearn import feature_extraction


import pickle
from nltk.corpus import XMLCorpusReader

import shutil

import xml.etree.ElementTree as ET
from gensim import corpora, models, similarities, downloader

import logging  # Setting up the loggings to monitor gensim
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)




XML_DIR = "../CC_xml/" # Directory of corpus.
XML_ELEC = "../CC_elec/" # Directory of corpus.

CSV_ELEC="./elec.csv"

corpus = XMLCorpusReader(XML_DIR, '.*')

def clean_xml(case_raw):
        pat = re.compile("\s{3,}")
        case_raw= re.sub(pat, "#", case_raw) 
        case_raw=case_raw.replace("\n"," ")
        case_raw=case_raw.replace("<br/><br/>","#")
        case_raw=case_raw.replace("<br/>","#")
        return case_raw


def get_eia(textxml, doc):
    date="unknown"
    extract=""
    numero=""
    grief="non"
    sens=""
    for elt in textxml.iter('DATE_DEC'):
        date = elt.text
       
        if (date >= "1900-04-07"):
            #shutil.copy(XML_DIR+doc,XML_NEW+doc)
            for elt1 in textxml.iter('NATURE_QUALIFIEE'):
                if elt1.text is not None:
                    nat=elt1.text
            for elt3 in textxml.iter('NUMERO'):
                if elt3.text is not None:
                    numero=elt3.text
            for elt4 in textxml.iter('SOLUTION'):
                if elt4.text is not None:
                    sens=elt4.text
            for elt2 in textxml.iter('CONTENU'):
                if elt2.text is not None:  
                    ind=elt2.text.find("code électoral")
                    ind2=elt2.text.find("grief")
                    if (ind >= 0): 
                        print(ind)
                        extract=elt2.text[ind-100:ind+110]
                        print(extract)
                    if (ind2 >= 0): 
                        grief="oui"

    return extract, date, nat, numero, grief, sens




i=0
doc_list = corpus.fileids()
csvstr="fichier;nature;numéro;date;année;sens;extrait\n"

for doc in doc_list:
    i+=1
    if i%500==0:
       print("---->")
       print(i)

    case_file=open(XML_DIR+doc,"r",encoding="utf8")
    case_raw = case_file.read()
    case_file.close()
    case_raw=clean_xml(case_raw)
    xmldoc = ET.fromstring(case_raw)

    extract, date, nat, numero, grief, sens=get_eia(xmldoc, doc)
    extract = extract.replace(";",",")

    if grief=="oui":
      shutil.copy(XML_DIR+doc,XML_ELEC+doc)
      csvstr+=doc+";"+nat+";"+numero+";"+date+";"+date[0:4]+";"+sens+";"+extract+"\n"     

with open(CSV_ELEC, 'w') as csvfile:
    csvfile.write(csvstr)
    csvfile.close()
              



