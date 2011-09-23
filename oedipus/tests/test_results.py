import fudge
from nose.tools import eq_, assert_raises

from oedipus import S
from oedipus.tests import Biscuit, SphinxMockingTestCase


class ResultsTestCase(SphinxMockingTestCase):
    """Tests for various result formatters"""

    @fudge.patch('sphinxapi.SphinxClient')
    def test_objects(self, sphinx_client):
        """Test constructing and iterating over object-style results."""
        self.mock_sphinx(sphinx_client)

        results = list(S(Biscuit))  # S.__iter__ and DictResults.__iter__

        eq_(results[0].color, 'red')
        eq_(results[1].color, 'blue')

    @fudge.patch('sphinxapi.SphinxClient')
    def test_dicts_all_fields(self, sphinx_client):
        """Test constructing and iterating over dict-style results returning all model fields."""
        self.mock_sphinx(sphinx_client)
        results = list(S(Biscuit).values_dict())
        eq_(results, [{'color': 'red', 'id': 123},
                      {'color': 'blue', 'id': 124}])

    @fudge.patch('sphinxapi.SphinxClient')
    def test_dicts_without_id(self, sphinx_client):
        """Test dict-style results with explicit fields excluding ID."""
        self.mock_sphinx(sphinx_client)
        results = list(S(Biscuit).values_dict('color'))
        eq_(results, [{'color': 'red'},
                      {'color': 'blue'}])

    @fudge.patch('sphinxapi.SphinxClient')
    def test_dicts_overriding(self, sphinx_client):
        """Calls to ``values_dict()`` should override previous ones."""
        self.mock_sphinx(sphinx_client)
        results = list(S(Biscuit).values_dict('color').values_dict('id'))
        eq_(results, [{'id': 123},
                      {'id': 124}])

    @fudge.patch('sphinxapi.SphinxClient')
    def test_tuples(self, sphinx_client):
        """Test constructing and iterating over tuple-style results returning all model fields."""
        self.mock_sphinx(sphinx_client)
        results = list(S(Biscuit).values('id', 'color'))
        eq_(results, [(123, 'red'), (124, 'blue')])

    @fudge.patch('sphinxapi.SphinxClient')
    def test_tuples_without_id(self, sphinx_client):
        """Test tuple-style results that don't return ID."""
        self.mock_sphinx(sphinx_client)
        results = list(S(Biscuit).values('color'))
        eq_(results, [('red',), ('blue',)])

    @fudge.patch('sphinxapi.SphinxClient')
    def test_tuples_overriding(self, sphinx_client):
        """Calls to ``values()`` should override previous ones."""
        self.mock_sphinx(sphinx_client)
        results = list(S(Biscuit).values('color').values('id'))
        eq_(results, [(123,), (124,)])

    @fudge.patch('sphinxapi.SphinxClient')
    def test_tuples_no_fields(self, sphinx_client):
        """An empty values() call should raise ``TypeError``."""
        s = S(Biscuit)
        assert_raises(TypeError, s.values)