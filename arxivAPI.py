# -*- coding: utf-8 -*-
"""
Created on Mon Apr 04 10:01:25 2016

@author: Matteus
"""

import urllib
url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=10'
data = urllib.urlopen(url).read()
print data