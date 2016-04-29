from pyPdf import PdfFileReader
from urllib2 import Request, urlopen


urlpdf = 'http://arxiv.org/pdf/1501.02262v1.pdf'
rfile = urlopen(Request(urlpdf)).read()
f = open(rfile, 'rb')
reader = PdfFileReader(f)
contents = reader.getPage(0).extractText().split('\n')
f.close()
