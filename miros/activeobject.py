# from standard library
import uuid
import time

from collections import deque, namedtuple
from pprint      import pprint
from threading   import Thread
from queue       import PriorityQueue, Queue
from threading   import Event as ThreadEvent
from miros.hsm   import state_method_template
from functools   import wraps

# from this package
from miros.hsm   import HsmWithQueues
from miros.event import signals, Signal
from miros.event import Event as HsmEvent
from miros.singleton import SingletonDecorator


def pp(item):
  pprint(item)


# Add to different signals to signal if they aren't there already
Signal().append("stop_fabric")
Signal().append("stop_active_object")

class SourceThreadEvent(ThreadEvent):
  pass


# The FiberThreadEvent is a singleton.  We want to be able to call
# `FiberThreadEvent()` and get the same ThreadEvent (threading.Event) object in
# many different places in this file.
FiberThreadEvent = SingletonDecorator(SourceThreadEvent)


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

  To subscribe (do this before starting it):
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
    self.fabric_task_event = FiberThreadEvent()

    # Set up two priority queues one for the fifo and one for the lifo
    self.fifo_fabric_queue = PriorityQueue()
    self.lifo_fabric_queue = PriorityQueue()

    # There are two different subscription registries
    self.fifo_subscriptions = {}
    self.lifo_subscriptions = {}

    # Two different threads which will pend on items in their respective
    # priority queues
    self.fifo_thread = None
    self.lifo_thread = None

  def start(self):
    '''start up the threads which manage the queues and subscription registry.'''

    # Get the ThreadEvent (singleton), set it so that the threads will try and
    # run forever
    self.fabric_task_event = FiberThreadEvent()
    self.fabric_task_event.set()

    # Initiate a thread and return it so that this object can reference it later
    def initiate_thread(thread_obj, name, thread_runner, queue, subscriptions):
      if thread_obj is None or thread_obj.is_alive() is not True:
        thread_obj = Thread(target = thread_runner,
                                     args=(self.fabric_task_event,
                                           queue,
                                           subscriptions))
        thread_obj.name   = name
        thread_obj.daemon = True
        thread_obj.start()
        # if we haven't done what we promised, crash the program
        assert(thread_obj.is_alive() is True)
        return thread_obj

    # Create a thread to wake up on fifo priority queue events
    self.fifo_thread = \
      initiate_thread(thread_obj     = self.fifo_thread,
                      name           = "fifo active fabric",
                      thread_runner  = self.thread_runner_fifo,
                      queue          = self.fifo_fabric_queue,
                      subscriptions  = self.fifo_subscriptions)

    # Create a thread to wake up on lifo priority queue events
    self.lifo_thread = \
      initiate_thread(thread_obj     = self.lifo_thread,
                      name           = "lifo active fabric",
                      thread_runner  = self.thread_runner_lifo,
                      queue          = self.lifo_fabric_queue,
                      subscriptions  = self.lifo_subscriptions)

  def is_alive(self):
    result = True
    if(self.fifo_thread is not None and self.lifo_thread is not None):
      result &= self.fifo_thread.is_alive()
      result &= self.lifo_thread.is_alive()
    else:
      result &= False
    return result

  def stop(self):
    '''stop the the threads in such a way that it can be restarted again'''

    # Get the ThreadEvent (singleton), clear it so that the threads will try to
    # exit once they wake up.
    fabric_task_event = FiberThreadEvent()
    fabric_task_event.clear()

    # Post an item to the queue to wake up the thread then join on it until it
    # completes its last run and exits
    def stop_thread(thread_obj, queue):
      if thread_obj is not None:
        if thread_obj.is_alive() is True:
          stop_fe = FabricEvent(HsmEvent(signal=signals.stop_fabric), priority=1)
          # The tasks are pending on items in their queue, wake them up with a
          # queue item, so that they can see that they need to stop running by
          # looking at their fabric_task_event thread-event
          queue.put(stop_fe)
          thread_obj.join()

    stop_thread(self.fifo_thread, self.fifo_fabric_queue)
    stop_thread(self.lifo_thread, self.lifo_fabric_queue)

    if self.fifo_thread is not None:
      assert(self.fifo_thread.is_alive() is False)
    if self.lifo_thread is not None:
      assert(self.lifo_thread.is_alive() is False)

  def thread_runner_fifo(self,
                     fabric_task_event,
                     fifo_queue,
                     fifo_subscriptions):
    '''If this was a Thread class this function would be called "run"

    This is the main execution code of the thread.  It watches to see if the
    HsmEvent() singleton has been cleared, if it has it exits its forever loop.

    '''
    fifo_item = None
    while fabric_task_event.is_set():

      # this locks the task, it will only run if something is in the queue
      fifo_item = fifo_queue.get()

      if fifo_item is not None:
        event = fifo_item.event
        if event.signal_name in fifo_subscriptions.keys():
          for q in fifo_subscriptions[event.signal_name]:
            # Post the inner event from your FabricEvent object.
            q.append(fifo_item.event)

      fifo_item = None
      fifo_queue.task_done()  # so that join can work

  def thread_runner_lifo(self,
                     fabric_task_event,
                     lifo_queue,
                     lifo_subscriptions):
    '''If this was a Thread class this function would be called "run"

    This is the main execution code of the thread.  It watches to see if the
    HsmEvent() singleton has been cleared, if it has it exits its forever loop.

    '''
    lifo_item = None
    while fabric_task_event.is_set():

      # this locks the task, it will only run if something is in the queue
      lifo_item = lifo_queue.get()

      if lifo_item is not None:
        event = lifo_item.event
        if event.signal_name in lifo_subscriptions.keys():
          for q in lifo_subscriptions[event.signal_name]:
            # Post the inner event from your FabricEvent object.
            q.append(lifo_item.event)

      lifo_item = None
      lifo_queue.task_done()  # so that join can work

  def subscribe(self, queue, event_or_signal, queue_type=None):
    '''subscribe a queue to an event in a 'fifo' or 'lifo' way

    There are two different ways to subscribe to an event:
      1) first in first out - fifo priority queue
      2) last in first out  - lifo priority queue

    Both methods 1 and 2 have tasks with associated priority queues.
    The fifo/lifo action only takes place at the moment the managing task puts
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
    def _subscribe(internal_queue, signal):
      if type(signal) == HsmEvent:
        signal_name = signal.signal_name
      elif type(signal) == int:
        signal_name = signals.name_for_signal(signal)

      if signal_name in internal_queue:
        registry = internal_queue[signal_name]
        # make a list of queue ids in queue_ids
        queue_ids = map(lambda x: id(x), registry)
        if id(queue) in queue_ids:
          q_index           = registry.index(queue)
          registry[q_index] = queue
        else:
          registry.append(queue)
      else:
        internal_queue[signal_name] = [queue]
        return signal_name

    if queue_type is None:
      queue_type = 'fifo'

    if queue_type == 'lifo':
      signal_name = _subscribe(self.lifo_subscriptions, event_or_signal)
    else:
      signal_name = _subscribe(self.fifo_subscriptions, event_or_signal)
    return signal_name

  def publish(self, event, priority=None):
    '''publish an event with a given priority to all subscribed queues

    Priority of 1 is the highest priority
    '''
    if priority is None:
      priority = 1000

    fefifo = FabricEvent(event, priority)
    self.lifo_fabric_queue.put(fefifo)
    felifo = FabricEvent(event, priority)
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

    thread = Thread(target=example_task, args=(ld,))
    thread.start()   # thread started and locked
    time.sleep(10)
    ld.append("bob") # thread prints "bob"
                     # thread finished
    time.sleep(0.1)
    assert(thread.is_alive() == False)

  '''

  def __init__(self, *args, **kwargs):
    self.deque         = deque(maxlen=HsmWithQueues.QUEUE_SIZE)
    self.locking_queue = Queue(maxsize=HsmWithQueues.QUEUE_SIZE)

  def get(self, block=True, timeout=None):
    '''block on the locking queue, popleft from deque'''
    return self.locking_queue.get(block, timeout)

  def wait(self, block=True, timeout=None):
    '''wait for an append/appendleft event'''
    return self.get(block, timeout)

  def popleft(self):
    return self.deque.popleft()

  def pop(self):
    return self.deque.pop()

  def append(self, item):
    if self.locking_queue.full() is False:
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

  def appendleft(self, item):
    if self.locking_queue.full() is False:
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
    self.locking_queue.task_done()  # so that join can work

  def qsize(self):
    return self.locking_queue.qsize()

  def __len__(self):
    return len(self.deque)

  def len(self):
    return len(self.deque)


class ActiveObjectOutOfPostedEventResources(Exception):
  pass


class ActiveObject(HsmWithQueues):
  def __init__(self, name=None, instrumented=None):

    if instrumented is None:
      instrumented = True

    super().__init__(instrumented)
    self.locking_deque = LockingDeque()
    self.activeobject_task_event = ThreadEvent()
    # Over-write the deque in the Hsm with Queues with the one managed by the
    # LockingDeque object. This is the 'magic' in this object.  Any time a
    # post_fifo or post_lifo method within the Hsm is touched, it unknowingly uses
    # the LockingDeque object; which will also provide the 'get' method feature.
    # This 'get' method will allow our active object task to sleep until there
    # is something to do.  To understand this object, you need to grok this.
    self.queue = self.locking_deque

    # The active fabric is a singletlon that dispatches messages between all
    # active objects.  It provides a publish/subscribe infrastructure, and it will
    # post directly into our locking_deque object, and as a result, provide the
    # 'get' method of this object to unlock our task.
    self.fabric = ActiveFabric()
    self.thread = None
    self.name   = name

    # the QUEUE_SIZE is defined in HsmWithQueues
    self.posted_events_queue = deque(maxlen = self.__class__.QUEUE_SIZE)
    self.PostedEventThreadSpec = namedtuple('PostedEventThreadSpec',
      [
        'event',
        'queue_type',
        'total_times',
        'deferred',
        'period',
        'task_run_event',
      ]
    )
    self.PostedEvent = namedtuple('PostedEvents',
      [
        'signal_name',
        'task_run_event',
        'uuid',
      ]
    )

  def __thread_running(self):
    if self.thread is None:
      result = False
    else:
      result = True if self.thread.is_alive() else False
    return result

  def start_thread_if_not_running(fn):
    '''start the active object thread if it is not currently running'''
    def _start_thread_if_not_running(self, *args, **kwargs):
      if self.__thread_running() is False:
        self.__start()
      return fn(self, *args, **kwargs)
    return _start_thread_if_not_running

  def append_subscribe_to_spy(fn):
    '''instrument the full spy with our subscription request'''
    @wraps(fn)
    def _append_subscribe_to_spy(self, e_or_s, queue_type='fifo'):
      if type(e_or_s) == HsmEvent:
        signal_name = e_or_s.signal_name
      elif type(e_or_s) == int:
        signal_name = signals.name_for_signal(e_or_s)
      if self.instrumented:
        self.full.spy.append("SUBSCRIBING TO:({}, TYPE:{})".format(signal_name, queue_type))
        return fn(self, e_or_s, queue_type)
    return _append_subscribe_to_spy

  @start_thread_if_not_running
  @append_subscribe_to_spy
  def subscribe(self, event_or_signal, queue_type=None):
    if queue_type is None:
      queue_type = 'fifo'
    self.fabric.subscribe(self.queue, event_or_signal, queue_type)

  def append_publish_to_spy(fn):
    '''instrument the rtc spy with our publish event'''
    @wraps(fn)
    def _append_publish_to_spy(self, e, priority=1000):
      if self.instrumented:
        self.rtc.spy.append("PUBLISH:({}, PRIORITY:{})".format(e.signal_name, priority))
        return fn(self, e, priority)
    return _append_publish_to_spy

  @append_publish_to_spy
  @start_thread_if_not_running
  def publish(self, event, priority=None):
    '''publish an event at a given priority to the active fabric'''
    if priority is None:
      priority = 1000
    self.fabric.publish(event, priority)

  @start_thread_if_not_running
  def post_fifo(self, e, period=None, times=None, deferred=None):
    '''post an event, or events to the fifo queue

    Example of posting a single event into the fifo queue:
      ao.post_fifo(Event(signal=signals.A))

    Example create a short lived thread to post a one-shot event in one second:
      thread_id = ao.post_fifo(Event(signal=signals.A), period=1.0, time=1, deferred=True)

      # to cancel this one shot
      ao.cancel_event(thread_id)

    Example to create a heart beat of 0.7 seconds starting in 0.7 seconds:
      thread_id = ao.post_fifo(Event(signal=signals.A), period=0.7, deferred=True)

      # to kill this thread:
      ao.cancel_event(thread_id)

    '''
    if times is None:
      times = 0
    if deferred is None:
      deferred = True

    thread_id = None
    '''post using the HsmWithQueues's post_fifo api'''
    if period is None:
      super().post_fifo(e)
    else:
      # this will make another thread to post this event into our fifo
      thread_id = self.__post_event(e, times, period, deferred, queue_type='fifo')
    return thread_id

  @start_thread_if_not_running
  def post_lifo(self, e, period=None, times=None, deferred=None):
    '''post an event, or events to the lifo queue

    Example of posting a single event into the lifo queue:
      ao.post_lifo(Event(signal=signals.A))

    Example create a short lived thread to post a one-shot event in one second:
      thread_id = ao.post_lifo(Event(signal=signals.A), period=1.0, time=1, deferred=True)

      # to cancel this one shot
      ao.cancel_event(thread_id)

    Example to create a heart beat of 0.7 seconds starting in 0.7 seconds:
      thread_id = ao.post_lifo(Event(signal=signals.A), period=0.7, deferred=True)

      # to kill this thread:
      ao.cancel_event(thread_id)

    '''
    if times is None:
      times = 0
    if deferred is None:
      deferred = True

    thread_id = None

    '''post using the HsmWithQueues's post_lifo api'''
    if period is None:
      super().post_lifo(e)
    else:
      # this will make another thread to post this event into our lifo
      thread_id = self.__post_event(e, times, period, deferred, queue_type='lifo')
    return thread_id

  def make_unique_name_based_on_start_at_function(fn):
    '''
    If the user has not specified a name for their active object, we assign one
    based on the starting function and the first 5 characters created from a
    uuid5 using the starting state name.

    '''
    def _make_unique_name_based_on_start_at_function(self, initial_state):
      if self.name is None:
        function_name = initial_state(self, HsmEvent(signal=signals.REFLECTION_SIGNAL))
        self.name = str(uuid.uuid5(uuid.NAMESPACE_DNS, function_name))[0:5]
      fn(self, initial_state)
    return _make_unique_name_based_on_start_at_function

  @make_unique_name_based_on_start_at_function
  def start_at(self, initial_state):
    '''start the active object at a given state and begin its task'''
    super().start_at(initial_state)
    self.__start()

  def __start(self):
    '''Starts an active object thread, and the active fabric if it is not running'''
    # if the self.post_event_queue variable is not defined, create it
    try:
      self.posted_events_queue
    except:
      self.posted_events_queue = deque(maxlen=self.__class__.QUEUE_SIZE)

    # if the self.locking_deque variable is not defined, create it
    try:
      self.locking_deque
    except:
      self.locking_deque = LockingDeque()


    def start_thread(self):
      '''Starts an active object -- called within __start

      This will start an active object and the task fabric
      '''
      self.activeobject_task_event.set()

      # objects can talk to each other.
      if self.fabric.is_alive() is False:
        self.fabric.start()

      self.fabric_task_event = FiberThreadEvent()

      thread = Thread(target=self.run_event,
                args=(self.activeobject_task_event, self.fabric_task_event, self.queue))
      thread.name = self.name
      thread.daemon = True
      thread.start()
      return thread

    if self.__thread_running() is False:
      self.thread = start_thread(self)

  def stop(self):
    '''Stops the active object, can cancels all of its pending events'''
    self.activeobject_task_event.clear()

    # post an item to wake up the task so it can see it's event has been cleared
    # this will cause it to exit its forever-loop and exit
    self.queue.append(HsmEvent(signal=signals.stop_active_object))
    try:
      # If stop is being called outside of this active object, wait for this
      # thread to stop
      self.thread.join()
    except RuntimeError:
      # If stop is being called from within the active object thread, we can not
      # join our own thread, so proceed with the next steps
      pass

    # kill threads which were started by post_fifo or post_lifo single-shots or
    # multi-shots
    events_with_their_own_threads = [event for event in self.posted_events_queue]
    for event in events_with_their_own_threads:
      self.cancel_events(event)

  def run_event(self, task_event, fabric_task_event, queue):
    '''The active object threading function.

    If this statechart has not been stopped and the active fabric hasn't been
    stopped the threading function will run.  If the active fabric has been
    stopped, it will stop this thread as well by clearing the task_event
    HsmEvent (threading.Event) object.

    This threading method waits on the locking-deque.  If the signal is not a
    stop_active_object signal it calls the hsm next_rtc method, which will pop
    the leftmost item out of the deque part of the locking-deque and dispatch it
    into the hsm.
    '''
    while task_event.is_set():
      queue.wait()  # wait for an event
      if fabric_task_event.is_set():
        if len(self.queue) >= 1:
          if self.queue.deque[0].signal != signals.stop_active_object:
            self.next_rtc()
          else:
            task_event.clear()
      else:
        task_event.clear()
      queue.task_done()  # write this so that 'join' will work

  def trace(self):
    '''Output state transition information only:

    Example:
    print(chart.trace())
      [05:23:25.314420] [<state_name>] start_at(): top->hsm_queues_graph_g1_s22
      [05:23:25.314420] [<state_name>] D->(): hsm_queues_graph_g1_s22->hsm_queues_graph_g1_s1
      [05:23:25.314420] [<state_name>] E->(): hsm_queues_graph_g1_s1->hsm_queues_graph_g1_s01
      [05:23:25.314420] [<state_name>] F->(): hsm_queues_graph_g1_s01->hsm_queues_graph_g1_s2111
      [05:23:25.314420] [<state_name>] A->(): hsm_queues_graph_g1_s2111->hsm_queues_graph_g1_s321
    '''
    if not self.instrumented or not self.spied_on:
      return None
    strace = "\n"
    for tr in self.full.trace:
      strace += self.trace_tuple_to_formatted_string(tr)
    return strace

  def __post_event(self, e, times=None, period=None, deferred=None, queue_type=None):
    '''
    The post_event method is used to post one-shots or periodic events to the
    active object.

    It constructs a fabric_task_event and a task, then starts the task.  The task will
    run periodically posting events into either the fifo or the lifo of the
    active object.

    Examples:
      # Post an 'A' signal event into the lifo every 1.0 seconds, 5 times.

      # On the first time, wait one second prior to posting.  This should take
      # about 6 seconds to complete
      ao.post_event(Event(signal=signals.A),
                      time=5,
                      period=1.0,
                      deferred=True,
                      queue_type='lifo')

      # Now to cancel it, you can to cancel all events with the same
      # signal_name
      time.sleep(2.0)
      ao.cancel_events(Event(signal=signals.A))

    Example:
      # Post an event, without a time or periodic constraint
      ao.post_event(Event(signal=signals.B))  # same as ao.post_fifo(Event(signal=signals.B)

    Example of posting an event with the same signal name several times:

      # construct a thread which will post signal A, 15 times every 1 second to
      # the lifo of the active object
      post_id_1 = ao.post_event(Event(signal=signals.A),
                      time=15,
                      period=1.0,
                      deferred=True,
                      queue_type='lifo')

      # construct a thread which will post signal A, 15 times every 10 seconds to
      # the fifo of the active object
      post_id_2 = ao.post_event(Event(signal=signals.A),
                      time=15,
                      period=10.0,
                      queue_type='fifo')

      # To cancel the first event posting thread and leave the second event
      # posting thread to run:
      ao.cancel_event(uuid=uuid1)

    Example of linking a posted event to a state function handler:

        @spy_on
        def some_state_function(chart, e):
          status = return_status.UNHANDLED

          if(e.signal == signals.ENTRY_SIGNAL):
            # This will cause us to transition into the other_state_function
            # once every three seconds, starting at the next rtc event
            one_shot_uuid = chart.post_event(Event(Signal=signal.TIME_OUT,
                                                   period=3.0,
                                                   queue_type='lifo'))

            # Now we graffiti this chart with the 'one_shot_uuid' attribute so
            # that we can cancel it upon exiting the state
            chart.augment(other=one_shot_uuid, name='one_shot_uuid')
            status = return_status.HANDLED

          elif(e.signal == signals.EXIT_SIGNAL):
            chart.cancel_event(uuid=chart.one_shot_uuid)
            del(chart.one_shot_uuid)
            status = return_status.HANDLED

          elif(e.signal == signals.TIME_OUT):
            status = chart.trans(other_state_function)

          else:
            status, chart.temp.fun = return_status.SUPER, chart.top

          return status

    '''
    if deferred is None:
      deferred = True
    if queue_type is None:
      queue_type = 'fifo'
    if times is None:
      times = 1
    # if our times are set to 1 and there is no period then just post our event
    # to the fifo/lifo
    if times == 1 and period is None:
      if queue_type == 'fifo':
        self.post_fifo(e, period=None)
      else:
        self.post_lifo(e, period=None)
    else:
      # create an exit event for the task, it will be shared with the
      # cancel_event/cancel_events methods, so that the task can be stopped by
      # someone using the ActiveObject api
      task_run_event = ThreadEvent()
      task_run_event.set()

      # set up the specification for this task
      posted_event_thread_spec = \
        self.PostedEventThreadSpec(
          event=e,
          queue_type=queue_type,
          deferred=deferred,
          period=period,
          total_times=times,
          task_run_event=task_run_event,
        )

      def post_event_thread_runner(spec, deferred, times_activated):
        # We have a Event object here that can be controlled by something
        # outside of our task.  If it is cleared, then this thread will just
        # exit and disappear from the system.
        while spec.task_run_event.is_set():
          if deferred:
            time.sleep(spec.period)
          else:
            # Pretend that we waited the first time we entered this function
            # this way we can access the time.sleep on every pass through from
            # now on.
            deferred = True
          # we might have been cancelled while we were sleeping
          if spec.task_run_event.is_set() is not True:
            break

          times_activated += 1
          if spec.queue_type == 'fifo':
            self.post_fifo(spec.event)
          else:
            self.post_lifo(spec.event)

          # If we don't want to run forever we can clear our own Event
          if spec.total_times != 0:
            if(times_activated >= spec.total_times):
              spec.task_run_event.clear()

      thread = Thread(
        target=post_event_thread_runner,
        args=(posted_event_thread_spec,
              posted_event_thread_spec.deferred,
              0),
        daemon=True
      )
      thread.name = uuid.uuid4()
      thread.start()

      # If we have run out of spots in our queue we should issue an
      # ActiveObjectOutOfPostedEventResources since it indicates a MAJOR design
      # problem
      if(len(self.posted_events_queue) < self.__class__.QUEUE_SIZE):
        # track this thread in our posted_events deque
        self.posted_events_queue.append(
          self.PostedEvent(
            e.signal_name,
            task_run_event,
            thread.name,
          )
        )
      else:
        # Have the timer thread that we just constructed shut down (we
        # can't manage it in our posted_events deque)

        # This could easily happen if the user creates posted_event items on
        # entry and doesn't cancel them upon exiting the same state (see
        # comment in this function's docstring)
        pp(self.posted_events_queue)
        task_run_event.clear()
        raise(ActiveObjectOutOfPostedEventResources(
          "posted_events_queue size is too small for what you have asked for"))

    return thread.name

  def cancel_event(self, uuid=None):
    '''
    This will cancel an event thread that was created using the __post_event api.
    The original call to the __post_event api would have returned the uuid needed
    to cancel it with this call.

    If there are no threads managing the uuid provided, this method will do
    nothing.

    Example:

      post_id_1 = ao.post_fifo(Event(signal=signals.A),
                      time=15,
                      period=1.0,
                      deferred=True,
                      queue_type='lifo')

      ao.cancel_event(post_id_1)


    '''
    # print("cancel uuid: {}".format(uuid))
    for i in reversed(range(len(self.posted_events_queue))):
      posted_event_task_meta_data = self.posted_events_queue[-1]
      if posted_event_task_meta_data.uuid is uuid:
        # If this thread hasn't already finished, ask it to stop
        posted_event_task_meta_data.task_run_event.clear()
        # we aren't managing this thread anymore, remove it from our list
        self.posted_events_queue.pop()
        break
      else:
        self.posted_events_queue.rotate(1)

  def cancel_events(self, e):
    '''
    This will cancel all events that have the same signal name as e, that were
    posted using the __post_event.

    This will cancel all event threads which have the same signal name as 'e',
    that were created using the __post_event api.

    If there are no threads managing the signals name within the event
    provided, this method will do nothing.

    Example:

      post_id_1 = ao.post_fifo(Event(signal=signals.A),
                      time=15,
                      period=1.0,
                      deferred=True,
                      queue_type='lifo')

      post_id_2 = ao.post_fifo(Event(signal=signals.A),
                      time=15,
                      period=1.0,
                      deferred=True,
                      queue_type='lifo')

      ao.cancel_events(Event(signal=signals.A))
    '''
    # cancel all threads which could cause this event to take place
    for i in reversed(range(len(self.posted_events_queue))):
      posted_event_task_meta_data = self.posted_events_queue[-1]
      if posted_event_task_meta_data.signal_name is e.signal_name:
        # If this thread hasn't already finished, ask it to stop
        posted_event_task_meta_data.task_run_event.clear()
        # we aren't managing this thread anymore, remove it from our list
        self.posted_events_queue.pop()
      else:
        self.posted_events_queue.rotate(1)


class Factory(ActiveObject):

  class StateMethodBlueprint():
    def __init__(self, name, ao):
      self.name = name
      self.state_method = state_method_template(name)
      self.ao = ao

    def catch(self, signal, handler):
      self.ao.register_signal_callback(self.state_method, signal, handler)
      return self

    def to_method(self):
      return self.state_method

  def __init__(self, name):
    super().__init__()
    self.name = name
    self.states = {}

  def create(self, state=None):
    '''
    This will allow the Factory to create different things and attach them to
    itself, for now it can only create states.

    '''
    self.states[state] = self.__class__.StateMethodBlueprint(name=state, ao=self)
    return self.states[state]

  def nest(self, state, parent):
    if type(state) == str:
      state_method = self.state[state].state_method
    else:
      state_method = state

    if type(parent) == str:
      parent_state_method = self.state[parent].state_method
    else:
      parent_state_method = parent
      if parent_state_method is None:
        parent_state_method = self.top

    self.register_parent(state_method, parent_state_method)
    return self

  def start_at(self, state):
    if type(state) == str:
      state_method = self.state[state].state_method
    else:
      state_method = state

    super().start_at(state_method)

  def to_code(self, state):
    if type(state) == str:
      state_method = self.states[state].state_method
    else:
      state_method = state
    return super().to_code(state_method)
