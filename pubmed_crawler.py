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
paperInfo = []


## --------------------------------------
## get all PMIDs on initial disease query
## --------------------------------------
#disease = "renal+cell+carcinoma" # common
#disease = "myeloid+sarcoma" # rare
disease = "pulmonary+blastoma"  # rare
#disease = "pancreatoblastoma"  # rare
#disease = "ocular+melanoma"  # rare
#disease = "skin+melanoma" # common
#disease = "chordoma"  # rare, but well-organized
#disease = "ultrasound+neuromodulation" # Patrick's research
#disease = "pancreatic+neuroendocrine"  # rare?
print(disease)
ret_max = 200000

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
count_text = get_text(dom, "Count")
count = int(extract_value(count_text, "Count"))
print count

for i in range(count):
    
    if i % 100 == 0:
        print i
    
    # source for more XML information: efetch instead of esummary
    # http://lifeasclay.wordpress.com/2010/07/06/how-to-query-pubmed-and-retrieve-xml-results/
    
    #retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
    id_text = get_text(dom, "Id", i)
    publication_id = extract_value(id_text, "Id")
    
    publication_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=%s" % publication_id

    # publication_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s" % publication_id
    
    publication_dom = get_dom(publication_url)
    
    # extract features
    if len(publication_dom.getElementsByTagName("Affiliation")) != 0:
        affil_text = get_text(publication_dom, "Affiliation")
        affiliation= extract_value(affil_text, "Affiliation")
    
    title_text = get_text(publication_dom, "ArticleTitle")
    title = extract_value(title_text, "ArticleTitle")
    
    year_text = get_text(publication_dom, "Year")
    year = extract_value(year_text, "Year")

    month_text = get_text(publication_dom, "Month")
    month = extract_value(month_text, "Month")

    day_text = get_text(publication_dom, "Day")
    day = extract_value(day_text, "Day")
    
    pub_date = str(year) + '-' + str(month) + '-' + str(day)
    
    # get all authors
    authors = []
    
    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)
    
    def handleAll(dom):
        authors = dom.getElementsByTagName("Author")
        handleAuthors(authors)

    def handleAuthors(authors):
        for author in authors:
            handleAuthor(author)
            
    def handleAuthor(author):
        if len(author.getElementsByTagName("LastName")) != 0:
            lastNameOut = handleLastName(author.getElementsByTagName("LastName")[0])
            foreNameOut = handleForeName(author.getElementsByTagName("ForeName")[0])
            fullName = lastNameOut + ', ' + foreNameOut
            authors.append(fullName)
        
    def handleLastName(lastName):
        lastNameOut = getText(lastName.childNodes)
        return lastNameOut

    def handleForeName(foreName):
        foreNameOut = getText(foreName.childNodes)
        return foreNameOut
        
    handleAll(publication_dom)
    

    ## -----------------------------------
    ## paper info to array for json output
    ## -----------------------------------
    
    this_paper_info = {
                'PMIDs':publication_id,
                'title':title,
                #'journal':journal,
                'pub_date':pub_date
                }
    paperInfo.append(this_paper_info)
        
    ## -----------------------------
    ## hash authors for lookup table
    ## -----------------------------

    len_authors = len(authors)

    for i in range(len_authors):
        author = authors[i]
        if author not in list_auth:
            list_auth.append(author)
            list_papersAuth.append([])
    # for i in range(len_authors):
        # author = authors[i]
        # author_hashed = hash(author)
        # auth_dict.update({author:author_hashed})
    
    
    # tally papers by single author
    for g in range(len_authors):
        list_author_idx = list_auth.index(authors[g])
        list_papersAuth[list_author_idx].append(int(publication_id))    
    
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
authorPairs = []
for h in range(len_pairs):
    count.append(len(list_papersPair[h]))
    jsonOut = {
            'authorA':list_hashPair[h][0],
            'authorB':list_hashPair[h][1],
            'paperCount':count[h],
            'PMIDs':list_papersPair[h]
            }
    #print jsonOut
    authorPairs.append(jsonOut)

## ---------------------------------
## json file for author paper output    
## ---------------------------------

len_authors = len(list_auth)
authorsOnly = []
for h in range(len_authors):
    jsonAuth = {
            'author_id':h,
            'author_name':list_auth[h],
            'papers':list_papersAuth[h]
            }
    #print jsonAuth
    authorsOnly.append(jsonAuth)
    
    
libAuth = {}
libAuth['authorPairs'] = authorPairs
libAuth['authorsOnly'] = authorsOnly
libAuth['paperInfo'] = paperInfo

filename = disease + '.txt'
with open(filename, 'wa') as outfile:
    json.dump(libAuth, outfile)


    
#print auth_dict
#print list_hashPair
#print list_papers
#print count
#print list_papersAuth


# ## --------------------------------
# ## write json file indexed by paper
# ## --------------------------------


# # print json.dumps({'PMID':publication_id, 'title':title, 'title':title, 'disease':disease})
# with open('papers.txt', 'aw') as outfile:
    # json.dumps({'PMID': publication_id, 'title':title, 'disease':disease}, outfile)
