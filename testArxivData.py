# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 10:33:59 2015

@author: Matteus
"""
from nltk.stem import *
#import urllib
import pyPdf
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from urllib2 import Request, urlopen
from StringIO import StringIO
#url = 'http://export.arxiv.org/api/query?search_query=all:cs&start=0&max_results=10'
#data = urllib.urlopen(url).read()
#urlpdf = 'http://arxiv.org/pdf/1510.02262v1.pdf'
#remoteFile = urlopen(Request(urlpdf)).read()
#memoryFile = StringIO(remoteFile)
#pdfFile = pyPdf.PdfFileReader(memoryFile)
#data = pyPdf.PdfFileReader(file('http://arxiv.org/pdf/1510.02262v1.pdf','r'))

#singles = [stemmer.stem(plural) for plural in plurals]

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

registry = MetadataRegistry()
URL = 'http://export.arxiv.org/oai2'
registry.registerReader('oai_dc', oai_dc_reader)

clt = Client(URL,registry)
ic = 0
for record in clt.listRecords(metadataPrefix='oai_dc'):
    if ic > 10:
        break
    print record[1]['title'][0]
    record[1]['identifier'][0]  # arxiv_id link
    ic +=1
