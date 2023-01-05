# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# import the wget module

import os
import gzip
import shutil
import tarfile
url= "https://echanges.dila.gouv.fr/OPENDATA/CONSTIT/"


file_type = ".gz"
path="../CC_gz/"
path_out="../CC_xml/"
for fname in os.listdir(path):
    if fname.endswith(file_type):
        with tarfile.open(path+fname,'r:gz') as f_in:
            for member in f_in.getmembers():
                if member.isreg():  # skip if the TarInfo is not files
                    member.name = os.path.basename(member.name) # remove the path by reset it
                    f_in.extract(member,path_out) # extract
                    