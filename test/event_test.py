import pytest
from miros.event import OrderedDictWithParams

def test_ordered_dict_with_params():
  od = OrderedDictWithParams()
  assert(od!=None)
