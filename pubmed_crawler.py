# pubmed_crawler.py
# Patrick Ye


#import library to do http requests:
import urllib2

import re
import logging

#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
#from xml.dom import minidom

# import json library for json output
import json

# initialize hash table
auth_dict = {}
list_auth = []
list_hash = []
list_hashPair = []
list_papers = []



## --------------------------------------
## get all PMIDs on initial disease query
## --------------------------------------
disease = "pancreatic+neuroendocrine"
ret_max = 20

base_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"
publication_list_url = "%s&term=%s&retmax=%s" % (base_url, disease, ret_max)


def get_dom(url):
    """
    http://www.travisglines.com/web-coding/python-xml-parser-tutorial
    """
    # download the file:
    file = urllib2.urlopen(url)
    # convert to string
    data = file.read()
    # close file because we dont need it anymore
    file.close()
    return parseString(data)


def get_text(dom, tag_name, index=0):
    return dom.getElementsByTagName(tag_name)[index].toxml()

def extract_value(text, tag_name):
    matches = re.search("<%s>(.*?)</%s>" % (tag_name, tag_name), text)
    return matches.group(1)

#parse the xml you downloaded
dom = get_dom(publication_list_url)

for i in range(ret_max):

    #retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
    id_text = get_text(dom, "Id", i)
    publication_id = extract_value(id_text, "Id")
    publication_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s" % publication_id
    publication_dom = get_dom(publication_url)

    item_list = publication_dom.getElementsByTagName('Item')

    authors = []
    for s in item_list:
        if s.attributes['Name'].value == 'Title':
            title = s.childNodes[0].nodeValue
            #print title
        if s.attributes['Name'].value == 'PubDate':
            pubDate = s.childNodes[0].nodeValue
            #print pubDate
        if s.attributes['Name'].value == 'LastAuthor':
            lastAuthor = s.childNodes[0].nodeValue
            #print lastAuthor
        if s.attributes['Name'].value == 'Author':
            author = s.childNodes[0].nodeValue
            #author.encode('ascii', 'ignore')
            try:
                author = str(author)
                authors.append(author)
            except ValueError:
                pass

        # "title":"Chordoma genetic sequencing",
        # "year": 2004,
        # "month": 3,
        # "authors": [12,8,2,5],
        # "URL": 34545,
        # "disease": "Chordoma",
        # "leading": 12,
        # "last author": 5,
        # "index": 8
        
    ## -----------------------------
    ## hash authors for lookup table
    ## -----------------------------
        
    len_authors = len(authors)
    
    for i in range(len_authors):
        author = authors[i]
        author_hashed = hash(author)
        auth_dict.update({author:author_hashed})
    
    # permutations to tally papers
    for j in range(len_authors-1):
        
        author1 = authors[j]
        hash1 = auth_dict[author1]
        for k in range(j+1, len_authors):
            author2 = authors[k]
            hash2 = auth_dict[author2]
            
            hashPair = [hash1, hash2]
            hashPair = hashPair.sort()
            
            if hashPair not in list_hashPair:
                list_hashPair.append(hashPair)
                list_papers.append(int(publication_id))
    
print auth_dict
print list_hashPair
print list_papers    

    ## --------------------------------
    ## write json file indexed by paper
    ## --------------------------------

    # print json.dumps({'PMID':publication_id, 'title':title, 'title':title, 'disease':disease})
    # with open('papers.txt', 'aw') as outfile:
    #     json.dumps({'PMID': publication_id, 'title':title, 'disease':disease}, outfile)
