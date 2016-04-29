# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 07:23:06 2016

@author: Matteus
"""

import sqlite3
import re

Jnames = []
Jabrvs = []
sqlite_file = 'bajs.db'
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS JournalNames(Jname TEXT, Jabrv TEXT)')

with open('journals.txt') as jtext:
    text = jtext.readline()
    while text:
        jrn_i = text.find('JournalTitle:')
        abr_i = text.find('IsoAbbr:')
        if jrn_i !=-1:
            Jname = text[jrn_i+14:-1]
            Jnames.append(Jname)
        elif abr_i !=-1:
            Jabr = text[abr_i+9:-1]
            Jabrvs.append(Jabr)
        text = jtext.readline()
for i in range(len(Jnames)):
    c.execute("INSERT INTO JournalNames (Jname, Jabrv) VALUES (?, ?)",(Jnames[i],Jabrvs[i]))
    conn.commit()
c.close()
conn.close()
    
