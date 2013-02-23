# pubmedWebcrawler.py
# Patrick Ye


#import library to do http requests:
import urllib2
 
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
#from xml.dom import minidom

# import json library for json output
import json

## --------------------------------------
## get all PMIDs on initial disease query
## --------------------------------------
disease = 'pancreatic+neuroendocrine'
numPapers = 20
url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=' + disease + '&retmax=' + str(numPapers)

## source: http://www.travisglines.com/web-coding/python-xml-parser-tutorial
#download the file:
file = urllib2.urlopen(url)
#file = urllib2.urlopen('http://www.somedomain.com/somexmlfile.xml')
#convert to string:
data = file.read()
#close file because we dont need it anymore:
file.close()

#print(data)

#parse the xml you downloaded
dom = parseString(data)

# total number of papers
countTag = dom.getElementsByTagName('Count')[0].toxml()
countData = countTag.replace('<Count>','').replace('</Count>','')
countData = int(countData)
#print countData

for i in range(countData):

	#retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
	xmlTag = dom.getElementsByTagName('Id')[i].toxml()

	#strip off the tag (<tag>data</tag>  --->   data):
	PMID=xmlTag.replace('<Id>','').replace('</Id>','')
	#print out the xml tag and data in this format: <tag>data</tag>
	#print xmlTag
	#just print the data
	print PMID

	## ------------------------------
	## get XML file from HTTP request
	## ------------------------------
	urlPaper = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=' + str(PMID)
	#urlPaper = 'http://www.ncbi.nlm.nih.gov/pubmed/?term=' + str(xmlData) + '&report=xml&format=xml'
	#print(urlPaper)

	#download the file:
	filePaper = urllib2.urlopen(urlPaper)
	#convert to string:
	dataPaper = filePaper.read()
	#close file because we dont need it anymore:
	filePaper.close()

	# print dataPaper

	domPaper = parseString(dataPaper)
	itemlist = domPaper.getElementsByTagName('Item') 
	#print len(itemlist)
	#print itemlist[0].attributes['Name'].value

	for s in itemlist:
		if s.attributes['Name'].value == 'Title':
			title = s.childNodes[0].nodeValue
			#print title
		if s.attributes['Name'].value == 'PubDate':
			pubDate = s.childNodes[0].nodeValue
			#print pubDate
		if s.attributes['Name'].value == 'LastAuthor':
			lastAuthor = s.childNodes[0].nodeValue
			#print lastAuthor

	#    print(s.attributes['Name'].value)
		#print(s.childNodes[0].nodeValue)


		# "title":"Chordoma genetic sequencing",
		# "year": 2004,
		# "month": 3,
		# "authors": [12,8,2,5],
		# "URL": 34545,
		# "disease": "Chordoma",
		# "leading": 12,
		# "last author": 5,
		# "index": 8
		
	#parse the xml you downloaded
	# dom = parseString(dataPaper)

	# #retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
	# authorTag = dom.getElementsByTagName('LastName')[0].toxml()
	# #strip off the tag (<tag>data</tag>  --->   data):
	# authorData=xmlTag.replace('<LastName>','').replace('</LastName>','')

	# authorTag = dom.getElementsByTagName('LastAuthor')[0].toxml()
	# #strip off the tag (<tag>data</tag>  --->   data):
	# authorData=xmlTag.replace('<LastAuthor>','').replace('</LastAuthor>','')

	# print(authorData)


	## --------------------------------
	## write json file indexed by paper
	## --------------------------------
	
	#json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
	print json.dumps({'PMID':PMID, 'title':title, 'title':title, 'disease':disease})
	# with open('papers.txt', 'aw') as outfile:
		# json.dump({'PMID':PMID, 'title':title, 'title':title, 'disease':disease}, outfile)
