from google.appengine.ext import ndb


class Author(ndb.Model):
    # key is name
    name = ndb.StringProperty(required=True)
    diseases = ndb.StringProperty(repeated=True)

    _serialize_blacklist = ["key", "publications"]

    @classmethod
    def all(cls):
        return cls.query().fetch(1000)

    @classmethod
    def flush(cls):
        authors = cls.query().fetch(1000, keys_only=True)
        for author in authors:
            author.delete()

    @classmethod
    def get_for_disease(cls, disease_slug, **kwargs):
        return cls.query(cls.diseases == disease_slug).fetch(1000, **kwargs)

    @property
    def publications(self):
        return Publication.get_for_author_name(self.name)


class Publication(ndb.Model):
    # key is pubmed_id
    pubmed_id = ndb.StringProperty(required=True)
    title = ndb.StringProperty()
    date_published = ndb.DateProperty()
    affiliation = ndb.StringProperty()

    diseases = ndb.StringProperty(repeated=True)
    author_names = ndb.StringProperty(repeated=True)

    _serialize_blacklist = ["key"]

    @classmethod
    def all(cls):
        return cls.query().order(-cls.date_published).fetch(1000)

    @classmethod
    def flush(cls):
        pubs = cls.query().fetch(1000, keys_only=True)
        for pub in pubs:
            pub.delete()

    @classmethod
    def get_for_author_name(cls, author_name, **kwargs):
        return cls.query(cls.author_names == author_name).order(-cls.date_published).fetch(1000, **kwargs)

    @classmethod
    def get_for_disease(cls, disease_slug, **kwargs):
        return cls.query(cls.diseases == disease_slug).order(-cls.date_published).fetch(1000, **kwargs)

    @classmethod
    def get_disease_counts(cls):
        pubs = cls.all()
        disease_count = {}
        for pub in pubs:
            for d in pub.diseases:
                if d not in disease_count:
                    disease_count[d] = 0
                else:
                    disease_count[d] += 1

        return disease_count


class Link(ndb.Model):
    # key is str(combo.__hash__()) where combo is tuple of author names
    # (source, sink)
    source = ndb.KeyProperty()
    sink = ndb.KeyProperty()

    diseases = ndb.StringProperty(repeated=True)
    publications = ndb.StringProperty(repeated=True)  # pubmed id

    _serialize_blacklist = ["key"]

    @classmethod
    def all(cls):
        return cls.query().fetch(1000)

    @classmethod
    def get_for_disease(cls, disease_slug, **kwargs):
        return cls.query(cls.diseases == disease_slug).fetch(1000, **kwargs)
