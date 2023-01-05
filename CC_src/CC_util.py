# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 16:26:49 2021

@author: Marc Clément
"""
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.propagate=True
fh = logging.FileHandler('jadelog.txt', mode='w')
formatter = logging.Formatter(fmt="%(levelname)s - %(asctime)s: %(message)s", datefmt='%H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)



import re
import xml.etree.ElementTree as ET
import nltk


from datetime import datetime

stopwords = nltk.corpus.stopwords.words('french')
stopwords.append('considérant')
stopwords.append('qu')

MIN_CONSID=20

def get_code_reference(codes,text):
    cod_matches=[]
    for cod in codes.cod_text:
        cod_matches.append(len(re.findall(cod,text,flags=re.I)))
    return cod_matches
    
def max_code_reference(codes,case_codes):
    max_codes=0
    matiere="aucune"
    for (cod, c) in zip(codes.cod_mat, case_codes):
            if (c>max_codes):
                matiere=cod
                max_codes=c
    return matiere

def merge_token(match_obj,tk):
    #on supprime les citations
    if tk!="QOT":
        repl=tk+"_"+re.sub(" ","_",match_obj.group().strip())
        repl=re.sub("'","_",repl)+" "
    else:
        repl=" "
    return repl
    
def tokenize_entities(codes,patt, rw_list, text):
    for cod, cod_tk in codes.cod_par:
        text=re.sub(cod,lambda m: merge_token(m,cod_tk),text,flags=re.I)
    for pat, pat_tk in patt.pat_par:
        text=re.sub(pat,lambda m: merge_token(m,pat_tk),text,flags=re.I)
    return text


def tokenize_only(codes,patt,rw_list, text):

    text=tokenize_entities(codes, patt, rw_list, text)
    text = text.replace("'"," ")
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)
    filtered_tokens_stop = [w for w in filtered_tokens if not w in stopwords]

    
    return filtered_tokens_stop


def get_considerant(text):
    considerant = []
    considerantraw = text.split('#')
    for consid in considerantraw:
          if len(consid.strip())>MIN_CONSID:
            considerant.append(consid.strip())       
    return considerant



def get_date_clair(date):
    date_cl=""
    Mois=['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']
    mois = date.month
    date_cl=str(date.day)+" "+Mois[mois-1]+" "+str(date.year)
    return date_cl

def get_case_name_list(case_ids,pos):
    case_find = ""
    case_find=case_ids[pos].split('_')[0]
    return case_find

def get_consid_id_list(case_ids,pos):
    numid=0
    considid=""
    considid=case_ids[pos].split('_')[1] 
    if len(considid)>0:
        numid=int(considid)
    return numid

def get_case_name(dictionary, cases):
    case_find = ""
    # on retrouve le mot dans le vecteur qui commence par cetatext pour avoir la source du considérant 
    for wd,_ in cases:
        if (dictionary[wd][0:8] == "cetatext"):
            case_find = dictionary[wd]
    case_find=case_find.split('_')[0]
    if (case_find==""):
        logger.info("Case name not found: "+print_clear(cases,dictionary))
    return case_find

def get_consid_id(dictionary, cases):
    id_find = ""
    numid=0
    considid=""
    # on retrouve le mot dans le vecteur qui commence par cetatext pour avoir le numero du considérant ou du sommaire
    for wd,_ in cases:
        if (dictionary[wd][0:8] == "cetatext"):
            id_find = dictionary[wd]
            considid=id_find.split('_')[1] 
    if len(considid)>0:
        numid=int(considid)
    logger.info("Case id found: "+considid)
    return numid

def print_clear(doc,dictionary):
    text=""
    for wd,_ in doc:
        text += dictionary[wd]+" "
    return text


class Jugement_case:

    def __init__(self):
          self.text=""
          self.date = ""
          self.date_obj = datetime
          self.text = ""
          self.considerant =[]
          self.cod_matches = None
          self.html = ""
          self.doc=[]
          self.citations=[]
                   
    def load_jgt(self, jgt_str):
          self.considerant.clear()
          self.doc.clear()
          self.text=""
          lines=jgt_str.splitlines()
          for line in lines:
               ln=line.lstrip()
               self.text+=ln
               if (len(ln) >MIN_CONSID):
                  test=re.search('\d{1,2}\\.\s',ln)
                  if test:
                     self.considerant.append(ln)

class CC_case:

    def __init__(self, caseref, sc, install_data):
        #Attention les fichiers sont en majuscule et le nom dans le xml en minuscule, problème sur Linux
        casef=caseref.split(sep='.', maxsplit=1)[0].upper()+".xml"
        logger.info("Init case:" + casef)
        case_file=open(install_data+casef,"r",encoding="utf8")
        case_raw = case_file.read()

        case_file.close()
        case_raw=clean_xml(case_raw)
        self.tree = ET.fromstring(case_raw)
        self.caseref= caseref
        self.sommaire = []
        self.classement = []
        self.score = sc
        self.text =""
        self.considerant=[]
        self.numero=""
        self.date = ""
        self.date_obj = datetime
        self.date_clair = ""
        self.lebon = "C"
        self.cod_matches = None
        self.html = ""
        self.doc=[]
        self.consid_selected = 0
        self.match_som = None
        self.juridiction ="CE"
        self.match_position = []
        
        for elt in self.tree.iter('DATE_DEC'):
            self.date = elt.text
            self.date_obj = self.date_obj.strptime(self.date,"%Y-%m-%d").date()
            self.date_clair = get_date_clair(self.date_obj)
        for elt in self.tree.iter('PUBLI_RECUEIL'):
            if not(elt.text.strip()==""):
                self.lebon = elt.text
        for elt in self.tree.iter('NUMERO'):
                self.numero = elt.text.strip()
                if not(self.numero[2:4].isnumeric()):
                    self.juridiction=self.numero[2:4]
          
        for elt in self.tree.iter('CONTENU'):
            if elt.text is not None:
                result=re.search('Considérant(.*?)End_Motivation',elt.text,re.MULTILINE)
                if result is not None: 
                    self.text="Considérant "+result.group(1)
                self.considerant=get_considerant(self.text)
                logger.info("Get nb considerant:" + casef+" "+str(len(self.considerant)))
                break
        if (self.lebon == "A") or (self.lebon == "B"):
                for elt2 in self.tree.iter('ANA'):
                    if elt2.text != None:
                        self.sommaire.append(elt2.text.strip())
        if (self.juridiction=="CE"):
            self.titre="CE "+self.date_clair+" n°"+self.numero+" "+self.lebon
        else:
            self.titre="CAA "+self.juridiction+" "+self.date_clair+" n°"+self.numero+" "+self.lebon


def clean_xml(case_raw):
        pat = re.compile("\s{3,}")
        case_raw= re.sub(pat, "#", case_raw) 
        #case_raw=case_raw.replace("DÉCIDE","DECIDE")
        #case_raw=case_raw.replace("D E C I D E","DECIDE")
        #case_raw=case_raw.replace("D É C I D E","DECIDE")
        #case_raw=case_raw.replace("O R D O N N E","DECIDE ORDONNE")
        #case_raw=case_raw.replace("ORDONNE","DECIDE ORDONNE")
        case_raw=case_raw.replace("Article 1er :","End_Motivation Article 1er :")
        case_raw=case_raw.replace("\n"," ")
        case_raw=case_raw.replace("<br/><br/>","#")
        case_raw=case_raw.replace("<br/>","#")
        return case_raw

   
