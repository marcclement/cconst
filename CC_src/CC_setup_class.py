# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 13:42:47 2021

@author: Marc
"""
install_src="./"
import re
import xml.etree.ElementTree as ET
from datetime import datetime

XML_DIR = "../CC_xml/" # Directory of corpus.
BASE_ALL="CC_all"
MIN_CONSID=5
UPDATE_DIR="./"




def read_considerant(textxml,doc):
    considerant = []
    cons_id = []
    nbconsid=1
    first=False
    notlast=True
    for elt in textxml.iter('CONTENU'):
      if (elt!=None):
        motif=elt.text
        considerantraw = motif.split('#')
        for consid in considerantraw:
            consid=consid.strip()
            test = re.compile(r'\d{1,5}\.')
            if len(consid)>MIN_CONSID:
                if (test.match(consid)):
                    first=True
                if (first and notlast):
                    if (consid[0]=="-"):
                        consid="§1"+consid
                        considerant.append(consid)
                        cons_id.append(doc+"_"+str(nbconsid))
                        nbconsid+=1
                    if (consid[0]=="."):
                        consid="§2"+consid
                        considerant.append(consid)
                        cons_id.append(doc+"_"+str(nbconsid))
                        nbconsid+=1
                    if (consid[0]=="«"):
                        considerant[len(considerant)-1]+=" "+consid
                    if (consid[0].isdigit()):
                        considerant.append(consid)
                        cons_id.append(doc+"_"+str(nbconsid))
                        nbconsid+=1
        #on ne prend que le premier contenu qui correspond au texte de la décision
        break
    return considerant, cons_id

def get_date_clair(date):
    date_cl=""
    Mois=['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']
    mois = date.month
    date_cl=str(date.day)+" "+Mois[mois-1]+" "+str(date.year)
    return date_cl

def get_cc_by_ref(CClist,ref):
    cc_find=None
    for cc in CClist:
        if (cc.caseref==ref):
            cc_find=cc
            break
    return cc_find

def print_clear(doc,dictionary):
    text=""
    for wd,_ in doc:
        text += dictionary[wd]+" "
    return text

def get_case_file(dictionary, cases):
    case_find = ""
    # on retrouve le mot dans le vecteur qui commence par constext pour avoir la source du considérant 
    for wd,_ in cases:
        if (dictionary[wd][0:8] == "constext"):
            case_find = dictionary[wd]
    case_find=case_find.split('_')[0]
    return case_find

def get_case_file_list(case_ids,pos):
    case_find = ""
    case_find=case_ids[pos].split('_')[0]
    return case_find

def get_consid_id_list(case_ids,pos):
    id_find = ""
    id_find=case_ids[pos].split('_')[1]
    #on a indexé les considérant à partir de 1 
    return int(id_find)-1

def get_text_consid_clear(cases, consid):
    numcase=consid.split('_')[0]
    numconsid=consid.split('_')[1]
    for c in cases:
        if numcase==c.caseref:
            casefind=c
            break
    text=casefind.considerant[int(numconsid)-1]
    return text

def clean_xml(case_raw):
        pat = re.compile("\s{3,}")
        case_raw= re.sub(pat, "#", case_raw) 
        #case_raw=case_raw.replace("DÉCIDE","DECIDE")
        #case_raw=case_raw.replace("D E C I D E","DECIDE")
        #case_raw=case_raw.replace("D É C I D E","DECIDE")
        #case_raw=case_raw.replace("O R D O N N E","DECIDE ORDONNE")
        #case_raw=case_raw.replace("ORDONNE","DECIDE ORDONNE")

        case_raw=case_raw.replace("\n"," ")
        case_raw=case_raw.replace("<br/><br/>","#")
        case_raw=case_raw.replace("<br/>","#")
        return case_raw

class CC_case:

    def __init__(self, doc):
        #Attention les fichiers sont en majuscule et le nom dans le xml en minuscule, problème sur Linux
        casef=doc.split(sep='.', maxsplit=1)[0].upper()+".xml"
        print(casef)

        case_file=open(XML_DIR+doc,"r",encoding="utf8")
        case_raw = case_file.read()
        case_file.close()
        case_raw=clean_xml(case_raw)
        self.tree = ET.fromstring(case_raw)
        self.caseref= casef
        self.text =""
        self.considerant=[]
        self.cons_id=[]
        self.numero=""
        self.solution=""
        self.nature=""
        self.date = ""
        self.date_obj = datetime
        self.date_clair = ""

        self.cod_matches = None
  
        
        for elt in self.tree.iter('DATE_DEC'):
            self.date = elt.text
            self.date_obj = self.date_obj.strptime(self.date,"%Y-%m-%d").date()
            self.date_clair = get_date_clair(self.date_obj)

        for elt in self.tree.iter('NUMERO'):
            self.numero = elt.text.strip()

        for elt in self.tree.iter('SOLUTION'):
            if (elt.text!=None):
                self.solution = elt.text.strip()
        for elt in self.tree.iter('NATURE_QUALIFIEE'):
            self.nature = elt.text.strip()
          
        self.considerant, self.cons_id=read_considerant(self.tree, doc)


class CC_cod:
    cod_text = []
    cod_text_tk=[]
    def __init__(self):
        list_cod = open(install_src+'CC_codes.txt','r', encoding="utf-8")
        cod_lines = list_cod.readlines()
        list_cod.close()
        for c in cod_lines:
            self.cod_text.append(c.strip())
            self.cod_text_tk.append('COD')
        self.cod_par=list(map(lambda x, y:(x,y), self.cod_text, self.cod_text_tk))
    def show(self):
        print(self.cod_text)

class CC_pattern:
    pattern_re = []
    pattern_text = []
    def __init__(self):
        list_pat = open(install_src+'CC_patterns.txt','r', encoding="utf-8")
        pat_lines = list_pat.readlines()
        list_pat.close()
        for t in pat_lines:
            self.pattern_re.append(t.split(' ')[0].strip())
            self.pattern_text.append(t.split(' ')[1].strip())
        self.pat_par=list(map(lambda x, y:(x,y), self.pattern_re, self.pattern_text))
    def show(self):
        print(self.pattern_text)
        print(self.pattern_re)
        
        
class CC_rewrite:
    rw_text = []
    rw_text_repl=[]
    def __init__(self):
        list_rw = open(install_src+'CC_rewrite.txt','r', encoding="utf-8")
        rw_lines = list_rw.readlines()
        list_rw.close()
        for c in rw_lines:
            txtsp=c.split(' ',1)
            txt=txtsp[0]
            txt_s=txtsp[1]
            self.rw_text.append(txt)
            self.rw_text_repl.append(txt_s)
        self.rw_par=list(map(lambda x, y:(x,y), self.rw_text, self.rw_text_repl))



class CC_tag:
    tag_text = []
    tag_tag = []
    def __init__(self):
        list_tag = open(install_src+'/CC_tags.txt','r', encoding="utf-8")
        tag_lines = list_tag.readlines()
        list_tag.close()
        for t in tag_lines:
            self.tag_text.append(t.split(' ')[0].strip())
            self.tag_tag.append(t.split(' ')[1].strip())
    def show(self):
        print(self.tag_text)
        print(self.tag_tag)
        
        
