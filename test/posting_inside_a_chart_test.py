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
#   |      |                        name='multishot_id')         |  |  |
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


@pytest.mark.postings
def test_interior_postings_example(fabric_fixture):
  ao = ActiveObject()
  ao.start_at(middle)
  time.sleep(4.0)
  ao.post_fifo(Event(signal=signals.D))
  time.sleep(0.1)  # if you don't wait it won't look like it is working
  pp(ao.spy_full())


################################################################################
#                          Posting Inside of a chart                           #
################################################################################
#
#   +---------------------- tazor operating ------------------------+
#   | entry/ recall()                                               |
#   | TRIGGER_PULLED/ recall()                                      |
#   |      +------------------ arming ---------------------------+  +--+
#   |      | entry/ multishot_id = \                             |  |  |
#   |      |          chart.post_fifo(                           |  |  |
#   |      |             Event(signal=signal.BATTTERY_CHARGE,    |  |  |
#   |      |             times=3,                                |  |  |
#   |      |             period=1.0,                             |  |  |
#   |      |             deffered=True)                          |  |  B* (print("zapping!"))
#   |      |          chart.augment(other=multishot_id,          |  |  |
#   |      |                        name='multishot_id')         |  |  |
#   |      | exit/ chart.cancel_event(chart.multishot_id)        |  |  |
#   |      |                                                     |  |  |
#   |      |         +---------- armed ------------------------+ |  <--+
#   |      |         | entry/ chart.defer(                     | |  |
#   |      |         |          Event(signal=signals.B))       | |  |
#   |      |         |            signal= \                    | |  |
#   |      |         |              signals.CAPACITOR_CHARGE   | |  |
#   |      |         |                                         | |  |
#   |      |         | *----->                                 | |  |
#   |      -----A*--->   print("charging tazor")               | |  |
#   |      |         +-----------------------------------------+ |  |
#   |      +-----------------------------------------------------+  |
#   +---------------------------------------------------------------+
#
#  A* -> BATTERY_CHARGE
#  B* -> CAPACITOR_CHARGE
#
# Here we are testing a charge that can post to itself
@spy_on
def tazor_operating(ao, e):
  status = state.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    ao.recall()
    status = state.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = state.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    status = state.HANDLED
  elif(e.signal == signals.TRIGGER_PULLED):
    ao.recall()
    status = state.HANDLED
  elif(e.signal == signals.CAPACITOR_CHARGE):
    print("zapping")
    status = ao.trans(tazor_operating)
  else:
    status, ao.temp.fun = state.SUPER, ao.top
  return status


@spy_on
def arming(ao, e):
  status = state.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    multi_shot_thread = \
      ao.post_fifo(Event(signal=signals.BATTERY_CHARGE),
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
  elif(e.signal == signals.BATTERY_CHARGE):
    status = ao.trans(armed)
  else:
    status, ao.temp.fun = state.SUPER, tazor_operating
  return status


@spy_on
def armed(ao, e):
  status = state.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    ao.defer(Event(signal=signals.CAPACITOR_CHARGE))
    status = state.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = state.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    print("charging tazor")
    status = state.HANDLED
  else:
    status, ao.temp.fun = state.SUPER, arming
  return status


@pytest.mark.postings
@pytest.mark.tazor
def test_tazoro_example(fabric_fixture):
  tazor = ActiveObject()
  tazor.start_at(arming)
  time.sleep(4.0)
  tazor.post_fifo(Event(signal=signals.TRIGGER_PULLED))
  time.sleep(2.1)  # if you don't wait it won't look like it is working
  pp(tazor.spy_full())
  print(tazor.trace())
