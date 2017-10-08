import pytest
from miros.event import ReturnStatus, Signal, signals, Event, return_status
from miros.activeobject import ActiveObject, FabricEvent, ActiveFabric, spy_on, HsmTopologyException
from collections import deque
import time
import pprint
def pp(item):
  pprint.pprint(item)

Signal().append("A")
Signal().append("B")
Signal().append("C")
Signal().append("D")
Signal().append("E")
Signal().append("F")
Signal().append("G")

def test_active_fabric_singleton():
  af1 = ActiveFabric()
  af2 = ActiveFabric()
  assert(id(af1)== id(af2)) 

@pytest.mark.pubsub
def test_turn_off_and_on_fabric(): 
  af1 = ActiveFabric()
  af1.start()
  assert(af1.thread.is_alive() == True)
  af1.stop()
  assert(af1.thread.is_alive() == False)
  af1.start()
  assert(af1.thread.is_alive() == True)
  af1.stop()
  assert(af1.thread.is_alive() == False)

@pytest.mark.pubsub
def test_publish_subscribe():
  input_queue_1 = deque(maxlen=5)
  print(id(input_queue_1))
  event_a = Event(signal=signals.A)
  af = ActiveFabric()
  af.subscribe(input_queue_1, event_a)
  af.start()
  af.publish(event_a)
  time.sleep(0.01)
  af.stop()
  assert(len(input_queue_1) == 1)
  assert(input_queue_1.pop().signal_name == 'A')
  #assert(af.fifo_fabric_queue.qsize() == 2)
  #af.start()
  #assert(af.fifo_fabric_queue.qsize() == 0)
  #assert(len(input_queue_1) == 2)
  #assert(len(input_queue_2) == 1)
  af.stop()
#def test_subscribe():
#  af = ActiveFabric()
#  dq = deque(maxlen = 150)
#
#  af.subscribe(queue=dq,event=Event(signal=signals.A),type='fifo')
#  af.subscribe(queue=dq,event=Event(signal=signals.A),type='lifo')
