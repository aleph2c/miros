import time
import pytest
from miros.hsm import spy_on
from miros.event import signals, Event
from miros.event import return_status as r
from miros.activeobject import ActiveObject, ActiveFabric
import pprint


def pp(item):
  pprint.pprint(item)


################################################################################
#                          Posting Inside of a chart                           #
################################################################################
#
#
#   +--------------------------- outer -----------------------------+
#   | entry/ recall()                                               |
#   | D/ recall()                                                   |
#   |      +-------------------- middle -------------------------+  +--+
#   |      | entry/ multishot_id = \                             |  |  |
#   |      |          chart.post_fifo(Event(signal=signals.A,    |  |  |
#   |      |                          times=3,                   |  |  |
#   |      |                          period=1.0,                |  |  |
#   |      |                          deffered=True)             |  |  B (print("flash B!"))
#   |      |          chart.augment(other=multishot_id,          |  |  |
#   +--C--->                        name='multishot_id')         |  |  |
#   |      | exit/ chart.cancel_event(chart.multishot_id)        |  |  |
#   |      |                                                     |  |  |
#   |      |         +---------- inner ------------------------+ |  <--+
#   |      |         | entry/ chart.defer(                     | |  |
#   |      |         |          Event(signal=signals.B))       | |  |
#   |      |         |                                         | |  |
#   |      |         | *----->                                 | |  |
#   |      -----A---->   print("inner r init")                 | |  |
#   |      |         +-----------------------------------------+ |  |
#   |      +-----------------------------------------------------+  |
#   +---------------------------------------------------------------+
#
#
# This is used for testing the type E topology in the trans_ method of the HsmEventProcessor
# class.
#   * test_hsm_next_rtc - start in active_objects_graph_g1_s22
@spy_on
def outer(chart, e):
  status = r.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    #chart.recall()
    status = r.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = r.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    status = r.HANDLED
  elif(e.signal == signals.D):
    chart.recall()
    status = r.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(outer)
  else:
    status, chart.temp.fun = r.SUPER, chart.top
  return status


@spy_on
def middle(chart, e):
  status = r.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    multi_shot_thread = \
      chart.post_fifo(Event(signal=signals.A),
                      times=3,
                      period=0.1,
                      deferred=True)
    chart.augment(other=multi_shot_thread,
                  name='multi_shot_thread')
    status = r.HANDLED

  elif(e.signal == signals.EXIT_SIGNAL):
    chart.cancel_event(chart.multi_shot_thread)
    status = r.HANDLED

  if(e.signal == signals.INIT_SIGNAL):
    status = r.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(inner)
  else:
    status, chart.temp.fun = r.SUPER, outer
  return status


@spy_on
def inner(chart, e):
  status = r.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.defer(Event(signal=signals.B))
    status = r.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = r.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    print("charging with B")
    status = r.HANDLED
  else:
    status, chart.temp.fun = r.SUPER, middle
  return status


@pytest.fixture
def fabric_fixture(request):
  yield
  # shut down the active fabric for the next test
  ActiveFabric().stop()
  ActiveFabric().clear()


@pytest.mark.onslaught
def test_onslaught(fabric_fixture):
  ao = ActiveObject()
  ao.start_at(middle)
  pp(ao.spy_full())
  time.sleep(1)
  ao.post_fifo(Event(signal=signals.D))
  ao.post_fifo(Event(signal=signals.D))
  ao.post_fifo(Event(signal=signals.D))
  ao.post_fifo(Event(signal=signals.D))
  time.sleep(1)
  pp(ao.spy_full())
  time.sleep(3)

