import jinja2
import os
import webapp2

import jsonify
import scraper
import logging
from itertools import combinations
from models import Author, Publication, Link


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render())


class GraphHandler(webapp2.RequestHandler):

    def return_json(self, data):
        data_json = jsonify.jsonify(data, camel_cased=True)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(data_json)

    def get_authors(self, disease_slug):
        authors = Author.get_for_disease(disease_slug)
        for author in authors:
            author.publication_ids = [pub.pubmed_id for pub in author.publications]

        return authors

    def get_publications(self, disease_slug):
        publications = Publication.get_for_disease(disease_slug)
        return publications

    def get_d3_data(self, disease_slug):
        # get authors
        authors = self.get_authors(disease_slug)

        # get publications
        pubs = self.get_publications(disease_slug)

        # generate related links using author indices
        # 1) create dict from author name to index in author list
        authors_dict = {}
        for i, author in enumerate(authors):
            authors_dict[author.name] = i

        link_dict = {}
        for pub in pubs:
            pub_authors = pub.author_names
            pub_authors.sort()
            n = len(pub_authors)
            for i in range(n - 1):
                for j in range(i + 1, n):
                    link_key = (pub_authors[i], pub_authors[j])
                    if link_key not in link_dict:
                        link_dict[link_key] = [pub.pubmed_id]
                    else:
                        link_dict[link_key].append(pub.pubmed_id)

        links = []
        for link_key in link_dict:
            index_a = authors_dict[link_key[0]]
            index_b = authors_dict[link_key[1]]
            pub_ids = link_dict[link_key]
            links.append({
                "author_a": index_a,
                "author_b": index_b,
                "paper_count": len(pub_ids),
                "publication_ids": pub_ids
            })

        return {
            "authors_only": authors,
            "author_pairs": links,
        }


    def get(self, disease_slug, group_type):

        if group_type == "authors":
            data = self.get_authors(disease_slug)

        elif group_type == "publications":
            data = self.get_publications(disease_slug)

        elif group_type == "d3":
            data = self.get_d3_data(disease_slug)

        self.return_json(data)


class AdminHandler(webapp2.RequestHandler):
    def get(self):

        disease_counts = Publication.get_disease_counts()
        authors = Author.all()
        pubs = Publication.all()

        template_values = {
            "authors": authors,
            "disease_counts": disease_counts,
            "pubs": pubs
        }

        template = jinja_environment.get_template('admin.html')
        self.response.out.write(template.render(template_values))


class ImportHandler(webapp2.RequestHandler):
    def post(self):
        # kick off the import
        query = self.request.get("query")
        disease_slug = self.request.get("disease_slug")

        if query and disease_slug:
            scraper.scrape_pubmed(disease_slug, query)

        self.redirect("/admin")


class ResetHandler(webapp2.RequestHandler):
    def post(self):
        disease_slugs = self.request.get_all("disease_slug")

        for slug in disease_slugs:
            pubs = Author.get_for_disease(slug, keys_only=True)
            for pub in pubs:
                pub.delete()

        self.redirect("/admin")


app = webapp2.WSGIApplication([
        ("/", MainPage),
        ("/admin", AdminHandler),
        ("/reset", ResetHandler),
        ("/import", ImportHandler),
        ("/disease/([^/]+)/([^/]+)", GraphHandler),

    ], debug=True)
