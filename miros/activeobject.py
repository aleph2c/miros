# from standard library
from threading   import Event as ThreadEventLib
from threading   import Thread
from queue       import PriorityQueue, Queue
from collections import deque
import time

# from this package
from miros.event import ReturnStatus, signals, return_status, Signal
from miros.event import Event as HsmEvent
from miros.hsm   import Hsm, HsmTopologyException, spy_on, spy_tuple
from miros.singletlon import SingletonDecorator


# Add to different signals to signal if they aren't there already
Signal().append("stop_fabric")
Signal().append("stop_active_object")

class SourceThreadEvent(ThreadEventLib):
  pass
ThreadEvent = SingletonDecorator(SourceThreadEvent)

class FabricEvent():
  def __init__(self, event, priority):
    self.priority = priority
    self.event    = event

  def __lt__(self, other):
    return self.priority < other.priority

  def __eq__(self, other):
    return self.priority == other.priority

class ActiveFabricSource():
  '''A (pub-sub) event dispatcher for active objects.

  To create it:
    af = ActiveFabric()  # it is a singleton

  To subscrbe (do this before starting it):
    client_deque = deque(maxlen=10)
    event_a      = HsmEvent(signal=signals.A)
    af.subscribe(client_deque, event_a, queue_type='fifo')

  To publish with priority:
    event_a = HsmEvent(signal=signals.A)
    af.publish(event_a, priority=1) # where 1 has the highest priorty
                                    # by default the priorty is set to 1000

  To be greedy, and ensure your messages take priority over everything, publish
  with a very high priority and subscribe using the lifo technique:
    client_deque = deque(maxlen=10)
    event_a      = HsmEvent(signal=signals.A)

    # By subscribing with the 'lifo' technique, any publishing event that this
    # deque item cares about will be placed at the front of the queue
    af.subscribe(client_deque, event_a, queue_type='lifo')

    # By publishing with a priority 1, the supporting tasks checking the active
    # fabric will ignore all queue items of lower priority and dispatch this
    # event first.
    af.publish(event_a, priority=1)

  Typically the active fabric is started by the first active object that is
  started.  The active fabric is a singleton, so that all active objects can
  communicate with each other by communicating to it.

  The tasks managed by this class can be started and stopped (needed for
  testing)  It does this by NOT inheriting from the threading class, instead it
  uses the a more primative approach of keeping an internal object that is a thread
  which can be killed and restarted.
  '''

  def __init__(self):
    super().__init__()

    # This is used to end the tasks forever loops
    self.task_off_event     = ThreadEvent()

    # Set up two priority queues one for the fifo and one for the lifo
    self.fifo_fabric_queue  = PriorityQueue()
    self.lifo_fabric_queue  = PriorityQueue()

    # There are two different subscription registries
    self.fifo_subscriptions = {}
    self.lifo_subscriptions = {}

    # Two different threads which will pend on items in their respective
    # priority queues
    self.fifo_thread        = None
    self.lifo_thread        = None

  def start(self):
    '''start up the threads which manage the queues and subscription registry.'''

    # Get the ThreadEvent (singleton), set it so that the threads will try and
    # run forever
    self.task_off_event = ThreadEvent()
    self.task_off_event.set()

    # Initiate a thread and return it so that this object can reference it later
    def initiate_thread(thread_obj, name, thread_runner, queue, subscriptions):
      if thread_obj is None or thread_obj.is_alive() is not True:
        thread_obj = Thread(target = thread_runner,
                                     args=(self.task_off_event,
                                           queue,
                                           subscriptions))
        thread_obj.name   = name
        thread_obj.daemon = True
        thread_obj.start()
        # if we haven't done what we promised, crash the program
        assert(thread_obj.is_alive() == True)
        return thread_obj

    # Create a thread to wake up on fifo priority queue events
    self.fifo_thread = \
      initiate_thread( thread_obj     = self.fifo_thread,
                       name           = "fifo active fabric",
                       thread_runner  = self.thread_runner_fifo,
                       queue          = self.fifo_fabric_queue,
                       subscriptions  = self.fifo_subscriptions)

    # Create a thread to wake up on lifo priority queue events
    self.lifo_thread = \
      initiate_thread( thread_obj     = self.lifo_thread,
                       name           = "lifo active fabric",
                       thread_runner  = self.thread_runner_lifo,
                       queue          = self.lifo_fabric_queue,
                       subscriptions  = self.lifo_subscriptions)

  def is_alive(self):
    result = True
    if( self.fifo_thread != None and self.lifo_thread != None):
      result &= self.fifo_thread.is_alive()
      result &= self.lifo_thread.is_alive()
    else:
      result &= False
    return result

  def stop(self):
    '''stop the the threads in such a way that it can be restarted again'''

    # Get the ThreadEvent (singleton), clear it so that the threads will try to
    # exit once they wake up.
    task_off_event = ThreadEvent()
    task_off_event.clear()

    # Post an item to the queue to wake up the thread then join on it until it
    # completes its last run and exits
    def stop_thread(thread_obj, queue):
      if thread_obj != None:
        if thread_obj.is_alive() is True:
          stop_fe = FabricEvent(HsmEvent(signal=signals.stop_fabric),priority=1)
          # The tasks are pending on items in their queue, wake them up with a
          # queue item, so that they can see that they need to stop running by
          # looking at their task_off_event thread-event
          queue.put(stop_fe)
          thread_obj.join()

    stop_thread(self.fifo_thread, self.fifo_fabric_queue)
    stop_thread(self.lifo_thread, self.lifo_fabric_queue)

    if self.fifo_thread != None:
      assert(self.fifo_thread.is_alive() == False)
    if self.lifo_thread != None:
      assert(self.lifo_thread.is_alive() == False)

  def thread_runner_fifo(self,
                     task_off_event,
                     fifo_queue,
                     fifo_subscriptions):
    '''If this was a Thread class this function would be called "run"

    This is the main execution code of the thread.  It watches to see if the
    HsmEvent() singleton has been cleared, if it has it exits its forever loop.

    '''
    fifo_item = None
    while task_off_event.is_set():

      # this locks the task, it will only run if something is in the queue
      fifo_item = fifo_queue.get()

      if fifo_item is not None:
        event = fifo_item.event
        if event.signal_name in fifo_subscriptions.keys():
          for q in fifo_subscriptions[event.signal_name]:
            # Post the inner event from your FabricEvent object.
            q.append(fifo_item.event)

      fifo_item = None
      fifo_queue.task_done() # so that join can work

  def thread_runner_lifo(self,
                     task_off_event,
                     lifo_queue,
                     lifo_subscriptions):
    '''If this was a Thread class this function would be called "run"

    This is the main execution code of the thread.  It watches to see if the
    HsmEvent() singleton has been cleared, if it has it exits its forever loop.

    '''
    lifo_item = None
    while task_off_event.is_set():

      # this locks the task, it will only run if something is in the queue
      lifo_item = lifo_queue.get()

      if lifo_item is not None:
        event = lifo_item.event
        if event.signal_name in lifo_subscriptions.keys():
          for q in lifo_subscriptions[event.signal_name]:
            # Post the inner event from your FabricEvent object.
            q.append(lifo_item.event)

      lifo_item = None
      lifo_queue.task_done() # so that join can work

  def subscribe(self,queue,event,queue_type='fifo'):
    '''subscribe a queue to an event in a 'fifo' or 'lifo' way

    There are two different ways to subscribe to an event:
      1) first in first out - fifo priority queue
      2) last in first out  - lifo priority queue

    Both methods 1 and 2 have tasks with associated priority queues.
    The fifo/lifo action only takes place at the momement the managing task puts
    an item into the external queue used as a registry object. For method 1, the
    task puts the event on the last location in the queue.  For method 2, the
    task puts the event at the beginning location of the queue.

    Typically, you would use the same external deque object to subscribe to
    events in the two different ways provided by this method.  This is best
    explained with an example:

    Example (FIFO):
      active_object_input_queue = deque(maxlen=100) # LockingDeque works too
      event_a = HsmEvent(signal=signals.A)
      event_b = HsmEvent(signal=signals.B)

      # To show are fifo in action we first push something on our deque:
      active_object_input_queue.append(event_a)

      # subscribe to b using the fifo technique
      af = ActiveFabric()
      af.subscribe(active_object_input_queue, event_b) # default to fifo
      af.start()
      af.publish(event_b)

      # show that our old item is still there
      assert(active_object_input_queue.pop().signal_name == 'A')
      # our new item was at the end of the list
      assert(active_object_input_queue.pop().signal_name == 'B')

    Example (LIFO):
      active_object_input_queue = deque(maxlen=100) # LockingDeque works too
      event_a = HsmEvent(signal=signals.A)
      event_b = HsmEvent(signal=signals.B)

      # To show are lifo in action push something onto our deque:
      active_object_input_queue.append(event_a)

      # subscribe to b using the lifo technique
      af = ActiveFabric()
      af.subscribe(active_object_input_queue, event_b, queue_type='lifo')
      af.start()
      af.publish(event_b)

      # show that the 'lifo' technique barged our event into the front of the list
      assert(active_object_input_queue.pop().signal_name == 'B')
      # our old event is still there
      assert(active_object_input_queue.pop().signal_name == 'A')

    '''
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

  def publish(self, event, priority=1000):
    '''publish an event with a given priority to all subscribed queues

    Priority of 1 is the highest priority
    '''
    fefifo = FabricEvent(event,priority)
    self.lifo_fabric_queue.put(fefifo)
    felifo = FabricEvent(event,priority)
    self.fifo_fabric_queue.put(felifo)

  def clear(self):
    '''clear out all subscriptions and queues'''
    self.fifo_fabric_queue = PriorityQueue()
    self.lifo_fabric_queue = PriorityQueue()
    self.fifo_subscriptions = {}
    self.lifo_subscriptions = {}

# ActiveFabric is a singleton class
ActiveFabric = SingletonDecorator(ActiveFabricSource)

class LockingDeque():
  '''merge of some deque and Queue object features
  
  This provides the locking interface of the Queue and pop, popleft, append,
  appendleft and clear features of the deque.

  Example:
    import time

    ld = LockingQueue()
    def example_task(ld):
      lq.wait() # => task will stop until an item is appended
      print(lq.pop())

    thread = Thread(target=example_task,args=(ld,))
    thread.start()   # thread started and locked
    time.sleep(10)
    ld.append("bob") # thread prints "bob"
                     # thread finished
    time.sleep(0.1)
    assert(thread.is_alive() == False)
  
  '''

  def __init__(self,*args,**kwargs):
    self.deque         = deque(maxlen=Hsm.QUEUE_SIZE)
    self.locking_queue = Queue(maxsize=Hsm.QUEUE_SIZE)

  def get(self, block=True, timeout=None):
    '''block on the locking queue, popleft from deque'''
    return self.locking_queue.get(block,timeout)

  def wait(self, block=True, timeout=None):
    '''wait for an append/appendleft event'''
    return self.get(block,timeout)

  def popleft(self):
    return self.deque.popleft()

  def pop(self):
    return self.deque.pop()

  def append(self, item):
    if self.locking_queue.full() == False:
      # we don't care about storing items in the locking_queue, our information
      # is in the deque, the locking_queue provides the 'get' unlocking feature
      self.locking_queue.put("ready")
      self.deque.append(item)
    else:
      self.deque.rotate(1)
      self.deque.append(item)

    if self.locking_queue.qsize() < len(self.deque):
      while self.locking_queue.qsize() != len(self.deque):
        self.locking_queue.put("ready")

  def appendleft(self,item):
    if self.locking_queue.full() == False:
      # we don't care about storing items in the locking_queue, our information
      # is in the deque, the locking_queue provides the 'get' locking feature
      self.locking_queue.put("ready")
      self.deque.appendleft(item)

    if self.locking_queue.qsize() < len(self.deque):
      while self.locking_queue.qsize() != len(self.deque):
        self.locking_queue.put("ready")

  def clear(self):
    self.deque.clear()
    try:
      while(True):
        self.locking_queue.get_nowait()
    except:
      self.locking_queue.task_done()

  def task_done(self):
    self.locking_queue.task_done() # so that join can work

  def qsize(self):
    return self.locking_queue.qsize()

  def __len__(self):
    return len(self.deque)

  def len(self):
    return len(self.deque)

class ActiveObject(Hsm):
  def __init__(self,instrumented=True,name=None):
    super().__init__(instrumented)
    self.locking_deque = LockingDeque()
    # Over-write the deque in the Hsm with Queues with the one managed by the
    # LockingDeque object. This is the 'magic' in this object.  Any time a
    # post_fifo or post_lifo method within the Hsm is touched, it unknowingly uses
    # the LockingDeque object; which will also provide the 'get' method feature.
    # This 'get' method will allow our active object task to sleep until there
    # is something to do.  To understand this object, you need to grok this.
    self.queue = self.locking_deque

    # The active fabric is a singletlon that dispatches messages between all
    # active objects.  It provides a publish/subscribe infrasture, and it will
    # post directly into our locking_deque object, and as a result, provide the
    # 'get' method of this object to unlock our task.
    self.fabric = ActiveFabric()
    self.thread = None
    self.name   = name

  def __thread_running(self):
    if self.thread is None:
      result = False
    else:
      result = True if self.thread_is_alive() else False
    return result

  def start_thread_if_not_running(fn):
    def _start_thread_if_not_running(self,*args,**kwargs):
      if self.__thread_running == False:
        self.__start()
      fn(self,*args,**kwargs)
    return _start_thread_if_not_running

  @start_thread_if_not_running
  def subscribe(self,event,queue_type='fifo'):
    self.fabric.subscription(self.queue, event, queue_type)

  @start_thread_if_not_running
  def publish(self, event, priority):
    self.fabric.publish(event,priority)

  @start_thread_if_not_running
  def post_fifo(self,e):
    super().post_fifo(e)

  @start_thread_if_not_running
  def post_lifo(self,e):
    super().post_lifo(e)

  def start_at(self, initial_state):
    super().start_at(initial_state)
    self.__start()

  def __start(self):
    # Get the ThreadEvent (singleton), set it so that the threads will try and
    # run forever
    task_off_event = ThreadEvent()
    task_off_event.set()

    # If the active fabric is not running, turn it on so that all of our active
    # objects can talk to each other.
    if self.fabric.is_alive() is False:
      self.fabric.start()

    def start_thread(self):
      thread        = Thread(target = self.run_event, args=(task_off_event,self.queue))
      thread.name   = self.name
      thread.daemon = True
      thread.start()
      return thread

    if self.__thread_running() == False:
      self.thread = start_thread(self)

    # crash if we can't start our thread
    assert(self.thread.is_alive())

  def stop(self,stop_fabric=False):
    task_off_event = ThreadEvent()
    task_off_event.clear()
    self.queue.append(HsmEvent(signal=signals.stop_active_object))
    self.thread.join()
    if stop_fabric:
      self.fabric.stop()

  def run_event(self, task_off_event, queue):
    ready = None
    while task_off_event.is_set():
      queue.wait()      # wait for an event we have subcribed to
      if self.queue.deque[0].signal_name != signals.stop_active_object:
        self.next_rtc()
      queue.task_done() # write this so that 'join' will work

