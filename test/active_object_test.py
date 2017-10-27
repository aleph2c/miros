import time
import pytest
import pprint
from miros.hsm import spy_on
from miros.activeobject import ActiveObject, ActiveFabric, ActiveObjectOutOfPostedEventResources
from miros.event import signals, Event, return_status


def pp(item):
  print("")
  pprint.pprint(item)


################################################################################
#                          ActiveObject Graph G1                               #
################################################################################
'''
                     +-------------------------------- g1_s1 --------------+
   +---g1_s0------+  | *i/fifo(e)                                          |
   |+-g1_s01-----+|  |                      +---------g1_s22 ----------+   |
   ||e/fifo(a)   |+------c------------------>  *i/fifo(d)              |   |
   ||e/lifo(f)   ||  |                      |                          |   |
   ||e/recall()  <-e-+                      | +-------g1_s3 ---------+ |   |
   |+------------+|  |                      | | *i/defer(f)          | |   |
   |+------------+|  | +-------g1_s21----+  | |    +----g1_s32-----+ | |   |
   +-+------------+  | | +--g1_s211-----+|  | |    |  +-g1_s321--+ | | |   |
     |               | | |+-g1_s2111+   ||  | |    |  |          | | | |   |
     |               | | ||         |   ||  | |    |  |          | | | |   |
     |               | | ||         |   ||  | |    |  |          | | | |   |
     |               | | ||         |   ||  | |    |  |          | | | |   |
     |               | | ||         |   |+-------b---->          <----f----+
     |               | | ||         |   ||  | |    |  |          | | | |   |
     |               | | ||         |   ||  | |    |  |          | | | |   |
     +----------f--------->         |   ||  | |  +---->          | | | |   |
                     | | ||         |   ||  | |  | |  |          | | | |   |
                     | | |++--------+   ||  | |  | |  |          | | | +-d->
                     | | +-|------------+|  | |  | |  +----------+ | | |   |
                     | +---|-------------+  | |  | +---------------+ | |   |
                     |     |                | +--|-------------------+ |   |
                     |     +------------a--------+                     |   |
                     |                      +--------------------------+   |
                     |                                                     |
                     +-----------------------------------------------------+


This is used for testing the type E topology in the trans_ method of the HsmEventProcessor
class.
  * test_hsm_next_rtc - start in active_objects_graph_g1_s22
'''


@spy_on
def g1_s0_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.F):
    status = chart.trans(g1_s2111_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


@spy_on
def g1_s01_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.post_fifo(Event(signal=signals.A))
    chart.post_lifo(Event(signal=signals.F))
    chart.recall()
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    status = chart.trans(g1_s22_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s0_active_objects_graph
  return status


@spy_on
def g1_s1_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    chart.post_fifo(Event(signal=signals.E))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.F):
    status = chart.trans(g1_s321_active_objects_graph)
  elif(e.signal == signals.E):
    status = chart.trans(g1_s01_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


@spy_on
def g1_s21_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(g1_s321_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s1_active_objects_graph
  return status


@spy_on
def g1_s211_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s21_active_objects_graph
  return status


@spy_on
def g1_s2111_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(g1_s321_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s211_active_objects_graph
  return status


@spy_on
def g1_s22_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.post_fifo(Event(signal=signals.D))
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.D):
    status = chart.trans(g1_s1_active_objects_graph)
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s1_active_objects_graph
  return status


@spy_on
def g1_s3_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.defer(Event(signal=signals.F))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s22_active_objects_graph
  return status


@spy_on
def g1_s32_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s3_active_objects_graph
  return status


@spy_on
def g1_s321_active_objects_graph(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, g1_s32_active_objects_graph
  return status


@pytest.fixture
def fabric_fixture(request):
  yield
  # shut down the active fabric for the next test
  ActiveFabric().stop()
  ActiveFabric().clear()


@pytest.mark.ao
def test_import(fabric_fixture):
  ao = ActiveObject()
  assert(ao is not None)


@pytest.mark.ao
def test_start_stop(fabric_fixture):
  ao = ActiveObject(name="bob")
  ao.start_at(g1_s22_active_objects_graph)
  assert(ao.thread.is_alive() is True)
  time.sleep(0.2)
  ao.stop()
  assert(ao.spy_full() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s22_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'ENTRY_SIGNAL:g1_s1_active_objects_graph',
     'ENTRY_SIGNAL:g1_s22_active_objects_graph',
     'INIT_SIGNAL:g1_s22_active_objects_graph',
     'POST_FIFO:D',
     '<- Queued:(1) Deferred:(0)',
     'D:g1_s22_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s22_active_objects_graph',
     'EXIT_SIGNAL:g1_s22_active_objects_graph',
     'INIT_SIGNAL:g1_s1_active_objects_graph',
     'POST_FIFO:E',
     '<- Queued:(1) Deferred:(0)',
     'E:g1_s1_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s01_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s0_active_objects_graph',
     'EXIT_SIGNAL:g1_s1_active_objects_graph',
     'ENTRY_SIGNAL:g1_s0_active_objects_graph',
     'ENTRY_SIGNAL:g1_s01_active_objects_graph',
     'POST_FIFO:A',
     'POST_LIFO:F',
     'INIT_SIGNAL:g1_s01_active_objects_graph',
     '<- Queued:(2) Deferred:(0)',
     'F:g1_s01_active_objects_graph',
     'F:g1_s0_active_objects_graph',
     'EXIT_SIGNAL:g1_s01_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s01_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s2111_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s0_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s211_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s21_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'EXIT_SIGNAL:g1_s0_active_objects_graph',
     'ENTRY_SIGNAL:g1_s1_active_objects_graph',
     'ENTRY_SIGNAL:g1_s21_active_objects_graph',
     'ENTRY_SIGNAL:g1_s211_active_objects_graph',
     'ENTRY_SIGNAL:g1_s2111_active_objects_graph',
     'INIT_SIGNAL:g1_s2111_active_objects_graph',
     '<- Queued:(1) Deferred:(0)',
     'A:g1_s2111_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s321_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s2111_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s32_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s3_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s22_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s1_active_objects_graph',
     'EXIT_SIGNAL:g1_s2111_active_objects_graph',
     'EXIT_SIGNAL:g1_s211_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s211_active_objects_graph',
     'EXIT_SIGNAL:g1_s21_active_objects_graph',
     'SEARCH_FOR_SUPER_SIGNAL:g1_s21_active_objects_graph',
     'ENTRY_SIGNAL:g1_s22_active_objects_graph',
     'ENTRY_SIGNAL:g1_s3_active_objects_graph',
     'ENTRY_SIGNAL:g1_s32_active_objects_graph',
     'ENTRY_SIGNAL:g1_s321_active_objects_graph',
     'INIT_SIGNAL:g1_s321_active_objects_graph',
     '<- Queued:(0) Deferred:(0)',
     'stop_active_object:g1_s321_active_objects_graph',
     'stop_active_object:g1_s32_active_objects_graph',
     'stop_active_object:g1_s3_active_objects_graph',
     'stop_active_object:g1_s22_active_objects_graph',
     'stop_active_object:g1_s1_active_objects_graph',
     '<- Queued:(0) Deferred:(0)'])
  ao.clear_spy()
  assert(ao.spy_full() == [])


@spy_on
def posted_event_snitch(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    chart.augment(other=0, name='a_signal')
    chart.augment(other=0, name='b_signal')
    chart.augment(other=0, name='f_signal')
    chart.augment(other=0, name='g_signal')
    status = return_status.HANDLED

  elif(e.signal == signals.EXIT_SIGNAL):
    del(chart.a_signal)
    del(chart.b_signal)
    del(chart.f_signal)
    del(chart.g_signal)
    status = return_status.HANDLED

  # set up a hook for testing
  elif(e.signal == signals.A):
    chart.a_signal += 1
    status = return_status.HANDLED

  # set up a hook for testing
  elif(e.signal == signals.B):
    chart.b_signal += 1
    status = return_status.HANDLED

  # set up a hook for testing
  elif(e.signal == signals.F):
    chart.f_signal += 1
    status = return_status.HANDLED

  # set up a hook for testing
  elif(e.signal == signals.G):
    chart.g_signal += 1
    status = return_status.HANDLED

  else:
    status, chart.temp.fun = return_status.SUPER, chart.top

  return status


@pytest.mark.ao
@pytest.mark.post_event
def test_that_it_can_post_events(fabric_fixture):
  '''inspect with your eyes'''
  ao = ActiveObject()
  ao.start_at(posted_event_snitch)
  assert(ao.thread.is_alive() is True)
  ao.post_lifo(
      Event(signal=signals.F),
      times=5,
      period=0.1,
      deferred=False,
  )
  time.sleep(1)
  assert(ao.spy_full() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:posted_event_snitch',
     'ENTRY_SIGNAL:posted_event_snitch',
     'INIT_SIGNAL:posted_event_snitch',
     '<- Queued:(0) Deferred:(0)',
     'F:posted_event_snitch:HOOK',
     '<- Queued:(0) Deferred:(0)',
     'F:posted_event_snitch:HOOK',
     '<- Queued:(0) Deferred:(0)',
     'F:posted_event_snitch:HOOK',
     '<- Queued:(0) Deferred:(0)',
     'F:posted_event_snitch:HOOK',
     '<- Queued:(0) Deferred:(0)',
     'F:posted_event_snitch:HOOK',
     '<- Queued:(0) Deferred:(0)']
  )
  assert(ao.f_signal == 5)


@pytest.mark.ao
@pytest.mark.post_event
def test_that_it_defer(fabric_fixture):
  '''inspect with your eyes'''
  ao = ActiveObject()
  ao.start_at(posted_event_snitch)
  assert(ao.thread.is_alive() is True)
  ao.post_lifo(Event(signal=signals.F),
                     times=1,
                     period=3.0,
                     deferred=True,
               )

  time.sleep(0.2)
  assert(ao.spy_full() ==
    ['START',
     'SEARCH_FOR_SUPER_SIGNAL:posted_event_snitch',
     'ENTRY_SIGNAL:posted_event_snitch',
     'INIT_SIGNAL:posted_event_snitch',
      '<- Queued:(0) Deferred:(0)']
  )
  assert(ao.f_signal == 0)


@pytest.mark.ao
@pytest.mark.post_event
def test_you_can_post_the_same_signal_over_and_over(fabric_fixture):
  ao = ActiveObject()
  ao.start_at(posted_event_snitch)
  ao.post_fifo(Event(signal=signals.F),
      times=1,
      period=0.1)
  ao.post_lifo(Event(signal=signals.F),
      times=1,
      period=0.1)
  time.sleep(0.3)
  assert(ao.f_signal == 2)


@pytest.mark.ao
@pytest.mark.post_event
@pytest.mark.this
def test_you_can_cancel_an_event_thread(fabric_fixture):
  ao = ActiveObject()
  ao.start_at(posted_event_snitch)
  print("")
  # run 2 times fast
  thread_id_a = ao.post_fifo(Event(signal=signals.A),
      deferred=False,
      times=20,
      period=0.1)

  # run forever with a period of 1 second
  thread_id_f = ao.post_fifo(Event(signal=signals.F),
      deferred=True,
      times=10,
      period=1.0)

  # run forever with a period of 1 second
  thread_id_g = ao.post_fifo(Event(signal=signals.G),
      deferred=True,
      period=1.0)

  # run 2 times fast
  thread_id_b = ao.post_fifo(Event(signal=signals.B),
      deferred=False,
      times=200,
      period=0.1)

  pp(ao.posted_events_queue)
  assert(len(ao.posted_events_queue) == 4)
  ao.cancel_event(thread_id_f)
  time.sleep(0.2)
  pp(ao.posted_events_queue)
  assert(len(ao.posted_events_queue) == 3)
  time.sleep(0.5)
  ao.cancel_event(thread_id_g)
  ao.cancel_event(thread_id_a)
  assert(len(ao.posted_events_queue) == 1)
  ao.cancel_event(thread_id_b)
  assert(len(ao.posted_events_queue) == 0)
  # demonstrate the the f signal was cancelled before it ran
  assert(ao.f_signal == 0)
  # demonstrate the the g signal was cancelled before it ran
  assert(ao.g_signal == 0)
  # demonstrate that a and b did run
  assert(ao.a_signal >= 1)
  assert(ao.b_signal >= 1)


@pytest.mark.ao
@pytest.mark.post_event
def test_you_can_cancel_all_events_of_the_same_name(fabric_fixture):
  ao = ActiveObject()
  ao.start_at(posted_event_snitch)

  # run 2 times fast
  thread_id_a = ao.post_fifo(Event(signal=signals.A),
      deferred=True,
      times=200,
      period=0.3)
  assert(thread_id_a is not None)
  # run forever with a period of 1 second
  thread_id_f = ao.post_lifo(Event(signal=signals.A),
      deferred=True,
      times=200,
      period=0.3)

  # run forever with a period of 1 second
  thread_id_f = ao.post_fifo(Event(signal=signals.A),
      deferred=False,
      times=200,
      period=0.3)
  assert(thread_id_f is not None)

  # run forever with a period of 1 second
  thread_id_g = ao.post_lifo(Event(signal=signals.G),
      deferred=True,
      period=1.0)
  assert(thread_id_g is not None)

  # run 2 times fast
  thread_id_b = ao.post_fifo(Event(signal=signals.B),
      deferred=False,
      times=200,
      period=0.1)
  assert(thread_id_b is not None)

  assert(len(ao.posted_events_queue) == 5)
  ao.cancel_events(Event(signal=signals.A))
  assert(len(ao.posted_events_queue) == 2)
  time.sleep(0.1)
  assert(ao.a_signal == 1)


@pytest.mark.ao
@pytest.mark.post_event
def test_posting_too_many_events_will_raise_exception(fabric_fixture):
  ao = ActiveObject()
  ao.start_at(posted_event_snitch)
  with pytest.raises(ActiveObjectOutOfPostedEventResources) as execinfo:
    assert(execinfo is not None)
    for i in range(1000):
      ao.post_fifo(Event(signal=signals.A),
          times=300,
          period=0.1)
  time.sleep(0.2)
  # we issue an exception, but we still run as well as we can
  # the existing threads will work
  assert(len(ao.posted_events_queue) is ao.__class__.QUEUE_SIZE)
  assert(ao.a_signal > 0)
  ao.cancel_events(Event(signal=signals.A))
  assert(len(ao.posted_events_queue) is 0)
