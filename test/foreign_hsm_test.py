import time
import pytest
from miros import spy_on, pp
from miros import stripped
from miros import ActiveObject
from miros import signals, Event, return_status
from miros.foreign import ForeignHsm

@pytest.mark.fhsm
def test_anything():
  fhsm = ForeignHsm()
  assert(fhsm != None)
