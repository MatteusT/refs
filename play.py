# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 17:15:44 2015

@author: mtanha
"""

#import pyPdf

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from urllib2 import Request, urlopen
from StringIO import StringIO
import re
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine
import sqlite3


def isName(name):
    isName = 0
    conn = sqlite3.connect('familynames.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM names WHERE name=?""", (name,))
    name = cursor.fetchall()
    if name:
        isName = 1
    return isName
    
class PDFPageDetailedAggregator(PDFPageAggregator):
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.rows = []
        self.page_number = 0
        self.ntot = []
        self.allnNames = []
        self.coords = []
    def receive_layout(self, ltpage):        
        def render(item, page_number):
            if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                for child in item:
                    render(child, page_number)
            elif isinstance(item, LTTextLine):
                child_str = item.get_text()
#                row = (page_number,  child_str) # bbox == (x1, y1, x2, y2)
#                self.rows.append(row)
                child_str = ''
                nNames = 0
                for child in item:
                    if isinstance(child, (LTChar, LTAnno)):
                        text = child.get_text()
                        child_str += text
                        nNames += isName(text)
                child_str = ' '.join(child_str.split()).strip()
                if child_str:
                    coord = ( item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3]) # bbox == (x1, y1, x2, y2)                 
                    n19 = len([m.start() for m in re.finditer('19', child_str)])
                    n20 = len([m.start() for m in re.finditer('20', child_str)])
                    self.ntot.append(n19+n20)
                    row = (page_number,  child_str, nNames) # bbox == (x1, y1, x2,y2)
#                    print row
                    self.coords.append(coord)
                    self.rows.append(row)
                    self.allnNames.append(nNames)
                for child in item:
                    render(child, page_number)
            return
        render(ltpage, self.page_number)
        self.page_number += 1
#        self.rows = sorted(self.rows, key = lambda x: (x[0], -x[2]))
        self.result = ltpage



urlpdf = 'http://arxiv.org/pdf/1501.02262v1.pdf'
remoteFile = urlopen(Request(urlpdf)).read()
memoryFile = StringIO(remoteFile)
parser = PDFParser(memoryFile)
doc = PDFDocument(parser)
#doc.initialize('password') # leave empty for no password

rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageDetailedAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)

for page in PDFPage.create_pages(doc):
    interpreter.process_page(page)
    # receive the LTPage object for this page
    device.get_result()


#from urllib2 import Request, urlopen
#from StringIO import StringIO
#
#urlpdf = 'http://arxiv.org/pdf/1501.02262v1.pdf'
#remoteFile = urlopen(Request(urlpdf)).read()
#memoryFile = StringIO(remoteFile)
##pdfFile = pyPdf.PdfFileReader(memoryFile)
#
##for ipage in pdfFile.pages:
##    pageContent = ipage.extractText()
##    print pageContent.find('[1]')
## Create a PDF parser object associated with the file object.
#parser = PDFParser(memoryFile)
## Create a PDF document object that stores the document structure.
## Supply the password for initialization.
#document = PDFDocument(parser)
## Create a PDF resource manager object that stores shared resources.
#rsrcmgr = PDFResourceManager()
## Create a PDF device object.
#device = PDFDevice(rsrcmgr)
## Create a PDF interpreter object.
#interpreter = PDFPageInterpreter(rsrcmgr, device)
## Process each page contained in the document.
#for page in PDFPage.create_pages(document):
#    interpreter.process_page(page)