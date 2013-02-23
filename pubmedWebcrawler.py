# pubmedWebcrawler.py
# Patrick Ye


#import library to do http requests:
import urllib2
 
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
#from xml.dom import minidom

## --------------------------------------
## get all PMIDs on initial disease query
## --------------------------------------
url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=pancreatic+neuroendocrine&retmax=20000'

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
#print countData

#retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
xmlTag = dom.getElementsByTagName('Id')[0].toxml()
#strip off the tag (<tag>data</tag>  --->   data):
xmlData=xmlTag.replace('<Id>','').replace('</Id>','')
#print out the xml tag and data in this format: <tag>data</tag>
#print xmlTag
#just print the data
#print xmlData

## ------------------------------
## get XML file from HTTP request
## ------------------------------
urlPaper = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=' + str(xmlData)
#urlPaper = 'http://www.ncbi.nlm.nih.gov/pubmed/?term=' + str(xmlData) + '&report=xml&format=xml'
#print(urlPaper)

#download the file:
filePaper = urllib2.urlopen(urlPaper)
#convert to string:
dataPaper = filePaper.read()
#close file because we dont need it anymore:
filePaper.close()

# print dataPaper

dom = parseString(dataPaper)
itemlist = dom.getElementsByTagName('Item') 
#print len(itemlist)
#print itemlist[0].attributes['Name'].value

for s in itemlist:
	if s.attributes['Name'].value == 'LastAuthor':
		print(s.childNodes[0].nodeValue)
#    print(s.attributes['Name'].value)
	#print(s.childNodes[0].nodeValue)


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


## -----------------------------------
## write csv database indexed by paper
## -----------------------------------

# import csv
# csvWriter = csv.writer(open('papersDB.csv', 'ab'), delimiter=',')

# for r in range(numExercises):
    # csvWriter.writerow([name, date, exerciseNames[r], exerciseNums[r]])
