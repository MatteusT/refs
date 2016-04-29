# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 17:15:44 2015

@author: mtanha
"""

#import pyPdf
import numpy as np
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
#from sklearn.cluster import MeanShift as mshift


def isName(name):
    # this fucntion will compare the string input to the database of names  
    isName = 0
    conn = sqlite3.connect('familynames.db')
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM names WHERE name=?""", (name,))
    name = cursor.fetchall()
    if name:
        isName = 1
    return isName
class PDFPageDetailedAggregator(PDFPageAggregator):
    #this function aggregates all the lines in the text
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.rows = []
        self.itemz = []
        self.page_number = 0
        self. line2page =[] #the line nr in which the page starts
        self.nyears = [] #number of times 19 or 20 are found in one line
        self.allnNames = []
        self.coords = []
        self.ncommas = []
        self.ndots = []
    def receive_layout(self, ltpage):        
        def render(item, page_number):
            if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                for child in item:
                    render(child, page_number)
            elif isinstance(item, LTTextLine):
                child_str = item.get_text()
                if child_str:
#                row = (page_number,  child_str) # bbox == (x1, y1, x2, y2)
                    self.rows.append(child_str)
                    self.itemz.append(item)
                    self.ncommas.append(child_str.find(','))
                    self.ndots.append(child_str.find('.'))
                    pattern = re.compile("^\s+|\s*,\s*|\.\s*|\s+$")
                    items_str = pattern.split(child_str)
                    nNames = 0
                    for child in items_str:
                        nNames += isName(child)
##                child_str = ''           
##                for child in item:
##                    if isinstance(child, (LTChar, LTAnno)):
##                        text = child.get_text()
##                        child_str += text
##                        nNames += isName(text)
##                child_str = ' '.join(child_str.split()).strip()
                    coord = ( item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3]) # bbox == (x1, y1, x2, y2)                 
                    n19 = len([m.start() for m in re.finditer('19', child_str)])
                    n20 = len([m.start() for m in re.finditer('20', child_str)])
                    self.nyears.append(n19+n20)
##                    row = (page_number,  child_str, nNames) # bbox == (x1, y1, x2,y2)
#                    print row
                    self.coords.append(coord)
##                    self.rows.append(row)
                    self.allnNames.append(nNames)
                    self.line2page.append(page_number)
                for child in item:
                    render(child, page_number)
            return
        render(ltpage, self.page_number)
        self.page_number += 1
#        self.rows = sorted(self.rows, key = lambda x: (x[0], -x[2]))
        self.result = ltpage

    def findrefSection(self,h):
        Xs = np.array(self.coords)
        shift_points = np.vstack([np.mean(Xs[:,[0,2]],axis=1),np.mean(Xs[:,[1,3]],axis=1)])
        max_min_dist = 1
        nyears = np.array(self.nyears)
        allnNames = np.array(self.allnNames)
        iteration_number = 0
        MIN_DISTANCE = 0.000001
        still_shifting = [True] * shift_points.shape[1]
        while max_min_dist > MIN_DISTANCE:
            # print max_min_dist
            max_min_dist = 0
            iteration_number += 1
            for i in range(0, shift_points.shape[1]):
                if not still_shifting[i]:
                    continue
                p_new = shift_points[:,i]
                p_new_start = p_new
                dist2all = np.linalg.norm((p_new_start.reshape([len(p_new_start),1])-shift_points),axis=1)
                p_membs = np.where(dist2all<h)[0]
                year_membs = nyears[p_membs]
                name_membs = allnNames[p_membs]
                if sum(year_membs)> 0 and sum(name_membs) > 2:
                    #yeardir = np.where(year_membs>0)
                    namedir = np.where(name_membs>1)[0]
                    p_new = np.mean(shift_points[:,p_membs[namedir]])
                    dist = np.linalg.norm((p_new_start-p_new),axis=1)
                    shift_points[i,:] = p_new
                    if dist > max_min_dist:
                        max_min_dist = dist
                    if dist < MIN_DISTANCE:
                        still_shifting[i] = False
##                allmembs[i].append(p_membs)
        return shift_points


                 
urlpdf = 'http://arxiv.org/pdf/1501.02262v1.pdf'
remoteFile = urlopen(Request(urlpdf)).read()
memoryFile = StringIO(remoteFile)
parser = PDFParser(memoryFile)
doc = PDFDocument(parser)

rsrcmgr = PDFResourceManager()
laparams = LAParams()
device = PDFPageDetailedAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)

for page in PDFPage.create_pages(doc):
    interpreter.process_page(page)
    # receive the LTPage object for this page
    device.get_result()


#mshift()
