"""Test the mapping from our API to Sphinx's.

We mock out all Sphinx's APIs.

"""
import fudge
from nose import SkipTest
from nose.tools import eq_
import sphinxapi  # Comes in sphinx source code tarball

from oedipus import S, MIN_LONG, MAX_LONG, _consolidate_ranges


no_results = [dict(status=0, matches=[])]  # empty Sphinx results


class Biscuit(object):
    """An arbitrary adaptation key that S can map to a SearchModel"""

    class SphinxMeta(object):
        """Search metadata for Biscuit"""
        index = 'biscuit'


@fudge.patch('sphinxapi.SphinxClient')
def test_initialization(sphinx_client):
    """S-wide default modes should get set when the SphinxClient is made."""
    (sphinx_client.expects_call().returns_fake()
                  .is_a_stub()  # Call other crap on it if you want; I don't care.
                  .expects('SetMatchMode').with_args(sphinxapi.SPH_MATCH_EXTENDED2)
                  .expects('SetRankingMode').with_args(sphinxapi.SPH_RANK_PROXIMITY_BM25)
                  .expects('SetSortMode').with_args(sphinxapi.SPH_SORT_RELEVANCE, ''))
    S(Biscuit)._sphinx()


@fudge.patch('sphinxapi.SphinxClient')
def test_no_query(sphinx_client):
    """Evaluating without calling query() should run an empty query."""
    (sphinx_client.expects_call().returns_fake()
                  .is_a_stub()
                  .expects('AddQuery').with_args('', 'biscuit')
                  .expects('RunQueries').returns([dict(status=0, matches=[])]))
    S(Biscuit).raw()


@fudge.patch('sphinxapi.SphinxClient')
def test_simple_query(sphinx_client):
    """A lone call to query(any_=...) should pass through to Sphinx.

    Control chars should be stripped. Other kwargs should be ignored.

    """
    (sphinx_client.expects_call().returns_fake()
                  .is_a_stub()
                  .expects('AddQuery').with_args('gerbil', 'biscuit')
                  .expects('RunQueries').returns([dict(status=0, matches=[])]))
    S(Biscuit).query('^$gerbil', ignored_kwarg='dummy').raw()


@fudge.patch('sphinxapi.SphinxClient')
def test_single_filter(sphinx_client):
    """A filter call should be translated into the right Sphinx API calls."""
    (sphinx_client.expects_call().returns_fake()
                  .is_a_stub()
                  .expects('SetFilter').with_args('a', [1], False)
                  .expects('SetFilter').with_args('b', [2, 3], False)

                  # These 2 lines must be ordered such. Why? Fudge bug?
                  .expects('SetFilterRange').with_args('c', 4, MAX_LONG, False)
                  .expects('SetFilterRange').with_args('d', MIN_LONG, 5, False)

                  .expects('RunQueries').returns(no_results))
    S(Biscuit).filter(a=1,  # Test auto-listification of ints for equality filters.
                      b__in=[2, 3],
                      c__gte=4,
                      d__lte=5).raw()


@fudge.patch('sphinxapi.SphinxClient')
def test_single_exclude(sphinx_client):
    """Assert conditions invert correctly."""
    (sphinx_client.expects_call().returns_fake()
                  .is_a_stub()
                  .expects('SetFilter').with_args('b', [2, 3], True)
                  .expects('RunQueries').returns(no_results))
    S(Biscuit).exclude(b__in=[2, 3]).raw()


@fudge.patch('sphinxapi.SphinxClient')
def test_range_exclude(sphinx_client):
    """Putting a gte and a lte exclusion on the same field in the same call should set a single filter range exclusion on the query.

    Otherwise, there would be no way to say "Give me docs with X between 1 and
    10."

    """
    (sphinx_client.expects_call().returns_fake()
                  .is_a_stub()
                  .expects('SetFilterRange').with_args('a', 1, 10, True)
                  .expects('RunQueries').returns(no_results))
    S(Biscuit).exclude(a__gte=1, a__lte=10).raw()


@fudge.patch('sphinxapi.SphinxClient')
def test_range_filter(sphinx_client):
    """Putting a gte and a lte exclusion on the same field in the same call should set a single filter range exclusion on the query.

    Otherwise, there would be no way to say "Give me docs with X between 1 and
    10."

    """
    (sphinx_client.expects_call().returns_fake()
                  .is_a_stub()
                  .expects('SetFilterRange').with_args('a', 1, 10, False)
                  .expects('RunQueries').returns(no_results))
    S(Biscuit).filter(a__gte=1, a__lte=10).raw()


def test_consolidate_ranges():
    """Assert that _consolidate_ranges() collapses lte/gte pairs."""
    input = [('category', 'gte', 1),
             ('category', 'lte', 10),
             ('category', '', 5),
             ('name', '', 'frank'),
             ('pog', 'gte', 0)]
    output = set([('category', 'RANGE', (1, 10)),
                  ('category', '', 5),
                  ('name', '', 'frank'),
                  ('pog', 'gte', 0)])
    eq_(set(_consolidate_ranges(input)), output)


def test_chained_filters():
    """Test several filter() calls ANDed together."""


def test_results_as_objects():
    """Results should come back as Django model objects by default."""
    # ...though we mock those model objects because we don't really want to
    # depend on Django; anything with a similar API should work.


def test_filter_adapters():
    """You should be able to set up conversions of enumerations to hashes, for example."""


def test_defaults():
    """Defaults from the metadata should be obeyed."""
