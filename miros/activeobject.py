from miros.event import ReturnStatus, signals, Event, return_status, Signal
from miros.hsm   import Hsm, HsmTopologyException, spy_on, spy_tuple
from miros.singletlon import SingletonDecorator
import time

Signal().append("stop_fabric")
from threading import Event as ThreadEventLib
from threading import Thread
from queue import PriorityQueue

processing_on_event_flag = ThreadEventLib()
processing_on_event_flag.set()

class SourceEvent(ThreadEventLib):
  pass

ThreadEvent = SingletonDecorator(SourceEvent)

class FabricEvent():
  def __init__(self,event, priority):
    self.priority = priority
    self.event    = event

  def __lt__(self, other):
    return self.priority < other.priority

  def __eq__(self, other):
    return self.priority == other.priority


class ActiveFabricSource():
  '''A task and a lifo and fifo queue which clients and subscribe and publish to

  The task managed by this class can be started and stopped (very useful for
  testing)  It does this by NOT inheriting from the threading class, instead it
  uses the more primative approach of keeping an internal object that is a thread
  which can be killed.
  '''

  def __init__(self):
    super().__init__()
    self.fifo_fabric_queue  = PriorityQueue()
    self.lifo_fabric_queue  = PriorityQueue()
    self.fifo_subscriptions = {}
    self.lifo_subscriptions = {}
    self.task_off_event     = ThreadEvent()
    self.fifo_thread        = None
    self.lifo_thread        = None
    self.stop_event         = Event(signal=signals.stop_fabric)

  def start(self):
    '''start up the thread which manages the queues and subscription registry.'''
    self.task_off_event = ThreadEvent()

    def initiate_thread(thread_obj, name, thread_runner, queue, subscriptions):
      if thread_obj is None or thread_obj.is_alive() is not True:
        self.task_off_event.set()
        thread_obj = Thread(target = thread_runner,
                                     args=(self.task_off_event,
                                     queue,
                                     subscriptions))
        thread_obj.name   = name
        thread_obj.daemon = True
        thread_obj.start()
        # crash right away if it didn't work
        assert(thread_obj.is_alive() == True)
        return thread_obj

    self.fifo_thread = \
      initiate_thread( thread_obj     = self.fifo_thread,
                       name           = "fifo active fabric",
                       thread_runner  = self._thread_runner_fifo,
                       queue          = self.fifo_fabric_queue,
                       subscriptions  = self.fifo_subscriptions)

    self.lifo_thread = \
      initiate_thread( thread_obj     = self.lifo_thread,
                       name           = "lifo active fabric",
                       thread_runner  = self._thread_runner_lifo,
                       queue          = self.lifo_fabric_queue,
                       subscriptions  = self.lifo_subscriptions)

  def stop(self):
    '''stop the the thread, but in such a way that it can be restarted'''
    task_off_event = ThreadEvent()
    task_off_event.clear()

    if self.fifo_thread != None:
      if self.fifo_thread.is_alive() is True:
        # this should kill the fifo thread
        fifo_stop_fe = FabricEvent(Event(signal=signals.stop_fabric),priority=1)
        self.fifo_fabric_queue.put(fifo_stop_fe)
        self.fifo_thread.join()

    if self.lifo_thread != None:
      if self.lifo_thread.is_alive() is True:
        # this should kill lifo thread
        lifo_stop_fe = FabricEvent(Event(signal=signals.stop_fabric),priority=1)
        self.lifo_fabric_queue.put(lifo_stop_fe)
        self.lifo_thread.join()


  def _thread_runner_fifo(self,
                     task_off_event, 
                     fifo_queue,
                     fifo_subscriptions):
    '''if this was a thread class this function would be called "run"

    This is the main execution code of the thread.  It watches to see if the
    Event() singleton has been cleared, if it has it exits its forever loop.

    '''
    fifo_item = None
    while task_off_event.is_set():

      if fifo_queue.qsize() != 0:
        fifo_item = fifo_queue.get()

      if fifo_item is not None:
        event = fifo_item.event
        if event.signal_name in fifo_subscriptions.keys():
          for q in fifo_subscriptions[event.signal_name]:
            # Post the inner event from your FabricEvent object.
            q.append(fifo_item.event)

      fifo_item = None

  def _thread_runner_lifo(self,
                     task_off_event, 
                     lifo_queue,
                     lifo_subscriptions):
    '''if this was a thread class this function would be called "run"

    This is the main execution code of the thread.  It watches to see if the
    Event() singleton has been cleared, if it has it exits its forever loop.

    '''
    lifo_item = None
    while task_off_event.is_set():

      if lifo_queue.qsize() != 0:
        lifo_item = lifo_queue.get()

      if lifo_item is not None:
        event = lifo_item.event
        if event.signal_name in lifo_subscriptions.keys():
          for q in lifo_subscriptions[event.signal_name]:
            # Post the inner event from your FabricEvent object.
            q.append(lifo_item.event)

      lifo_item = None

  def subscribe(self,queue,event,queue_type='fifo'):
    '''subscribe a queue to an event'''

    def _subscribe(internal_queue,event):
      if event.signal_name in internal_queue:
        registry = internal_queue[event.signal_name]
        # make a list of queue ids in queue_ids
        queue_ids = map(lambda x: id(x), registry)
        if id(queue) in queue_ids:
          q_index           = registry.index(queue)
          registry[q_index] = queue
        else:
          registry.append(queue)
      else:
        internal_queue[event.signal_name] = [queue]

    if queue_type is 'lifo':
      _subscribe(self.lifo_subscriptions,event)
    else:
      _subscribe(self.fifo_subscriptions,event)

  def publish(self, event, priority=10):
    '''publish an event to all subscribed queues'''
    fefifo = FabricEvent(event,priority)
    self.lifo_fabric_queue.put(fefifo)
    felifo = FabricEvent(event,priority)
    self.fifo_fabric_queue.put(felifo)

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

class ActiveObject(Hsm):
  pass
#class ActiveObject(Hsm, ActiveThread):
#
#  def __init__(self,instrumented=True,name=None):
#    ActiveThread().__init__(self)
#    Hsm().__init__(self,instrumented)
#
#    self.fabric = ActiveFabric()
#    if self.fabric.is_alive() is False:
#      self.fabric.start()
#
#  def start(self):
#    '''start up the thread which manages the queues and subscription registry.'''
#    if self.started is not True:
#      task_off_event = ThreadEvent()
#      task_off_event.set()
#      self.thread = Thread(target=self._thread_runner,
#                           args=(task_off_event,
#                                 self.lifo_fabric_queue, 
#                                 self.fifo_fabric_queue,
#                                 self.lifo_subscriptions,
#                                 self.fifo_subscriptions))
#      if self.name != None:
#        self.thread.name == self.name
#      self.thread.start()
#
#  def _thread_runner(self, task_off_event, fifo_queue, lifo_queue):
#    task_off_event = ThreadEvent()
#    while(task_off_event.is_set()):
#      self.next_rtc()
#
#  def subscribe_lifo(self, event):
#    pass
#    #self.fabric.subscription(self.lifo_event,

  ## This about this: # wrap it
  ## This about this def p: # wraost_fifo(self,e):
  ## This about this  supe: # wrar().post_fifo(self,e)

  ## This about this # wra: # wrap it
  ## This about this def p: # wraost_lifo(self,e):
  ## This about this  supe: # wrar().post_lifo(self,e)

