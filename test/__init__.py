'''
A common location for functions used within your tests.  To include one of
these functions:

from test import pp

This is different from the conftest.py file, which contains fixtures and is
automatically found by pytest.

'''
import pprint


def pp(item):
  pprint.pprint(item)

