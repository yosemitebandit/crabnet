# pubmedWebcrawler.py
# Patrick Ye


import urllib2


## get PMIDs with initial query on disease
url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=pancreatic+neuroendocrine&retmax=20000'

resp = urllib2.urlopen(url)
data = resp.read()
# print data

