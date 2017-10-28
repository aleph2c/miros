import time
import pytest
from miros.hsm import spy_on
from miros.event import signals, Event
from miros.event import return_status as state
from miros.activeobject import ActiveObject, ActiveFabric
import pprint


def pp(item):
  pprint.pprint(item)


################################################################################
#                          Posting Inside of a chart                           #
################################################################################
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
#   |      -----A---->   print("charging with B")              | |  |
#   |      |         +-----------------------------------------+ |  |
#   |      +-----------------------------------------------------+  |
#   +---------------------------------------------------------------+
#
# Here we are testing a charge that can post to itself
@spy_on
def outer(ao, e):
  status = state.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    ao.recall()
    status = state.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = state.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    status = state.HANDLED
  elif(e.signal == signals.D):
    ao.recall()
    status = state.HANDLED
  elif(e.signal == signals.B):
    print("flash B!")
    status = ao.trans(outer)
  else:
    status, ao.temp.fun = state.SUPER, ao.top
  return status


@spy_on
def middle(ao, e):
  status = state.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    multi_shot_thread = \
      ao.post_fifo(Event(signal=signals.A),
                      times=3,
                      period=1.0,
                      deferred=True)
    # We mark up the ao with this id, so that
    # state function can be used by many different aos
    ao.augment(other=multi_shot_thread,
                  name='multi_shot_thread')
    status = state.HANDLED

  elif(e.signal == signals.EXIT_SIGNAL):
    ao.cancel_event(ao.multi_shot_thread)
    status = state.HANDLED

  if(e.signal == signals.INIT_SIGNAL):
    status = state.HANDLED
  elif(e.signal == signals.A):
    status = ao.trans(inner)
  else:
    status, ao.temp.fun = state.SUPER, outer
  return status


@spy_on
def inner(ao, e):
  status = state.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    ao.defer(Event(signal=signals.B))
    status = state.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = state.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    print("charging with B")
    status = state.HANDLED
  else:
    status, ao.temp.fun = state.SUPER, middle
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
  time.sleep(3.5)
  ao.post_fifo(Event(signal=signals.D))
  time.sleep(0.1)  # if you don't wait it won't look like it is working
  pp(ao.spy_full())
