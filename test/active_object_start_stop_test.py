import time
import pytest
from miros import Event
from miros import signals
from miros import Factory
from collections import deque
from miros import return_status
from collections import namedtuple

Payload = namedtuple('Payload', ['item'])

class StartStopChart(Factory):

  def __init__(self, name=None, live_trace=None, live_spy=None):

    super().__init__('start_stop_test' if name == None else name)

    self.live_spy = False if live_spy == None else live_spy
    self.live_trace = False if live_trace == None else live_trace
    self.buffer = deque(maxlen=2)

    self.example_state = self.create(state="example_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.example_state_entry). \
      catch(signal=signals.do_some_useful_work,
        handler=self.example_state_do_some_useful_work). \
      to_method()

    self.nest(self.example_state, parent=None)
    self.start_at(self.example_state)

  @staticmethod
  def example_state_entry(ex, e):
    status = return_status.HANDLED
    # we don't use these, we just start them... 
    # the stop method should cancel these events
    ex.post_fifo(
      Event(signal=signals.multi_shot_signal_10_times_1),
      deferred=True,
      period=1.0,
      times=10
      )
    ex.post_fifo(
      Event(signal=signals.multi_shot_signal_10_times_2),
      deferred=True,
      period=1.0,
      times=10
      )
    return status

  @staticmethod
  def example_state_do_some_useful_work(ex, e):
    status = return_status.HANDLED
    ex.buffer.append(e.payload.item)
    return status

  def get_item(self):
    return self.buffer.popleft()

@pytest.mark.stop
def test_that_chart_is_working():
  ssc = StartStopChart('whatever')
  ssc.post_fifo(Event(signal=signals.do_some_useful_work, payload=Payload(item=1)))
  time.sleep(0.1)
  assert(len(ssc.posted_events_queue)==2)
  assert(ssc.get_item() == 1)

@pytest.mark.stop
def test_that_stop_kills_the_active_object_thread():
  ssc = StartStopChart('bob')
  ssc.post_fifo(Event(signal=signals.do_some_useful_work, payload=Payload(item=1)))
  time.sleep(0.1)
  assert(len(ssc.posted_events_queue)==2)
  assert(ssc.get_item() == 1)
  assert(ssc.thread.is_alive() == True)
  ssc.stop()
  time.sleep(0.1)
  ssc.post_fifo(Event(signal=signals.do_some_useful_work, payload=Payload(item=1)))
  time.sleep(0.1)
  with pytest.raises(IndexError):
    ssc.get_item()
  assert(ssc.thread.is_alive() == False)
  assert(len(ssc.posted_events_queue)==0)
  assert(ssc.fabric.is_alive() == True)
    
@pytest.mark.stop
def test_that_stop_cancels_all_multishots():
  ssc = StartStopChart('bob')
  ssc.post_fifo(Event(signal=signals.do_some_useful_work, payload=Payload(item=1)))
  time.sleep(0.1)
  assert(len(ssc.posted_events_queue)==2)
  assert(ssc.get_item() == 1)
  assert(ssc.thread.is_alive() == True)
  ssc.stop()
  time.sleep(0.1)
  assert(len(ssc.posted_events_queue)==0)

@pytest.mark.stop
def test_that_stop_doenst_stop_the_fabric_tasks():
  ssc = StartStopChart('bob')
  ssc.post_fifo(Event(signal=signals.do_some_useful_work, payload=Payload(item=1)))
  time.sleep(0.1)
  assert(len(ssc.posted_events_queue)==2)
  assert(ssc.get_item() == 1)
  assert(ssc.thread.is_alive() == True)
  ssc.stop()
  time.sleep(0.1)
  assert(ssc.fabric.is_alive() == True)

@pytest.mark.stop
def test_that_stopping_the_fabric_stops_the_tasks():
  ssc = StartStopChart('bob')
  ssc.post_fifo(Event(signal=signals.do_some_useful_work, payload=Payload(item=1)))
  time.sleep(0.1)
  assert(len(ssc.posted_events_queue)==2)
  assert(ssc.get_item() == 1)
  assert(ssc.thread.is_alive() == True)
  ssc.fabric.stop()
  # the active object dies after it is woken by an event
  ssc.post_fifo(Event(signal=signals.do_some_useful_work, payload=Payload(item=1)))
  time.sleep(0.1)
  assert(ssc.thread.is_alive() == False)

if __name__ == "__main__":
  print("hey")
  ssc = StartStopChart('whatever')
  ssc.post_fifo(Event(signal=signals.do_some_useful_work, payload=Payload(item=1)))
  assert(ssc.get_item() == 1)
