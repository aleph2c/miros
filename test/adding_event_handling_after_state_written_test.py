import time
import pytest
import pprint

from miros.hsm import spy_on
from miros.activeobject import ActiveObject, ActiveFabric
from miros.event import signals, Event, return_status
from collections import namedtuple

def pp(item):
  print("")
  pprint.pprint(item)


# diagram for next set of state functions
#
#  The following state chart is used to test topology C
#
#        +------------------- c2_s1 -----------+
#        |   +------ c2_s2-+   +------ c2_s3-+ |
#        | * |             |   |             | +----+
#        | | |             +-a->             | |    |
#        | +->             <-a-+             | |    bb
#        |   |             |   |             | |    |
#        |   |             |   |             | <----+
#        |   +-------------+   +-------------+ |
#        +-------------------------------------+
#
# This is used for testing the type C topology within another state, in the trans_
# method of the HsmEventProcessor class.
@spy_on
def c2_s1(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.trans(c2_s2)
  elif(e.signal == signals.BB):
    status = chart.trans(c2_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


@spy_on
def c2_s2(chart, e):
  with chart.filter(e) as fn:
    status = fn(chart, e)

  if(status == return_status.UNHANDLED):
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, c2_s1
  return status


@spy_on
def c2_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(c2_s2)
  else:
    status, chart.temp.fun = return_status.SUPER, c2_s1
  return status


@pytest.mark.post_add
def test_post_addition_of_signal_handling(fabric_fixture):

  def trans_to_c2_s3(chart, e):
    return chart.trans(c2_s3)

  ao = ActiveObject()
  ao.register_filter(c2_s2, signals.A, trans_to_c2_s3)
  ao.start_at(c2_s2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.30)
  pp(ao.spy())



