import urllib2
from xml.dom.minidom import parseString
import re
from datetime import date
import logging
from models import Author, Publication


ret_max = 50
base_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed"


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
    elems = dom.getElementsByTagName(tag_name)
    if len(elems) == 0:
        return ""
    return dom.getElementsByTagName(tag_name)[index].toxml()


def extract_value(text, tag_name):
    matches = re.search("<%s>(.*?)</%s>" % (tag_name, tag_name), text)
    if not matches:
        return ""
    return matches.group(1)


def get_value(dom, tag_name, index=0):
    text = get_text(dom, tag_name, index)
    return extract_value(text, tag_name)


def scrape_pubmed(disease, query):
    publication_list_url = "%s&term=%s&retmax=%s" % (base_url, query, ret_max)

    dom = get_dom(publication_list_url)
    count = int(extract_value(get_text(dom, "Count"), "Count"))

    num_results = min(ret_max, count)
    for i in range(num_results):

        #retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
        publication_id = get_value(dom, "Id", i)
        publication_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id=%s" % publication_id
        publication_dom = get_dom(publication_url)

        # extract features
        title = get_value(publication_dom, "ArticleTitle")
        affiliation = get_value(publication_dom, "Affiliation")

        year = int(get_value(publication_dom, "Year"))
        month = int(get_value(publication_dom, "Month"))
        day = int(get_value(publication_dom, "Day"))
        pub_date = date(year, month, day)

        # get all author_names
        author_names = []

        def getText(nodelist):
            rc = []
            for node in nodelist:
                if node.nodeType == node.TEXT_NODE:
                    rc.append(node.data)
            return ''.join(rc)

        def handleLastName(lastName):
            lastNameOut = getText(lastName.childNodes)
            return lastNameOut

        def handleForeName(foreName):
            foreNameOut = getText(foreName.childNodes)
            return foreNameOut

        def processAuthorElem(elem):
            if len(elem.getElementsByTagName("LastName")) != 0:
                last_name = handleLastName(elem.getElementsByTagName("LastName")[0])
                fore_name = handleForeName(elem.getElementsByTagName("ForeName")[0])
                author_names.append("%s, %s" % (last_name, fore_name))

        def processAuthors(dom):
            author_elems = dom.getElementsByTagName("Author")
            for elem in author_elems:
                processAuthorElem(elem)

        processAuthors(publication_dom)

        # create author models
        for name in author_names:
            author = Author.get_or_insert(name, name=name)
            # TODO: fix this so it's appending instead of overwriting
            author.diseases = [disease]

            author.put()

        # create publication model
        pub = Publication.get_or_insert(publication_id, pubmed_id=publication_id)
        pub.title = title
        pub.publication_date = pub_date
        pub.author_names = author_names
        pub.affiliation = affiliation
        # TODO: fix this so it's appending instead of overwriting
        pub.diseases = [disease]

        pub.put()
