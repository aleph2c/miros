import re
import time
import pytest
import random
import logging
from threading import Thread
from threading import Event as ThreadingEvent

from miros import MetaThreadSafeAttributes

from miros import Event
from miros import spy_on
from miros import signals
from miros import Factory
from miros import ActiveObject
from miros import return_status
from miros import ThreadSafeAttributes
from miros import FactoryWithAttributes
from miros import ActiveObjectWithAttributes

log_file = 'thread_safe_attribute.log'

logging.basicConfig(
  format='%(message)s',
  filename=log_file,
  level=logging.INFO)

@spy_on
def c(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_1 = False
    chart.thread_safe_attr_2 = False
  elif(e.signal == signals.INIT_SIGNAL):
    status = chart.trans(c1)
  elif(e.signal == signals.B):
    chart.thread_safe_attr_1 = True
    status = chart.trans(c)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
  chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  return status

@spy_on
def c1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_1 = True
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(c2)
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.thread_safe_attr_1 = False
    status = return_status.HANDLED
  else:
    chart.temp.fun = c
    status = return_status.SUPER
  chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
  chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  return status

@spy_on
def c2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_2 = True
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(c1)
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.thread_safe_attr_2 = False
    status = return_status.HANDLED
  else:
    chart.temp.fun = c
    status = return_status.SUPER
  chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
  chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  return status

def make_test_thread(name, object_to_hammer, thread_event):
  def thread_runner(name, obj, e):
    while e.is_set():
      if random.choice(list(['get', 'set'])) == 'get':
        logging.info(name + str(obj.hammed_attribute))
      else:
        obj.hammed_attribute += 1 
      time.sleep(random.uniform(0, 0.5))
  return Thread(target=thread_runner, name=name, daemon=True, args=(name, object_to_hammer, thread_event))

def thread_safe_attribute_test(time_in_seconds, number_of_threads, log_file):
  '''test the thread safe attribute feature provided by miros

    This test will create and run a given number of threads for a given number
    of seconds.  Each thread will either set an attribute or increment an
    attribute.  The results will be written to a log file (logging is thread
    safe) at INFO level.  This same log file will be openned at the end of the test, and it will be checked
    to confirm that the numbers increased monotonically.  This is confirming
    that all threads accessed and changed the same variable.

    **Args**:
       | ``time_in_seconds`` (int): time to run the parallel threads in the test
       | ``number_of_threads`` (int): the number of threads to test with
       | ``log_file`` (str): the file name used

    **Example(s)**:
      
    .. code-block:: python

       test_thread_safe_attribute(
         time_in_seconds=10,
         number_of_threads=100,
         log_file=log_file)

  '''
  # a class to test against
  class A3(metaclass=MetaThreadSafeAttributes):
    _attributes = ['hammed_attribute']

    def __init__(self, a, b, c):
      self.hammed_attribute = 0
      self.a = a
      self.b = b
      self.c = c

  # confirm that normal attributes are working
  a3 = A3(a=1, b=2, c=3)
  assert(a3.a == 1)
  assert(a3.b == 2)
  assert(a3.c == 3)
  # confirm that the thread safe attribute is working as expected from main
  a3.hammed_attribute = 0
  assert(a3.hammed_attribute == 0)
  a3.hammed_attribute += 1
  assert(a3.hammed_attribute == 1)
  a3.hammed_attribute -= 1
  assert(a3.hammed_attribute == 0)

  # begin the multithreaded tests
  # make an event that can turn off all threads
  event = ThreadEvent()
  event.set()
  # create and start the thread
  for i in range(number_of_threads):
    thread = make_test_thread("thrd_" + "{0:02}:".format(i), a3, event)
    thread.start()

  # let the test run for the desired time
  time.sleep(time_in_seconds)

  # the test is over, open the log file and check the last number in it.
  # this number should always be equal to the last number or greater than the
  # last number. If this is true over the entire file, the test passes
  last_number = 0
  with open(log_file, 'r') as fp:
    for line in fp.readlines():
      print(line, end='')
      current_last = int(line.split(':')[-1])
      assert(current_last >= last_number)
      last_number = current_last

@pytest.mark.thread_safe_attributes
def test_thread_safe_attribute():

  with open(log_file, 'w') as fp:
    fp.write("")

  thread_safe_attribute_test(
    time_in_seconds=10,
    number_of_threads=100,
    log_file=log_file)

def trace_callback(trace):
  '''trace without datetime-stamp'''
  trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
  logging.info("T: " + trace_without_datetime)

def spy_callback(spy):
  '''trace without datetime-stamp'''
  logging.info("S: {}" + spy)

class Example1(ThreadSafeAttributes, ActiveObject):
  _attributes = ['thread_safe_attr_1', 'thread_safe_attr_2']

  def __init__(self, name):
    super().__init__(name)
    self.register_live_trace_callback(trace_callback)
    self.register_live_trace_callback(spy_callback)

@pytest.mark.isolated
@pytest.mark.thread_safe_attributes
def test_active_object():

  with open(log_file, 'w') as fp:
    fp.write("")

  ao = Example1('example')
  ao.live_spy = True
  ao.start_at(c)
  ao.thread_safe_attr_1 = False
  ao.thread_safe_attr_2 = True
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.B))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.B))
  ao.post_fifo(Event(signal=signals.A))

  with open(log_file, 'r') as fp:
    for line in fp.readlines():
      print(line, end='')


