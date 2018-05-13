import pytest
from miros import signals, Event
from miros.activeobject import ActiveFabric
from collections import deque
import time
import pprint


def pp(item):
  pprint.pprint(item)

@pytest.mark.pubsub
def test_active_fabric_singleton():
  af1 = ActiveFabric()
  af2 = ActiveFabric()
  assert(id(af1) == id(af2))


# Confirm that we can start and stop the active fabric, otherwise we can't test
# this system
@pytest.mark.pubsub
def test_turn_off_and_on_fabric():
  af1 = ActiveFabric()
  af1.start()
  assert(af1.fifo_thread.is_alive() is True)
  assert(af1.lifo_thread.is_alive() is True)
  af1.stop()
  assert(af1.fifo_thread.is_alive() is False)
  assert(af1.lifo_thread.is_alive() is False)
  af1.start()
  assert(af1.fifo_thread.is_alive() is True)
  assert(af1.lifo_thread.is_alive() is True)
  af1.stop()
  assert(af1.fifo_thread.is_alive() is False)
  assert(af1.lifo_thread.is_alive() is False)


# Confirm that we can clear the active fabric, otherwise we can't test the
# system
@pytest.mark.pubsub
def test_clear_feature():
  af1 = ActiveFabric()
  event_a = Event(signal=signals.A)
  event_b = Event(signal=signals.B)
  event_c = Event(signal=signals.C)
  input_queue_1 = deque(maxlen=5)
  af1.subscribe(input_queue_1, event_a)
  af1.subscribe(input_queue_1, event_b)
  af1.subscribe(input_queue_1, event_a)
  af1.subscribe(input_queue_1, event_b)
  af1.subscribe(input_queue_1, event_c)
  af1.subscribe(input_queue_1, event_c)
  af1.start()
  af1.stop()
  af1.clear()
  assert(af1.fifo_fabric_queue.empty() is True)
  assert(af1.lifo_fabric_queue.empty() is True)
  assert(af1.lifo_subscriptions == {})
  assert(af1.fifo_subscriptions == {})


@pytest.mark.pubsub
def test_simple_publish_subscribe(fabric_fixture):
  input_queue_1 = deque(maxlen=5)
  event_a       = Event(signal=signals.A)
  af            = ActiveFabric()

  af.subscribe(input_queue_1, event_a)
  af.start()
  af.publish(event_a)
  time.sleep(0.10)

  assert(len(input_queue_1) == 1)


@pytest.mark.pubsub
def test_multi_subscribe(fabric_fixture):
  input_queue_1 = deque(maxlen=5)
  input_queue_2 = deque(maxlen=5)
  event_a = Event(signal=signals.A)

  # set two different queues to subscribe to one event
  af = ActiveFabric()
  af.subscribe(input_queue_1, event_a)
  af.subscribe(input_queue_2, event_a)

  af.start()
  af.publish(event_a)
  time.sleep(0.10)
  assert(len(input_queue_1) == 1)
  assert(len(input_queue_2) == 1)


@pytest.mark.pubsub
def test_repeat_publish_subscribe(fabric_fixture):
  input_queue_1 = deque(maxlen=5)
  event_a = Event(signal=signals.A)

  af = ActiveFabric()
  af.subscribe(input_queue_1, event_a)
  af.subscribe(input_queue_1, event_a)

  # If you subscribe twice using the same queue with the same event signal_name
  # then we should.
  af.start()
  af.publish(event_a)
  time.sleep(0.10)
  assert(len(input_queue_1) == 1)


@pytest.mark.pubsub
def test_subscribe_lilo(fabric_fixture):
  input_queue_1 = deque(maxlen=5)
  event_a       = Event(signal=signals.A)
  event_b       = Event(signal=signals.B)
  input_queue_1.append(event_b)
  af = ActiveFabric()
  af.subscribe(input_queue_1, event_a, queue_type='lifo')
  af.subscribe(input_queue_1, event_b, queue_type='lifo')
  af.start()
  af.publish(event_a)
  time.sleep(0.11)
  assert(len(input_queue_1) == 2)
  popped_event = input_queue_1.pop()
  assert(popped_event.signal_name == 'A')
  assert(len(input_queue_1) == 1)
  popped_event = input_queue_1.pop()
  assert(popped_event.signal_name == 'B')
  af.publish(event_a)
  af.publish(event_b)
  time.sleep(0.11)
  popped_event = input_queue_1.pop()
  assert(popped_event.signal_name == 'B')
  assert(len(input_queue_1) == 1)
  popped_event = input_queue_1.pop()
  assert(popped_event.signal_name == 'A')
  assert(len(input_queue_1) == 0)
