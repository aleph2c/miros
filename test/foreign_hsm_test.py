import time
import pytest
from miros.hsm import spy_on, pp
from miros.hsm import stripped
from miros.activeobject import ActiveObject
from miros.event import signals, Event, return_status
from miros.foreign import Hsm as ForeignHsm

@pytest.mark.fhsm
def test_anything():
  fhsm = ForeignHsm()
  assert(fhsm != None)
