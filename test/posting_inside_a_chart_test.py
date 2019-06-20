import time
import pytest
from miros import spy_on, stripped, pp
from miros import signals, Event
from miros import return_status as state
from miros import ActiveObject


assert(pp)  # to make an irritating pep8 error go away


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
#   |      |                          period=0.1,                |  |  |
#   |      |                          deferred=True)             |  |  B (print("flash B!"))
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
                      period=0.1,
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
  elif(e.signal == signals.READY):
    status = ao.trans(arming)
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
                      period=0.1,
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
def test_interior_postings_example():
  ao = ActiveObject()
  ao.start_at(middle)
  time.sleep(0.4)
  ao.post_fifo(Event(signal=signals.D))
  time.sleep(0.5)  # if you don't wait it won't look like it is working
  pp(ao.spy)
  assert(ao.spy_full() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:middle',
     'SEARCH_FOR_SUPER_SIGNAL:outer',
     'ENTRY_SIGNAL:outer',
     'ENTRY_SIGNAL:middle',
     'INIT_SIGNAL:middle',
     '<- Queued:(0) Deferred:(0)',
     'A:middle',
     'SEARCH_FOR_SUPER_SIGNAL:inner',
     'ENTRY_SIGNAL:inner',
     'POST_DEFERRED:B',
     'INIT_SIGNAL:inner',
     '<- Queued:(0) Deferred:(1)',
     'A:inner',
     'A:middle',
     'EXIT_SIGNAL:inner',
     'SEARCH_FOR_SUPER_SIGNAL:inner',
     'ENTRY_SIGNAL:inner',
     'POST_DEFERRED:B',
     'INIT_SIGNAL:inner',
     '<- Queued:(0) Deferred:(2)',
     'A:inner',
     'A:middle',
     'EXIT_SIGNAL:inner',
     'SEARCH_FOR_SUPER_SIGNAL:inner',
     'ENTRY_SIGNAL:inner',
     'POST_DEFERRED:B',
     'INIT_SIGNAL:inner',
     '<- Queued:(0) Deferred:(3)',
     'D:inner',
     'D:middle',
     'D:outer',
     'RECALL:B',
     'POST_FIFO:B',
     'D:outer:HOOK',
     '<- Queued:(1) Deferred:(2)',
     'B:inner',
     'B:middle',
     'B:outer',
     'EXIT_SIGNAL:inner',
     'EXIT_SIGNAL:middle',
     'EXIT_SIGNAL:outer',
     'ENTRY_SIGNAL:outer',
     'RECALL:B',
     'POST_FIFO:B',
     'INIT_SIGNAL:outer',
     '<- Queued:(1) Deferred:(1)',
     'B:outer',
     'EXIT_SIGNAL:outer',
     'ENTRY_SIGNAL:outer',
     'RECALL:B',
     'POST_FIFO:B',
     'INIT_SIGNAL:outer',
     '<- Queued:(1) Deferred:(0)',
     'B:outer',
     'EXIT_SIGNAL:outer',
     'ENTRY_SIGNAL:outer',
     'INIT_SIGNAL:outer',
     '<- Queued:(0) Deferred:(0)'])

@pytest.mark.tazor
@pytest.mark.postings
def test_tazor_example():
  tazor = ActiveObject()
  tazor.start_at(arming)
  time.sleep(0.4)
  tazor.post_fifo(Event(signal=signals.TRIGGER_PULLED))
  time.sleep(0.1)  # if you don't wait it won't look like it is working

  assert(tazor.spy_full() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:arming',
     'SEARCH_FOR_SUPER_SIGNAL:tazor_operating',
     'ENTRY_SIGNAL:tazor_operating',
     'ENTRY_SIGNAL:arming',
     'INIT_SIGNAL:arming',
     '<- Queued:(0) Deferred:(0)',
     'BATTERY_CHARGE:arming',
     'SEARCH_FOR_SUPER_SIGNAL:armed',
     'ENTRY_SIGNAL:armed',
     'POST_DEFERRED:CAPACITOR_CHARGE',
     'INIT_SIGNAL:armed',
     '<- Queued:(0) Deferred:(1)',
     'BATTERY_CHARGE:armed',
     'BATTERY_CHARGE:arming',
     'EXIT_SIGNAL:armed',
     'SEARCH_FOR_SUPER_SIGNAL:armed',
     'ENTRY_SIGNAL:armed',
     'POST_DEFERRED:CAPACITOR_CHARGE',
     'INIT_SIGNAL:armed',
     '<- Queued:(0) Deferred:(2)',
     'BATTERY_CHARGE:armed',
     'BATTERY_CHARGE:arming',
     'EXIT_SIGNAL:armed',
     'SEARCH_FOR_SUPER_SIGNAL:armed',
     'ENTRY_SIGNAL:armed',
     'POST_DEFERRED:CAPACITOR_CHARGE',
     'INIT_SIGNAL:armed',
     '<- Queued:(0) Deferred:(3)',
     'TRIGGER_PULLED:armed',
     'TRIGGER_PULLED:arming',
     'TRIGGER_PULLED:tazor_operating',
     'RECALL:CAPACITOR_CHARGE',
     'POST_FIFO:CAPACITOR_CHARGE',
     'TRIGGER_PULLED:tazor_operating:HOOK',
     '<- Queued:(1) Deferred:(2)',
     'CAPACITOR_CHARGE:armed',
     'CAPACITOR_CHARGE:arming',
     'CAPACITOR_CHARGE:tazor_operating',
     'EXIT_SIGNAL:armed',
     'EXIT_SIGNAL:arming',
     'EXIT_SIGNAL:tazor_operating',
     'ENTRY_SIGNAL:tazor_operating',
     'RECALL:CAPACITOR_CHARGE',
     'POST_FIFO:CAPACITOR_CHARGE',
     'INIT_SIGNAL:tazor_operating',
     '<- Queued:(1) Deferred:(1)',
     'CAPACITOR_CHARGE:tazor_operating',
     'EXIT_SIGNAL:tazor_operating',
     'ENTRY_SIGNAL:tazor_operating',
     'RECALL:CAPACITOR_CHARGE',
     'POST_FIFO:CAPACITOR_CHARGE',
     'INIT_SIGNAL:tazor_operating',
     '<- Queued:(1) Deferred:(0)',
     'CAPACITOR_CHARGE:tazor_operating',
     'EXIT_SIGNAL:tazor_operating',
     'ENTRY_SIGNAL:tazor_operating',
     'INIT_SIGNAL:tazor_operating',
     '<- Queued:(0) Deferred:(0)'])
  print(tazor.trace())


@pytest.mark.postings
@pytest.mark.live_spy
@pytest.mark.live_trace
@pytest.mark.tazor
def test_live_spys():
  tazor = ActiveObject()
  tazor.live_spy = True
  tazor.live_trace = True
  tazor.start_at(arming)
  time.sleep(0.1)
  tazor.post_fifo(Event(signal=signals.READY))
  time.sleep(0.1)
  # print(tazor.trace())
  # pp(tazor.spy())


@pytest.mark.tazor
def test_trace_testing():
  tazor = ActiveObject()
  tazor.start_at(arming)
  time.sleep(0.4)
  target_with_timestamp = tazor.trace()
  print(target_with_timestamp)
  other_with_timestamp = tazor.trace()

  with stripped(target_with_timestamp) as twt, \
       stripped(other_with_timestamp) as owt:

    for target_item, other_item in zip(twt, owt):
      print(target_item)
      assert(target_item == other_item)

  with stripped('[2017-11-05 15:17:39.424492] [75c8c] e->BATTERY_CHARGE() armed->armed') as swt:
    assert(swt == '[75c8c] e->BATTERY_CHARGE() armed->armed')

  assert(tazor.state.fun.__name__ == 'armed')

