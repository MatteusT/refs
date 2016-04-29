# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 15:28:21 2016

@author: Matteus
"""
import sqlite3
Jname = []
conn = sqlite3.connect('bajs.db')
c = conn.cursor()
for clusts in dref.clust:
    for itr in range(clusts[0],clusts[1]):
        c.execute("SELECT * FROM JournalNames WHERE instr(?,Jname) > 0;",(dref.rows[itr]))
        Jname.append(cursor.fetchall())

c.close()
conn.close()
    