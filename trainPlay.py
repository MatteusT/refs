# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 17:15:44 2015

@author: mtanha
"""

import numpy as np
from sklearn.svm import SVC
from sklearn.cluster import MeanShift
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from urllib2 import Request, urlopen
from StringIO import StringIO
import re
import io
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine
import sqlite3
#from sklearn.cluster import MeanShift as mshift

##def isYear(year):
##    np.arange(1800,2016).asType('str'):

def refsecSearch(pdf_path):
##    pdf_path = "C:\Users\Matteus\MSQCpaper\LL_absE_Lu2.pdf"
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
            self.line2page =[] #the line nr in which the page starts
            self.nyears = [] #number of times 19 or 20 are found in one line
            self.allnNames = []
            self.coords = []
            self.ncommas = []
            self.ndots = []
            self.name_ratio = []
            self.clust = []
            self.References = []
        def receive_layout(self, ltpage):        
            def render(item, page_number):
                if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                    for child in item:
                        render(child, page_number)
                elif isinstance(item, LTTextLine):
                    child_str = item.get_text()
                    if child_str:
                        # bbox == (x1, y1, x2, y2)
                        self.rows.append(child_str)
                        self.itemz.append(item)
                        self.ncommas.append(len([m.start() for m in re.finditer(',', child_str)]))
                        self.ndots.append(len([m.start() for m in re.finditer('\.', child_str)]))
                        pattern = re.compile("^\s+|\s*,\s*|\.\s*|\)\s*|\(\s*|\s+$")
                        items_str = pattern.split(child_str)
                        nNames = 0
                        names = []
                        for child in items_str:
                            if isName(child):
                                names.append(child)
                                nNames += 1
    ##                    if nNames > 0 or self.ref_cont:
    ##                    self.name_ratio.append(float(nNames)/len(items_str))
    ##                    for iyear in list(reversed(range(1900,2017))):
    ##                        year_index = child_str.find(str(iyear))#len([m.start() for m in re.finditer(str(iyear), child_str)])
    ##                        if year_index != -1
    ##                            break
                        coord = ( item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3]) # bbox == (x1, y1, x2, y2)                 
    ##                    self.nyears.append(nyears)
                        self.coords.append(coord)
                        self.allnNames.append(nNames)
                        self.line2page.append(page_number)
                    for child in item:
                        render(child, page_number)
                return
            render(ltpage, self.page_number)
            self.page_number += 1
    #        self.rows = sorted(self.rows, key = lambda x: (x[0], -x[2]))
            self.result = ltpage

        def findrefSection(self,h=3,ncom=6,ndot=6):
            ''' This is a variation of Mean-Shift in One dimension space to fidn the rows which have the largest population names, commas and dots.
            '''
            self.clust =[]
            Xs = np.array(self.coords)
            nitems = len(self.rows)
            shift_points = np.arange(nitems) # maybe should change this to the name rows
            max_min_dist = 1
            ncommas = np.array(self.ncommas)
            ndots = np.array(self.ndots)
            allnNames = np.array(self.allnNames)
            name_loc = np.where(allnNames > 0)[0]
            i = name_loc[0];
            niters = 0
            max_iter = 100
            while i:
                p_new = shift_points[i]
                p_new_start = p_new
                while True:
                    niters +=1
                    dist2all = abs(p_new-shift_points)
                    p_membs = np.where(dist2all<h)[0]
                    ncomma_membs = ncommas[p_membs] #
                    ndot_membs = ndots[p_membs]#
                    name_membs = allnNames[p_membs]
                    if sum(name_membs) == 0 or sum(ndot_membs) < ndot or sum(ncomma_membs)< ncom:
                        i = name_loc[name_loc>p_new][0]
                        break
    ##                commadir = np.where(ncomma_membs>0)[0] #
    ##                dotdir = np.where(ndot_membs>0)[0] #
                    namedir = np.where(name_membs>0)[0]
                    move = np.round(p_new - np.mean(shift_points[p_membs[namedir]])).astype('int')
                    if move == 0 or niters > max_iter:
                        move_test = -1
                        p_test = p_new + h
                        while move_test < 0: 
                            p_test += 1
                            dist2all = abs(p_test-shift_points) 
                            p_membs = np.where(dist2all<h)[0]
                            name_membs = allnNames[p_membs]
                            ncomma_membs = ncommas[p_membs] #
                            ndot_membs = ndots[p_membs]#
                            if sum(name_membs) == 0 or sum(ndot_membs) < ndot or sum(ncomma_membs)< ncom:
                                break
                            namedir = np.where(name_membs>0)[0]
                            move_test = np.round(p_new - np.mean(shift_points[p_membs[namedir]])).astype('int')
                        self.clust.append([p_new_start,p_test-1])
                        if p_test >(nitems-2) or sum(name_loc>p_test) == 0 :
                            i = False
                        else:
                            print nitems
                            print p_test
                            print name_loc
                            i = name_loc[name_loc>p_test][0]
                        break
                    p_new += move
        def findEachRef(self):
            for clusts in self.clust:
                for itr in range(clusts[0],clusts[1]):
                    self.rows[itr]
                    
    ##urlpdf = 'http://arxiv.org/pdf/1501.02262v1.pdf'
    ##remoteFile = urlopen(Request(urlpdf)).read()
    ##memoryFile = StringIO(remoteFile)
    memoryFile = io.open(pdf_path, mode='rb')
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
    return device


class trModel():
    def __init__(papers, labels):
        self.models = []
        for paper in papers:
            mod = refsecSearch(paper)
            l_temp = np.zeros(mod.nitems)
            for l in labels:
                l_temp[l[0]:[1]]=1
            self.labels.append(l_temp)
            self.models.append(mod)
    def geterr(x):
        err = []
        for i,mod in enumerate(self.models):
            preds = mod.findrefSection(x[0], x[1], x[2])
            pred = np.zeros(mod.nitems)
            for p in preds:
                pred[p[0]:p[1]]=1
            err.append(sum(abs(pred-np.array(self.labels))))
        return err


papers = ['C:\Users\Matteus\GNNforPES.pdf','C:\Users\Matteus\GibbsSampling.pdf']              
#mod = trModel(papers,labels)
            
