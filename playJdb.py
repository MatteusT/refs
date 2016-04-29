# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 15:28:21 2016

@author: Matteus
"""

from trainPlay import refsecSearch
import sqlite3
path = 'http://arxiv.org/pdf/1501.02262v1.pdf'
dref = refsecSearch(path)
dref.findrefSection()
Jname = []
conn = sqlite3.connect('bajs.db')
c = conn.cursor()
for clusts in dref.clust:
    for itr in range(clusts[0],clusts[1]):
        c.execute("SELECT * FROM JournalNames WHERE instr(?,Jname) > 0;",(dref.rows[itr]))
        Jname.append(c.fetchall())

c.close()
conn.close()
    