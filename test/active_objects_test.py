import time
import pytest
import pprint

from miros import spy_on
from miros.activeobject import ActiveObject, ActiveFabric
from miros import signals, Event, return_status


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
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(c2_s3)
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


#  The following state chart is used to test topology B
#
#           +------- b1_s1 -----------s-----+
#           |  +---- b1_s2 -----t-------+   |
#           |  | i/pub(bb)              |   | --> bb
#           |  |  +- b1_s3 -------+     |   |
#           |  |  |               |     |   |
#           |  |  |               <-b-+ <-a-+
#           |  |  +---------------+   +-+   |
#           |  +------------------------+   |
#           +-------------------------------+
#
# This is used for testing the type B topology in the trans_ method of the Hsm
# class.
#   * test_trans_topology_b1_1 - start in graph_b1_s2 (diagram)
#   * test_trans_topology_b1_2 - start in graph_b1_s3 (diagram)
@spy_on
def b1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    chart.post_fifo(Event(signal=signals.B))
    status = chart.trans(b1_s2)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


@spy_on
def b1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.publish(Event(signal=signals.BB))
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(b1_s3)
  else:
    status, chart.temp.fun = return_status.SUPER, b1_s1
  return status


@spy_on
def b1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, b1_s2
  return status


@pytest.mark.aos
def test_import(fabric_fixture):
  ao = ActiveObject()
  assert(ao is not None)


@pytest.mark.aos
def test_start_stop_b(fabric_fixture):
  ao1 = ActiveObject()
  ao1.start_at(b1_s3)
  time.sleep(0.2)
  ao1.post_fifo(Event(signal=signals.A))
  time.sleep(0.2)
  pp(ao1.spy_full())


@pytest.mark.aos
def test_start_stop_c(fabric_fixture):
  ao1 = ActiveObject()
  ao1.start_at(c2_s3)
  time.sleep(0.2)
  ao1.post_fifo(Event(signal=signals.A))
  time.sleep(0.2)
  pp(ao1.spy_full())


@pytest.mark.aos
def test_publish_subscribe(fabric_fixture):
  c1 = ActiveObject("c1")
  c2 = ActiveObject("c2")
  b = ActiveObject("b")
  c1.subscribe(signals.BB)
  c2.subscribe(Event(signal=signals.BB))
  c1.subscribe(Event(signal=signals.CC))
  c2.subscribe(Event(signal=signals.CC))
  b.live_trace = True
  c1.live_trace = True
  c2.live_trace = True
  c1.start_at(c2_s2)
  c2.start_at(c2_s2)
  b.start_at(b1_s2)
  time.sleep(0.2)
  c1.post_fifo(Event(signal=signals.CC))
  time.sleep(0.1)
  assert(c1.spy_full() == \
      ['POST_LIFO:SUBSCRIBE_META_SIGNAL',
        'POST_LIFO:SUBSCRIBE_META_SIGNAL',
        'START',
        'SEARCH_FOR_SUPER_SIGNAL:c2_s2',
        'SEARCH_FOR_SUPER_SIGNAL:c2_s1',
        'ENTRY_SIGNAL:c2_s1',
        'ENTRY_SIGNAL:c2_s2',
        'INIT_SIGNAL:c2_s2',
        '<- Queued:(2) Deferred:(0)',
        'SUBSCRIBE_META_SIGNAL:c2_s2',
        'SUBSCRIBE_META_SIGNAL:c2_s1',
        'SUBSCRIBING TO:(CC, TYPE:fifo)',
        '<- Queued:(1) Deferred:(0)',
        'SUBSCRIBE_META_SIGNAL:c2_s2',
        'SUBSCRIBE_META_SIGNAL:c2_s1',
        'SUBSCRIBING TO:(BB, TYPE:fifo)',
        '<- Queued:(0) Deferred:(0)',
        'BB:c2_s2',
        'BB:c2_s1',
        'EXIT_SIGNAL:c2_s2',
        'SEARCH_FOR_SUPER_SIGNAL:c2_s2',
        'EXIT_SIGNAL:c2_s1',
        'ENTRY_SIGNAL:c2_s1',
        'INIT_SIGNAL:c2_s1',
        '<- Queued:(0) Deferred:(0)',
        'CC:c2_s1',
        '<- Queued:(0) Deferred:(0)']

  )

  assert(b.spy_full() == 
      ['START',
        'SEARCH_FOR_SUPER_SIGNAL:b1_s2',
        'SEARCH_FOR_SUPER_SIGNAL:b1_s1',
        'ENTRY_SIGNAL:b1_s1',
        'ENTRY_SIGNAL:b1_s2',
        'INIT_SIGNAL:b1_s2',
        'POST_LIFO:PUBLISH_META_SIGNAL',
        '<- Queued:(1) Deferred:(0)',
        'PUBLISH_META_SIGNAL:b1_s2',
        'PUBLISH_META_SIGNAL:b1_s1',
        'PUBLISH:(BB, PRIORITY:1000)',
        '<- Queued:(0) Deferred:(0)']

  )

  assert(c2.spy_full() == 
      ['POST_LIFO:SUBSCRIBE_META_SIGNAL',
        'POST_LIFO:SUBSCRIBE_META_SIGNAL',
        'START',
        'SEARCH_FOR_SUPER_SIGNAL:c2_s2',
        'SEARCH_FOR_SUPER_SIGNAL:c2_s1',
        'ENTRY_SIGNAL:c2_s1',
        'ENTRY_SIGNAL:c2_s2',
        'INIT_SIGNAL:c2_s2',
        '<- Queued:(2) Deferred:(0)',
        'SUBSCRIBE_META_SIGNAL:c2_s2',
        'SUBSCRIBE_META_SIGNAL:c2_s1',
        'SUBSCRIBING TO:(CC, TYPE:fifo)',
        '<- Queued:(1) Deferred:(0)',
        'SUBSCRIBE_META_SIGNAL:c2_s2',
        'SUBSCRIBE_META_SIGNAL:c2_s1',
        'SUBSCRIBING TO:(BB, TYPE:fifo)',
        '<- Queued:(0) Deferred:(0)',
        'BB:c2_s2',
        'BB:c2_s1',
        'EXIT_SIGNAL:c2_s2',
        'SEARCH_FOR_SUPER_SIGNAL:c2_s2',
        'EXIT_SIGNAL:c2_s1',
        'ENTRY_SIGNAL:c2_s1',
        'INIT_SIGNAL:c2_s1',
        '<- Queued:(0) Deferred:(0)']

  )
