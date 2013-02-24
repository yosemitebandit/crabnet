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
list_papersAuth = []
list_papersPair = []



## --------------------------------------
## get all PMIDs on initial disease query
## --------------------------------------
disease = "ultrasound+neuromodulation"
#disease = "pancreatic+neuroendocrine"
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


        
    ## -----------------------------
    ## hash authors for lookup table
    ## -----------------------------

    len_authors = len(authors)

    for i in range(len_authors):
        author = authors[i]
        if author not in list_auth:
            list_auth.append(author)
    
    # for i in range(len_authors):
        # author = authors[i]
        # author_hashed = hash(author)
        # auth_dict.update({author:author_hashed})
    
    
    # tally papers by single author
    

    # permutations to tally papers by pairs of authors
    for j in range(len_authors-1):

        author1 = authors[j]
        hash1 = list_auth.index(author1)
        #hash1 = auth_dict[author1]
        for k in range(j+1, len_authors):
            author2 = authors[k]
            hash2 = list_auth.index(author2)
            #hash2 = auth_dict[author2]

            hashPair = [hash1, hash2]
            hashPair.sort()            

            if hashPair not in list_hashPair:
                list_hashPair.append(hashPair)
                list_papersPair.append([int(publication_id)])
            else:
                thisHashPairPapersIdx = list_hashPair.index(hashPair)
                thisHashPairPapers = list_papersPair[thisHashPairPapersIdx]
                thisHashPairPapers.append(int(publication_id))
                list_papersPair[thisHashPairPapersIdx] = thisHashPairPapers

## ---------------------------------------------------------------
## count number of papers each pair of authors has writen together
## ---------------------------------------------------------------


count = []
len_pairs = len(list_hashPair)
library = []
for h in range(len_pairs):
    count.append(len(list_papersPair[h]))
    jsonOut = {
            'authorA':list_hashPair[h][0],
            'authorB':list_hashPair[h][1],
            'paperCount':count[h],
            'PMIDs':list_papersPair[h]
            }
    print jsonOut
    library.append(jsonOut)
    
with open('papers.txt', 'w') as outfile:
    json.dump(library, outfile)         

#print auth_dict
#print list_hashPair
#print list_papers
#print count


# ## --------------------------------
# ## write json file indexed by paper
# ## --------------------------------


# # print json.dumps({'PMID':publication_id, 'title':title, 'title':title, 'disease':disease})
# with open('papers.txt', 'aw') as outfile:
    # json.dumps({'PMID': publication_id, 'title':title, 'disease':disease}, outfile)
