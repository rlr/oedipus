class SearchResults(object):
    """Results in the order in which they came out of Sphinx

    Since Sphinx stores no non-numerical attributes, we have to reach into the
    DB to pull them out.

    """
    def __init__(self, type, results, fields):
        self.type = type
        self.results = results
        self.fields = fields  # tuple
        matches = results['matches']
        # Sphinx may return IDs of objects since deleted from the DB.
        self.ids = [r['id'] for r in matches]
        self.objects = dict(self._objects())  # {id: obj/tuple/dict, ...}

    def _queryset(self):
        """Return a QuerySet of the objects parallel to the found docs."""
        return self.type.objects.filter(id__in=self.ids)

    def __iter__(self):
        """Iterate over results in the same order they came out of Sphinx."""
        # Ripped off from elasticutils
        return (self.objects[id] for id in self.ids if id in self.objects)

    def __len__(self):
        return len(self.objects)


class DictResults(SearchResults):
    """Results as an iterable of dictionaries"""
    def _dicts_with_ids(self):
        """Return an iterable of dicts with ``id`` attrs, each representing a matched DB object."""
        fields = self.fields
        # Append ID to the requested fields so we can keep track of object
        # identity to sort by weight (or whatever Sphinx sorted by). We could
        # optimize slightly by not prepending ID if the user already
        # specifically asked for it, but then we'd have to keep track of its
        # offset.
        if fields and 'id' not in fields:
            fields += ('id',)

        # Get values rather than values_list, because we need to be able to
        # find the ID afterward, and we don't want to have to go rooting around
        # in the Django model to figure out what order the fields were declared
        # in in the case that no fields were passed in.
        return self._queryset().values(*fields)

    def _objects(self):
        """Return an iterable of (document ID, dict) pairs."""
        should_strip_ids = self.fields and 'id' not in self.fields
        for d in self._dicts_with_ids():
            id = d.pop('id') if should_strip_ids else d['id']
            yield id, d


class TupleResults(DictResults):
    """Results as an iterable of tuples, like Django's values_list()"""
    def _objects(self):
        """Return an iterable of (document ID, tuple) pairs."""
        for d in self._dicts_with_ids():
            yield d['id'], tuple(d[k] for k in self.fields)


class ObjectResults(SearchResults):
    """Results as an iterable of Django model-like objects"""
    def _objects(self):
        """Return an iterable of (document ID, model object) pairs."""
        # Assuming the document ID is called "id" lets us depend on fewer
        # Djangoisms than assuming it's the pk; we'd have to get
        # self.type._meta to get the name of the pk.
        return ((o.id, o) for o in self._queryset())