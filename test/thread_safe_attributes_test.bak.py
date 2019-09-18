import os
import re
import time
import pytest
import random
import logging
from pathlib import Path
from threading import Thread
from functools import partial
from threading import Event as ThreadEvent

from miros import Event
from miros import spy_on
from miros import signals
from miros import Factory
from miros import ActiveObject
from miros import return_status
from miros import ThreadSafeAttributes
from miros import FactoryWithAttributes
from miros import ActiveObjectWithAttributes
from miros import MetaThreadSafeAttributes

#from miros.thread_safe_attributes_broken import MetaThreadSafeAttributes
#class ThreadSafeAttributes(metaclass=MetaThreadSafeAttributes): pass

# the basic logger is not working, so build a custom logger
this_dir = (Path(__file__) / '..').resolve()
alog_file = str((this_dir / 'thread_safe_attribute_active_object.log'))
flog_file = str((this_dir / 'thread_safe_attribute_factory.log'))

################################################################################
#                       logging doesn't work with pytest                       #
################################################################################
# logger = logging.getLogger('thread_safe_attribute_tests')
# this_dir = (Path(__file__) / '..').resolve()
# alog_file = str((this_dir / 'thread_safe_attribute_active_object.log'))
# f_handler = logging.FileHandler(alog_file)
# f_handler.setLevel(logging.DEBUG)
# f_format = logging.Formatter('%(message)s')
# f_handler.setFormatter(f_format)
# logger.addHandler(f_handler)

def trace_callback(trace, log_file):
  '''trace without datetime-stamp, logger not working in pytest (hours wasted)'''
  trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
  with open(log_file, "a+") as fp:
    fp.write("T: " + trace_without_datetime + '\n')
  #logging.debug("T: " + trace_without_datetime)

def spy_callback(spy, log_file):
  '''trace without datetime-stamp, logger not working in pytest (hours wasted)'''
  logged_spy_message = "S: {}".format(spy)
  with open(log_file, "a+") as fp:
    fp.write(logged_spy_message+'\n')
  #logging.debug(logged_spy_message)

def get_spy_as_list(log_file):
  results = ""
  with open(log_file, 'r') as fp:
    output = [line for line in fp.readlines()]
    for line in output:
      #print(line, end='')
      if line[0] == 'S':
        results += line
  return results.split("\n")

def get_trace_as_list(log_file):
  results = ""
  with open(log_file, 'r') as fp:
    output = [line for line in fp.readlines()]
    for line in output:
      #print(line, end='')
      if line[0] == 'T':
        results += line
  return results.split("\n")

################################################################################
#             Active Object Representation of a Simple Statechart              #
################################################################################
@spy_on
def c(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_1 = False
    chart.thread_safe_attr_2 = False
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.INIT_SIGNAL):
    status = chart.trans(c1)
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.B):
    chart.thread_safe_attr_1 = True
    status = chart.trans(c)
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def c1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_1 = True
    status = return_status.HANDLED
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.A):
    status = chart.trans(c2)
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.thread_safe_attr_1 = False
    status = return_status.HANDLED
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  else:
    chart.temp.fun = c
    status = return_status.SUPER
  return status

@spy_on
def c2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.thread_safe_attr_2 = True
    status = return_status.HANDLED
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.A):
    status = chart.trans(c1)
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.thread_safe_attr_2 = False
    status = return_status.HANDLED
    chart.scribble("thread_safe_attr_1: {}".format(chart.thread_safe_attr_1))
    chart.scribble("thread_safe_attr_2: {}".format(chart.thread_safe_attr_2))
  else:
    chart.temp.fun = c
    status = return_status.SUPER
  return status

class Example1(ThreadSafeAttributes, ActiveObject):
  _attributes = ['thread_safe_attr_1', 'thread_safe_attr_2']

  def __init__(self, name):
    super().__init__(name)
    self.register_live_trace_callback(partial(trace_callback, log_file=alog_file))
    self.register_live_spy_callback(partial(spy_callback, log_file=alog_file))

################################################################################
#                Factory representation of a Simple Statechart                 #
################################################################################
class Example2(Factory):
  _attributes = ['thread_safe_attr_1', 'thread_safe_attr_2']

  def __init__(self, name, live_trace=None, live_spy=None):

    super().__init__(name=name)
    self.live_trace = False if live_trace == None else live_trace
    self.live_spy = False if live_spy == None else live_spy

    self.c = self.create(state="c"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.c_init_signal). \
      catch(signal=signals.B,
        handler=self.c_b). \
      to_method()

    self.c1 = self.create(state="c1"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c1_entry_signal). \
      catch(signal=signals.A,
        handler=self.c1_a). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.c1_exit_signal). \
      to_method()

    self.c2 = self.create(state="c2"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c2_entry_signal). \
      catch(signal=signals.A,
        handler=self.c2_a). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.c2_exit_signal). \
      to_method()

    self.nest(self.c, parent=None). \
         nest(self.c1, parent=self.c). \
         nest(self.c2, parent=self.c)

    self.register_live_trace_callback(partial(trace_callback, log_file=flog_file))
    self.register_live_spy_callback(partial(spy_callback, log_file=flog_file))

    self.start_at(self.c)

  def c_entry_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_1 = False
    self.thread_safe_attr_2 = False
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c_init_signal(self, e):
    status = self.trans(self.c1)
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c_b(self, e):
    self.thread_safe_attr_1 = True
    status = self.trans(self.c)
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c1_entry_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_1 = True
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c1_a(self, e):
    status = self.trans(self.c2)
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c1_exit_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_1 = False
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c2_entry_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_2 = True
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c2_a(self, e):
    status = self.trans(self.c1)
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

  def c2_exit_signal(self, e):
    status = return_status.HANDLED
    self.thread_safe_attr_2 = False
    self.scribble("thread_safe_attr_1: {}".format(self.thread_safe_attr_1))
    self.scribble("thread_safe_attr_2: {}".format(self.thread_safe_attr_2))
    return status

################################################################################
#     Testing thread-safe attributes outside of a statechart (in threads)      #
################################################################################
def make_test_thread1(name, object_to_hammer, thread_event):
  def thread_runner(name, obj, e):
    while e.is_set():
      if random.choice(list(['get', 'set'])) == 'get':
        logging.debug(name + str(obj.hammered_attribute))
      else:
        obj.hammered_attribute += 1 
      time.sleep(random.uniform(0, 0.5))
  return Thread(target=thread_runner, name=name, daemon=True, args=(name, object_to_hammer, thread_event))

def make_test_thread2(name, object_to_hammer, thread_event):
  def thread_runner2(name, obj, e):
    index = 0
    while e.is_set():
      obj.hammered_attribute += 1  # 1
      obj.hammered_attribute += 1  # 2
      obj.hammered_attribute += 1  # 3
      obj.hammered_attribute += 1  # 4
      obj.hammered_attribute += 1  # 5
      obj.hammered_attribute += 1  # 6
      obj.hammered_attribute += 1  # 7
      obj.hammered_attribute += 1  # 8
      obj.hammered_attribute += 1  # 9
      obj.hammered_attribute += 1  # 10
      #time.sleep(random.uniform(0, 0.005))
      index += 1 
      if index == 10:
        break
  return Thread(target=thread_runner2, name=name, daemon=True, args=(name, object_to_hammer, thread_event))

def thread_safe_attribute_test1(time_in_seconds, number_of_threads, alog_file):
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
       | ``alog_file`` (str): the file name used

    **Example(s)**:
      
    .. code-block:: python

       test_thread_safe_attribute(
         time_in_seconds=10,
         number_of_threads=100,
         alog_file=alog_file)

  '''
  # a class to test against
  class A3(metaclass=MetaThreadSafeAttributes):
    _attributes = ['hammered_attribute']

    def __init__(self, a, b, c):
      self.hammered_attribute = 0
      self.a = a
      self.b = b
      self.c = c

  # confirm that normal attributes are working
  a3 = A3(a=1, b=2, c=3)
  assert(a3.a == 1)
  assert(a3.b == 2)
  assert(a3.c == 3)
  # confirm that the thread safe attribute is working as expected from main
  a3.hammered_attribute = 0
  assert(a3.hammered_attribute == 0)
  a3.hammered_attribute += 1
  assert(a3.hammered_attribute == 1)
  a3.hammered_attribute -= 1
  assert(a3.hammered_attribute == 0)

  # begin the multithreaded tests
  # make an event that can turn off all threads
  event = ThreadEvent()
  event.set()
  # create and start the thread
  for i in range(number_of_threads):
    thread = make_test_thread1("thrd_" + "{0:02}:".format(i), a3, event)
    thread.start()

  # let the test run for the desired time
  time.sleep(time_in_seconds)

  # the test is over, open the log file and check the last number in it.
  # this number should always be equal to the last number or greater than the
  # last number. If this is true over the entire file, the test passes
  last_number = 0
  with open(alog_file, 'r') as fp:
    for line in fp.readlines():
      #print(line, end='')
      current_last = int(line.split(':')[-1])
      assert(current_last >= last_number)
      last_number = current_last

def thread_safe_attribute_test2(time_in_seconds, number_of_threads, alog_file):
  # a class to test against
  class A4(metaclass=MetaThreadSafeAttributes):
    _attributes = ['hammered_attribute']

    def __init__(self):
      self.hammered_attribute = 0

  # confirm that normal attributes are working
  a3 = A4()
  # confirm that the thread safe attribute is working as expected from main
  a3.hammered_attribute = 0
  assert(a3.hammered_attribute == 0)
  a3.hammered_attribute += 1
  assert(a3.hammered_attribute == 1)
  a3.hammered_attribute -= 1
  assert(a3.hammered_attribute == 0)

  # begin the multithreaded tests
  # make an event that can turn off all threads
  event = ThreadEvent()
  event.set()
  # create and start the thread
  for i in range(number_of_threads):
    thread = make_test_thread2("thrd_" + "{0:02}:".format(i), a3, event)
    thread.start()

  # let the test run for the desired time
  time.sleep(time_in_seconds)
  event.clear()
  time.sleep(0.5)
  assert(a3.hammered_attribute ==  number_of_threads * 100)

@pytest.mark.thread_safe_attributes
def test_thread_safe_attribute1():

  with open(alog_file, 'w') as fp:
    fp.write("")

  thread_safe_attribute_test1(
    time_in_seconds=10,
    number_of_threads=100,
    alog_file=alog_file)

@pytest.mark.isolated
@pytest.mark.thread_safe_attributes
def test_thread_safe_attribute2():

  with open(alog_file, 'w') as fp:
    fp.write("")

  thread_safe_attribute_test2(
    time_in_seconds=3,
    number_of_threads=1,
    alog_file=alog_file)

################################################################################
#             Begin testing thread-safe attributes in statecharts              #
################################################################################
expected_results = \
'''S: START
S: SEARCH_FOR_SUPER_SIGNAL:c
S: ENTRY_SIGNAL:c
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: INIT_SIGNAL:c
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: SEARCH_FOR_SUPER_SIGNAL:c1
S: ENTRY_SIGNAL:c1
S: thread_safe_attr_1: True
S: thread_safe_attr_2: False
S: INIT_SIGNAL:c1
S: <- Queued:(0) Deferred:(0)
S: A:c1
S: thread_safe_attr_1: False
S: thread_safe_attr_2: True
S: SEARCH_FOR_SUPER_SIGNAL:c2
S: SEARCH_FOR_SUPER_SIGNAL:c1
S: EXIT_SIGNAL:c1
S: thread_safe_attr_1: False
S: thread_safe_attr_2: True
S: ENTRY_SIGNAL:c2
S: thread_safe_attr_1: False
S: thread_safe_attr_2: True
S: INIT_SIGNAL:c2
S: <- Queued:(4) Deferred:(0)
S: B:c2
S: B:c
S: thread_safe_attr_1: True
S: thread_safe_attr_2: True
S: EXIT_SIGNAL:c2
S: thread_safe_attr_1: True
S: thread_safe_attr_2: False
S: SEARCH_FOR_SUPER_SIGNAL:c2
S: EXIT_SIGNAL:c
S: ENTRY_SIGNAL:c
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: INIT_SIGNAL:c
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: SEARCH_FOR_SUPER_SIGNAL:c1
S: ENTRY_SIGNAL:c1
S: thread_safe_attr_1: True
S: thread_safe_attr_2: False
S: INIT_SIGNAL:c1
S: <- Queued:(3) Deferred:(0)
S: A:c1
S: thread_safe_attr_1: True
S: thread_safe_attr_2: False
S: SEARCH_FOR_SUPER_SIGNAL:c2
S: SEARCH_FOR_SUPER_SIGNAL:c1
S: EXIT_SIGNAL:c1
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: ENTRY_SIGNAL:c2
S: thread_safe_attr_1: False
S: thread_safe_attr_2: True
S: INIT_SIGNAL:c2
S: <- Queued:(2) Deferred:(0)
S: B:c2
S: B:c
S: thread_safe_attr_1: True
S: thread_safe_attr_2: True
S: EXIT_SIGNAL:c2
S: thread_safe_attr_1: True
S: thread_safe_attr_2: False
S: SEARCH_FOR_SUPER_SIGNAL:c2
S: EXIT_SIGNAL:c
S: ENTRY_SIGNAL:c
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: INIT_SIGNAL:c
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: SEARCH_FOR_SUPER_SIGNAL:c1
S: ENTRY_SIGNAL:c1
S: thread_safe_attr_1: True
S: thread_safe_attr_2: False
S: INIT_SIGNAL:c1
S: <- Queued:(1) Deferred:(0)
S: A:c1
S: thread_safe_attr_1: True
S: thread_safe_attr_2: False
S: SEARCH_FOR_SUPER_SIGNAL:c2
S: SEARCH_FOR_SUPER_SIGNAL:c1
S: EXIT_SIGNAL:c1
S: thread_safe_attr_1: False
S: thread_safe_attr_2: False
S: ENTRY_SIGNAL:c2
S: thread_safe_attr_1: False
S: thread_safe_attr_2: True
S: INIT_SIGNAL:c2
S: <- Queued:(0) Deferred:(0)
'''

@pytest.mark.ao
@pytest.mark.scribble
@pytest.mark.live_spy
@pytest.mark.thread_safe_attributes
def test_thread_safe_in_active_object():
  global expected_results

  with open(alog_file, 'w') as fp:
    fp.write("")

  ao = Example1('example')
  ao.live_spy = True
  #ao.live_trace = True
  ao.start_at(c)
  ao.thread_safe_attr_1 = False
  ao.thread_safe_attr_2 = True
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.B))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.B))
  ao.post_fifo(Event(signal=signals.A))

  time.sleep(2)
  results = get_spy_as_list(alog_file)
  eresults = expected_results.split("\n")
  for i, item in enumerate(results):
    assert(results[i] == eresults[i])

  # remove comment if debugging this test
  os.remove(alog_file)

@pytest.mark.factory
@pytest.mark.scribble
@pytest.mark.live_spy
@pytest.mark.thread_safe_attributes
def test_thread_safe_in_factory():
  global expected_results

  with open(flog_file, 'w') as fp:
    fp.write("")

  fo = Example2('example', live_spy=True)
  fo.thread_safe_attr_1 = False
  fo.thread_safe_attr_2 = True
  fo.post_fifo(Event(signal=signals.A))
  fo.post_fifo(Event(signal=signals.B))
  fo.post_fifo(Event(signal=signals.A))
  fo.post_fifo(Event(signal=signals.B))
  fo.post_fifo(Event(signal=signals.A))

  time.sleep(2)
  results = get_spy_as_list(flog_file)
  eresults = expected_results.split("\n")
  for i, item in enumerate(results):
    assert(results[i] == eresults[i])

  # remove comment if debugging this test
  os.remove(flog_file)

if __name__ == '__main__':
  test_thread_safe_in_active_object()
  test_thread_safe_in_factory()
