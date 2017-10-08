from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import Hsm, HsmTopologyException, spy_on, spy_tuple
from miros.singletlon import SingletonDecorator
import time

from threading import Event, Thread
from queue import PriorityQueue

processing_on_event_flag = Event()
processing_on_event_flag.set()

class SourceEvent(Event):
  pass

Event = SingletonDecorator(SourceEvent)

class FabricEvent():
  def __init__(self,event, priority):
    self.priority = priority
    self.event    = event

  def __lt__(self, other):
    return self.priority < other.priority

  def __eq__(self, other):
    return self.priority == other.priority


class ActiveThread:
  def __init__(self):
    self.started = False
    self.thread  = None

  def start(self):
    '''start up the thread which manages the queues and subscription registry.'''
    if self.started is not True:
      task_off_event = Event()
      task_off_event.set()
      self.thread = Thread(target=self._thread_runner, args=(task_off_event,))
      self.thread.start()

  def stop(self):
    '''stop the the thread, but in such a way that it can be restarted'''
    if self.started is not True:
      task_off_event = Event()
      task_off_event.clear()
      self.thread.join()
      self.started = False

  def kill(self):
    '''alias of the "stop" thread method'''
    self.stop()

  def is_alive(self):
    return self.task.is_alive()

  def _thread_runner(self, task_off_event, fifo_queue, lifo_queue):
    raise("you need to define this")

class ActiveFabricSource(ActiveThread):
  '''A task and a lifo and fifo queue which clients and subscribe and publish to

  The task managed by this class can be started and stopped (very useful for
  testing)  It does this by NOT inheriting from the threading class, instead it
  uses the more primative approach of keeping an internal object that is a thread
  which can be killed.
  '''

  def __init__(self):
    super().__init__()
    self.fifo_fabric_queue = PriorityQueue()
    self.lifo_fabric_queue = PriorityQueue()
    self.fifo_subscriptions = {}
    self.lifo_subscriptions = {}
    self.task_off_event     = Event()

  def start(self):
    '''start up the thread which manages the queues and subscription registry.'''
    self.task_off_event = Event()
    if self.started is not True:
      self.task_off_event.set()
      self.thread = Thread(target=self._thread_runner,
                           args=(self.task_off_event, self.lifo_fabric_queue, self.fifo_fabric_queue,))
      self.thread.name   = "active_fabric"
      self.thread.daemon = True # when the main thread dies so should this one
      self.thread.start()

  def stop(self):
    '''stop the the thread, but in such a way that it can be restarted'''
    print("stop {}".format(id(self.task_off_event)))
    self.task_off_event.clear()
    if self.started is not True:
      self.task_off_event.clear()
      self.thread.join()
      self.started = False

  def _thread_runner(self, task_off_event, fifo_queue, lifo_queue):
    '''if this was a thread class this function would be called "run"

    This is the main execution code of the thread.  It watches to see if the
    Event() singleton has been cleared, if it has it exits its forever loop.

    '''
    lilo_item, fifo_item = None, None
    i = 0
    while task_off_event.is_set():

      if self.lifo_fabric_queue.qsize() != 0:
        lilo_item = self.lifo_fabric_queue.get(False)
      if self.fifo_fabric_queue.qsize() != 0:
        fifo_item = self.fifo_fabric_queue.get(False)

      if lilo_item is not None:
        event = lilo_item.event
        for lilo_queue in self.lifo_subscriptions[event.signal_name]:
          # Post the inner event from your FabricEvent object.
          # The provided queue is actually just a deque, so we
          # post to the left to provide the lifo functionality.
          lifo_queue.appendleft(lifo_item.event)

      if fifo_item is not None:
        event = fifo_item.event
        for fifo_queue in self.fifo_subscriptions[event.signal_name]:
          # Post the inner event from your FabricEvent object.
          fifo_queue.append(fifo_item.event)

      lilo_item, fifo_item = None, None
      print("run {} {}".format(i, id(self.task_off_event)))
      i += 1

  def subscribe(self,queue,event,type='fifo'):
    '''subscribe a queue to an event'''

    def _subscribe(internal_queue,event):
      if event.signal_name in internal_queue:
        registry = internal_queue[event.signal_name]
        if queue in registry:
          q_index = registry.index(queue)
          registry[q_index] = queue
        else:
          registry.append(queue)
      else:
        internal_queue[event.signal_name] = [queue]

    if type is 'lifo':
      _subscribe(self.lifo_subscriptions,event)
    else:
      _subscribe(self.fifo_subscriptions,event)

  def publish(self,event,priority=10,type='fifo'):
    '''publish an event to all subscribed queues'''

    if type is 'lifo':
      fe = FabricEvent(event,priority)
      self.lifo_fabric_queue.put(fe)
    else:
      fe = FabricEvent(event,priority)
      self.fifo_fabric_queue.put(fe)

  def clear(self):
    '''clear out all subscriptions and queues

    This will mostly be used by testing functions
    '''
    self.fifo_fabric_queue = PriorityQueue()
    self.lifo_fabric_queue = PriorityQueue()
    self.fifo_subscriptions = {}
    self.lifo_subscriptions = {}

# ActiveFabric is a singleton class
ActiveFabric = SingletonDecorator(ActiveFabricSource)

class ActiveObject(Hsm, ActiveThread):

  def __init__(self,instrumented=True,name=None):
    ActiveThread().__init__(self)
    Hsm().__init__(self,instrumented)

    self.fabric = ActiveFabric()
    if self.fabric.is_alive() is False:
      self.fabric.start()

  def start(self):
    '''start up the thread which manages the queues and subscription registry.'''
    if self.started is not True:
      task_off_event = Event()
      task_off_event.set()
      self.thread = Thread(target=self._thread_runner,
                           args=(task_off_event, self.lifo_fabric_queue, self.fifo_fabric_queue,))
      if self.name != None:
        self.thread.name == self.name
      self.thread.start()

  def _thread_runner(self, task_off_event, fifo_queue, lifo_queue):
    task_off_event = Event()
    while(task_off_event.is_set()):
      self.next_rtc()

  def subscribe_lifo(self, event):
    pass
    #self.fabric.subscription(self.lifo_event,

  ## This about this: # wrap it
  ## This about this def p: # wraost_fifo(self,e):
  ## This about this  supe: # wrar().post_fifo(self,e)

  ## This about this # wra: # wrap it
  ## This about this def p: # wraost_lifo(self,e):
  ## This about this  supe: # wrar().post_lifo(self,e)

