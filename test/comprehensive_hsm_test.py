# comprehensive test of all possible hsm transitions with instrumentation
# features turned on and off
import time
import pprint
import pytest
import traceback
from miros import pp
from miros import Event
from miros import spy_on
from miros import signals
from miros import stripped
from threading import Thread
from miros import ActiveObject
from miros import return_status
from threading import Event as ThreadEvent

# Examples
# pytest -m --vv hsm
# pytest -m --vv comprehensive
# pytest -m --vv test_group_1
# pytest -m --vv instrumented
# pytest -m --vv no_spy_on_dectorator
# pytest -m --vv spy_on_dectorator
# pytest -m --vv not_instrumented
# pytest -m --vv no_live_spy
# pytest -m --vv live_spy
# pytest -m --vv no_live_trace
# pytest -m --vv live_trace
# -----------------------------------------------------------------------------
# | test scenarios | spy_on_decorators | instrumented | live_spy | live_trace |
# | test_group_1   | no                | no           | no       | no         |
# | test_group_2   | no                | no           | no       | yes        |
# | test_group_3   | no                | no           | yes      | no         |
# | test_group_4   | no                | no           | yes      | yes        |
# | test_group_5   | no                | yes          | no       | no         |
# | test_group_6   | no                | yes          | no       | yes        |
# | test_group_7   | no                | yes          | yes      | no         |
# | test_group_8   | no                | yes          | yes      | yes        |
# | test_group_9   | yes               | no           | no       | no         |
# | test_group_10  | yes               | no           | no       | yes        |
# | test_group_11  | yes               | no           | yes      | no         |
# | test_group_12  | yes               | no           | yes      | yes        |
# | test_group_13  | yes               | yes          | no       | no         |
# | test_group_14  | yes               | yes          | no       | yes        |
# | test_group_15  | yes               | yes          | yes      | no         |
# | test_group_16  | yes               | yes          | yes      | yes        |
# -----------------------------------------------------------------------------

# Typical Test:
# 
# a,b,d,h,g,c,c,f,e,f,f,a,b,d,h,d,d,i,i
# start:     foo = 0;s-ENTRY;s2-ENTRY;s2-INIT;s21-ENTRY;s211-ENTRY;
# 
# :A  s21-A;s211-EXIT;s21-EXIT;s21-ENTRY;s21-INIT;s211-ENTRY;
# :B  s21-B;s211-EXIT;s211-ENTRY;
# :D  s211-D;s211-EXIT;s21-INIT;s211-ENTRY;
# :H  s211-H;s211-EXIT;s21-EXIT;s2-EXIT;s-INIT;s1-ENTRY;s11-ENTRY;
# :G  s11-G;s11-EXIT;s1-EXIT;s2-ENTRY;s21-ENTRY;s211-ENTRY;
# :C  s2-C;s211-EXIT;s21-EXIT;s2-EXIT;s1-ENTRY;s1-INIT;s11-ENTRY;
# :C  s1-C;s11-EXIT;s1-EXIT;s2-ENTRY;s2-INIT;s21-ENTRY;s211-ENTRY;
# :F  s2-F;s211-EXIT;s21-EXIT;s2-EXIT;s1-ENTRY;s11-ENTRY;
# :E  s-E;s11-EXIT;s1-EXIT;s1-ENTRY;s11-ENTRY;
# :F  s1-F;s11-EXIT;s1-EXIT;s2-ENTRY;s21-ENTRY;s211-ENTRY;
# :F  s2-F;s211-EXIT;s21-EXIT;s2-EXIT;s1-ENTRY;s11-ENTRY;
# :A  s1-A;s11-EXIT;s1-EXIT;s1-ENTRY;s1-INIT;s11-ENTRY;
# ...

class ExampleStatechart(ActiveObject):

  def __init__(self, name):
    super().__init__(name)
    self.foo = None

  def write(self, string):
    print(string, end=';')

class ExampleStatechartMock(ExampleStatechart):

  def __init__(self, name=".format(name)mock"):
    super().__init__(name)
    self.results = ""
    self.live_trace_results = ""
    self.live_spy_results = []

  def write(self, string):
    self.results += string + ";"

  def clear(self):
    self.results = ""
    self.live_trace_results = ""
    self.live_spy_results = []

################################################################################
#                             Non-Instrumented HSM                             #
################################################################################
def s(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    me.write('s-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    me.write('s-INIT')
    status = me.trans(s11)
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s-EXIT')
    status = return_status.HANDLED
  elif(e.signal == signals.E):
    me.write('s-E')
    status = me.trans(s11)
  elif(e.signal == signals.I):
    me.write('s-I')
    status = return_status.HANDLED
    if me.foo:
      me.foo = 0; me.write("foo = 0")
  else:
    me.temp.fun = me.top
    status = return_status.SUPER
  return status

def s1(me, e):
  status = return_status.UNHANDLED
  
  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s1-ENTRY')
    status = return_status.HANDLED
  elif (e.signal == signals.INIT_SIGNAL):
    me.write('s1-INIT')
    status = me.trans(s11)
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s1-EXIT')
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    me.write("s1-A")
    status = me.trans(s1)
  elif(e.signal == signals.B):
    me.write("s1-B")
    status = me.trans(s11)
  elif(e.signal == signals.C):
    me.write("s1-C")
    status = me.trans(s2)
  elif(e.signal == signals.D):
    status = return_status.UNHANDLED
    if not me.foo:
      me.write("s1-D")
      me.foo = 1; me.write("foo = 1")
      status = me.trans(s)
  elif(e.signal == signals.F):
    me.write("s1-F")
    status = me.trans(s211)
  else:
    me.temp.fun = s
    status = return_status.SUPER
  return status   

def s11(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s11-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s11-EXIT')
    status = return_status.HANDLED
  elif(e.signal == signals.D):
    status = return_status.UNHANDLED
    if me.foo:
      me.write('s11-D')
      me.foo = 0; me.write("foo = 0")
      status = me.trans(s1)      
  elif(e.signal == signals.G):
    me.write('s11-G')
    status = me.trans(s211)
  elif(e.signal == signals.H):
    me.write('s11-H')
    status = me.trans(s)
  else:
    me.temp.fun = s1
    status = return_status.SUPER
  return status

def s2(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s2-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    me.write('s2-INIT')
    status = me.trans(s211)
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s2-EXIT')
    status = return_status.HANDLED  
  elif(e.signal == signals.I):
    me.write('s2-I')
    if not me.foo:
      me.foo = 1; me.write("foo = 1")
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    me.write('s2-C')
    status = me.trans(s1)
  elif(e.signal == signals.F):
    me.write('s2-F')
    status = me.trans(s11)
  else:
    me.temp.fun = s
    status = return_status.SUPER
  return status

def s21(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s21-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    me.write('s21-INIT')
    status = me.trans(s211)
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s21-EXIT')
    status = return_status.HANDLED 
  elif(e.signal == signals.A):
    me.write('s21-A')
    status = me.trans(s21)
  elif(e.signal == signals.B):
    me.write('s21-B')
    status = me.trans(s211)
  elif(e.signal == signals.G):
    me.write('s21-G')
    status = me.trans(s11)
  else:
    me.temp.fun = s2
    status = return_status.SUPER
  return status

def s211(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s211-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s211-EXIT')
    status = return_status.HANDLED   
  elif(e.signal == signals.D):
    me.write('s211-D')
    status = me.trans(s21)
  elif(e.signal == signals.H):
    me.write('s211-H')
    status = me.trans(s)
  else:
    me.temp.fun = s21
    status = return_status.SUPER
  return status
################################################################################
#                               Instrumented HSM                               #
################################################################################
@spy_on
def ss(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    me.write('s-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    me.write('s-INIT')
    status = me.trans(ss11)
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s-EXIT')
    status = return_status.HANDLED
  elif(e.signal == signals.E):
    me.write('s-E')
    status = me.trans(ss11)
  elif(e.signal == signals.I):
    me.write('s-I')
    status = return_status.HANDLED
    if me.foo:
      me.foo = 0; me.write("foo = 0")
  else:
    me.temp.fun = me.top
    status = return_status.SUPER
  return status

@spy_on
def ss1(me, e):
  status = return_status.UNHANDLED
  
  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s1-ENTRY')
    status = return_status.HANDLED
  elif (e.signal == signals.INIT_SIGNAL):
    me.write('s1-INIT')
    status = me.trans(ss11)
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s1-EXIT')
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    me.write("s1-A")
    status = me.trans(ss1)
  elif(e.signal == signals.B):
    me.write("s1-B")
    status = me.trans(ss11)
  elif(e.signal == signals.C):
    me.write("s1-C")
    status = me.trans(ss2)
  elif(e.signal == signals.D):
    status = return_status.UNHANDLED
    if not me.foo:
      me.write("s1-D")
      me.foo = 1; me.write("foo = 1")
      status = me.trans(ss)
  elif(e.signal == signals.F):
    me.write("s1-F")
    status = me.trans(ss211)
  else:
    me.temp.fun = ss
    status = return_status.SUPER
  return status   

@spy_on
def ss11(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s11-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s11-EXIT')
    status = return_status.HANDLED
  elif(e.signal == signals.D):
    status = return_status.UNHANDLED
    if me.foo:
      me.write('s11-D')
      me.foo = 0; me.write("foo = 0")
      status = me.trans(ss1)      
  elif(e.signal == signals.G):
    me.write('s11-G')
    status = me.trans(ss211)
  elif(e.signal == signals.H):
    me.write('s11-H')
    status = me.trans(ss)
  else:
    me.temp.fun = ss1
    status = return_status.SUPER
  return status

@spy_on
def ss2(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s2-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    me.write('s2-INIT')
    status = me.trans(ss211)
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s2-EXIT')
    status = return_status.HANDLED  
  elif(e.signal == signals.I):
    me.write('s2-I')
    if not me.foo:
      me.foo = 1; me.write("foo = 1")
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    me.write('s2-C')
    status = me.trans(ss1)
  elif(e.signal == signals.F):
    me.write('s2-F')
    status = me.trans(ss11)
  else:
    me.temp.fun = ss
    status = return_status.SUPER
  return status

@spy_on
def ss21(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s21-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    me.write('s21-INIT')
    status = me.trans(ss211)
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s21-EXIT')
    status = return_status.HANDLED 
  elif(e.signal == signals.A):
    me.write('s21-A')
    status = me.trans(ss21)
  elif(e.signal == signals.B):
    me.write('s21-B')
    status = me.trans(ss211)
  elif(e.signal == signals.G):
    me.write('s21-G')
    status = me.trans(ss11)
  else:
    me.temp.fun = ss2
    status = return_status.SUPER
  return status

@spy_on
def ss211(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s211-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s211-EXIT')
    status = return_status.HANDLED   
  elif(e.signal == signals.D):
    me.write('s211-D')
    status = me.trans(ss21)
  elif(e.signal == signals.H):
    me.write('s211-H')
    status = me.trans(ss)
  else:
    me.temp.fun = ss21
    status = return_status.SUPER
  return status

def naked_driver(chart, event, target):
  '''naked chart test (works with or without instrumentation): clears, posts event,
     waits, then checks the result.

  **Args**:
     | ``chart`` (ActiveObject): tested statechart
     | ``event`` (event|str): event or signal name of the event you want to post
     | ``target`` (str): expected result

  **Example(s)**:
    
  .. code-block:: python

    nake_driver(chart, "G",
      "s11-G;s11-EXIT;s1-EXIT;s2-ENTRY;s21-ENTRY;s211-ENTRY;")

  '''
  if type(event) is str:
    event = eval("Event(signal=signals.{})".format(event))
  chart.clear()
  chart.post_fifo(event)
  time.sleep(0.01)
  assert(chart.results == target)

def live_trace_driver(chart, event, trace_target):
  '''live trace test: clears, posts event, waits, then checks the result

  **Note(s)**:
    Uses the stripped context manager to remove datetime stamps before 
    test comparison

  **Args**:
     | ``chart`` (ActiveObject): tested statechart
     | ``event`` (event|str): event or signal name of the event you want to post
     | ``trace_target`` (str): expected result

  **Example(s)**:
    
  .. code-block:: python
     
    live_trace_driver(chart, "A",
      "[2019-02-23 08:08:34.878743] [{}] e->A() ss211->ss211".format(name))

  '''
  chart.clear()
  if type(event) is str:
    event = eval("Event(signal=signals.{})".format(event))
  chart.post_fifo(event)
  time.sleep(0.01)

  if trace_target == '':
    assert(chart.live_trace_results == '')
  else:
    with stripped(trace_target) as target, \
         stripped(chart.live_trace_results) as result:
      try:
        assert(target == result[0])
      except:
        #print(chart.live_trace_results)
        chart.live_trace_results
        assert(target == result[0])

def trace_driver(chart, event, trace_target):
  '''trace test: clears, posts event, waits, then checks the result

  **Note(s)**:
    Uses the stripped context manager to remove datetime stamps before 
    test comparison

  **Args**:
     | ``chart`` (ActiveObject): tested statechart
     | ``event`` (event|str): event or signal name of the event you want to post
     | ``trace_target`` (str): expected result

  **Example(s)**:
    
  .. code-block:: python
     
    trace_driver(chart, "A",
      "[2019-02-23 08:08:34.878743] [{}] e->A() ss211->ss211".format(name))

  '''
  chart.clear_trace()

  if type(event) is str:
    event = eval("Event(signal=signals.{})".format(event))
  chart.post_fifo(event)
  time.sleep(0.01)

  if trace_target == '':
    assert(chart.trace().strip() == '')
  else:
    with stripped(trace_target) as target, \
         stripped(chart.trace()) as result:
      try:
        assert(target == result[0])
      except:
        #print(chart.trace())
        assert(target == result[0])

def helper_test_chart_is_working(chart, name, start_at):
  '''Test if the chart is working, with, or without instrumentation enabled

  **Args**:
     | ``chart`` (ActiveObject): tested ActiveObject
     | ``name`` (str): name of the statechart
     | ``start_at`` (fn): the starting state (callback)

  **Example(s)**:
    
  .. code-block:: python
     
    chart = ExampleStatechartMock(name='test_group_1')
    helper_test_chart_is_working(chart, 'test_group_1', s2)

  '''
  chart.start_at(start_at)
  time.sleep(0.01)
                                                       
  assert(chart.results == \
    "s-ENTRY;s2-ENTRY;s2-INIT;s21-ENTRY;s211-ENTRY;")

  naked_driver(chart, "A", 
    "s21-A;s211-EXIT;s21-EXIT;s21-ENTRY;s21-INIT;s211-ENTRY;")

  naked_driver(chart, "B", 
    "s21-B;s211-EXIT;s211-ENTRY;")

  naked_driver(chart, "D",
    "s211-D;s211-EXIT;s21-INIT;s211-ENTRY;")

  naked_driver(chart, "H",
    "s211-H;s211-EXIT;s21-EXIT;s2-EXIT;s-INIT;s1-ENTRY;s11-ENTRY;")

  naked_driver(chart, "G",
    "s11-G;s11-EXIT;s1-EXIT;s2-ENTRY;s21-ENTRY;s211-ENTRY;")

  naked_driver(chart, "C",
    "s2-C;s211-EXIT;s21-EXIT;s2-EXIT;s1-ENTRY;s1-INIT;s11-ENTRY;")

  naked_driver(chart, "C",
    "s1-C;s11-EXIT;s1-EXIT;s2-ENTRY;s2-INIT;s21-ENTRY;s211-ENTRY;")

  naked_driver(chart, "F",
    "s2-F;s211-EXIT;s21-EXIT;s2-EXIT;s1-ENTRY;s11-ENTRY;")

  naked_driver(chart, "E",
    "s-E;s11-EXIT;s1-EXIT;s1-ENTRY;s11-ENTRY;")

  naked_driver(chart, "F",
    "s1-F;s11-EXIT;s1-EXIT;s2-ENTRY;s21-ENTRY;s211-ENTRY;")

  naked_driver(chart, "F",
    "s2-F;s211-EXIT;s21-EXIT;s2-EXIT;s1-ENTRY;s11-ENTRY;")

  naked_driver(chart, "A",
    "s1-A;s11-EXIT;s1-EXIT;s1-ENTRY;s1-INIT;s11-ENTRY;")

  naked_driver(chart, "B",
    "s1-B;s11-EXIT;s11-ENTRY;")

  naked_driver(chart, "D",
    "s1-D;foo = 1;s11-EXIT;s1-EXIT;s-INIT;s1-ENTRY;s11-ENTRY;")

  naked_driver(chart, "H",
    "s11-H;s11-EXIT;s1-EXIT;s-INIT;s1-ENTRY;s11-ENTRY;")

  naked_driver(chart, "D",
    "s11-D;foo = 0;s11-EXIT;s1-INIT;s11-ENTRY;")

  naked_driver(chart, "D",
    "s1-D;foo = 1;s11-EXIT;s1-EXIT;s-INIT;s1-ENTRY;s11-ENTRY;")

  naked_driver(chart, "D",
    "s11-D;foo = 0;s11-EXIT;s1-INIT;s11-ENTRY;")

  naked_driver(chart, "C",
    "s1-C;s11-EXIT;s1-EXIT;s2-ENTRY;s2-INIT;s21-ENTRY;s211-ENTRY;")

  naked_driver(chart, "I", "s2-I;foo = 1;")

  naked_driver(chart, "I", "s2-I;")

def helper_live_trace_off(chart, start_at):
  '''Test to confirm that the live_trace is off

  **Args**:
     | ``chart`` (ActiveObject): tested ActiveObject
     | ``start_at`` (fn): the starting state (callback)

  **Example(s)**:
    
  .. code-block:: python
     
    chart = ExampleStatechartMock(name='test_group_1')
    helper_live_trace_off(chart, start_at=s2)

  '''
  def live_trace_callback(trace_line):
    chart.live_trace_results += trace_line

  chart.register_live_trace_callback(live_trace_callback)
  chart.start_at(start_at)
  time.sleep(0.01)
  trace_target = ""
  with stripped(trace_target) as target, \
       stripped(chart.live_trace_results) as result:
    assert(target == result)

  live_trace_driver(chart, "A", "")
  live_trace_driver(chart, "B", "")
  live_trace_driver(chart, "D", "")
  live_trace_driver(chart, "H", "")
  live_trace_driver(chart, "G", "")
  live_trace_driver(chart, "C", "")
  live_trace_driver(chart, "C", "")
  live_trace_driver(chart, "F", "")
  live_trace_driver(chart, "E", "")
  live_trace_driver(chart, "F", "")
  live_trace_driver(chart, "A", "")
  live_trace_driver(chart, "D", "")
  live_trace_driver(chart, "D", "")
  live_trace_driver(chart, "D", "")
  live_trace_driver(chart, "C", "")
  live_trace_driver(chart, "I", "")
  live_trace_driver(chart, "I", "")

def helper_test_live_trace_on(chart, name, start_at):
  '''Test to confirm that the live_trace is on

  **Args**:
     | ``chart`` (ActiveObject): tested ActiveObject
     | ``name`` (str): name of the statechart
     | ``start_at`` (fn): the starting state (callback)

  **Example(s)**:
    
  .. code-block:: python
     
    chart = ExampleStatechartMock(name='test_group_1')
    helper_test_live_trace_on(chart, name=name, start_at=s2)

  '''

  chart.live_trace = True
  def live_trace_callback(trace_line):
    chart.live_trace_results += trace_line

  chart.register_live_trace_callback(live_trace_callback)
  chart.start_at(start_at)
  time.sleep(0.01)
  trace_target = \
    "[2019-02-23 08:08:34.878743] [{}] e->start_at() top->ss211".format(name)

  with stripped(trace_target) as target, \
       stripped(chart.live_trace_results) as result:
    assert(target == result)

  live_trace_driver(chart,
    "A",
    "[2019-02-23 08:08:34.878743] [{}] e->A() ss211->ss211".format(name))
  live_trace_driver(chart,
    "B",
    "[2019-02-23 10:19:35.167693] [{}] e->B() ss211->ss211".format(name))
  live_trace_driver(chart,
    "D",
    "[2019-02-23 10:22:16.090842] [{}] e->D() ss211->ss211".format(name))
  live_trace_driver(chart,
    "H",
    "[2019-02-23 10:23:40.777355] [{}] e->H() ss211->ss11".format(name))
  live_trace_driver(chart,
    "G",
    "[2019-02-23 10:26:08.725721] [{}] e->G() ss11->ss211".format(name))
  live_trace_driver(chart,
    "C",
    "[2019-02-23 10:26:49.244554] [{}] e->C() ss211->ss11".format(name))
  live_trace_driver(chart,
    "C",
    "[2019-02-23 10:27:18.599432] [{}] e->C() ss11->ss211".format(name))
  live_trace_driver(chart,
    "F",
    "[2019-02-23 10:27:46.127202] [{}] e->F() ss211->ss11".format(name))
  live_trace_driver(chart,
    "E",
    "[2019-02-23 10:28:14.209865] [{}] e->E() ss11->ss11".format(name))
  live_trace_driver(chart,
    "F",
    "[2019-02-23 10:28:47.806519] [{}] e->F() ss11->ss211".format(name))
  live_trace_driver(chart,
    "A",
    "[2019-02-23 10:29:14.099473] [{}] e->A() ss211->ss211".format(name))
  live_trace_driver(chart,
    "D",
    "[2019-02-23 10:37:42.823554] [{}] e->D() ss211->ss211".format(name))
  live_trace_driver(chart,
    "D",
    "[2019-02-23 10:37:42.823554] [{}] e->D() ss211->ss211".format(name))
  live_trace_driver(chart,
    "D",
    "[2019-02-23 10:37:42.823554] [{}] e->D() ss211->ss211".format(name))
  live_trace_driver(chart,
    "C",
    "[2019-02-23 10:26:49.244554] [{}] e->C() ss211->ss11".format(name))
  live_trace_driver(chart, "I", "")
  live_trace_driver(chart, "I", "")

def helper_test_trace_off(chart, start_at):
  '''Test to confirm that the trace is off

  **Args**:
     | ``chart`` (ActiveObject): tested ActiveObject
     | ``start_at`` (fn): the starting state (callback)

  **Example(s)**:
    
  .. code-block:: python
     
    chart = ExampleStatechartMock(name='test_group_1')
    helper_test_trace_off(chart, name=name, start_at=s2)

  '''
  chart.start_at(start_at)
  time.sleep(0.01)
  assert(chart.trace() == None)

  for event in [
    Event(signal=signals.A),
    Event(signal=signals.B),
    Event(signal=signals.D),
    Event(signal=signals.H),
    Event(signal=signals.G),
    Event(signal=signals.C),
    Event(signal=signals.C),
    Event(signal=signals.F),
    Event(signal=signals.E),
    Event(signal=signals.F),
    Event(signal=signals.F),
    Event(signal=signals.A),
    Event(signal=signals.B),
    Event(signal=signals.D),
    Event(signal=signals.H),
    Event(signal=signals.D),
    Event(signal=signals.D),
    Event(signal=signals.I),
    Event(signal=signals.I)]:

    chart.clear()
    chart.post_fifo(event)
    time.sleep(0.01)
    assert(chart.trace() == None)

def helper_test_trace_on(chart, name, start_at):
  '''Test to confirm that the trace is on

  **Args**:
     | ``chart`` (ActiveObject): tested ActiveObject
     | ``name`` (str): name of the statechart
     | ``start_at`` (fn): the starting state (callback)

  **Example(s)**:
    
  .. code-block:: python
     
    chart = ExampleStatechartMock(name='test_group_1')
    helper_test_trace_on(chart, name=name, start_at=s2)

  '''
  chart.start_at(start_at)
  time.sleep(0.01)
  trace_target = \
    "[2019-02-23 08:08:34.878743] [{}] e->start_at() top->ss211".format(name)

  with stripped(trace_target) as target, \
       stripped(chart.trace()) as result:
    assert(target == result[0])

  trace_driver(chart,
    "A",
    "[2019-02-23 08:08:34.878743] [{}] e->A() ss211->ss211".format(name))
  trace_driver(chart,
    "B",
    "[2019-02-23 10:19:35.167693] [{}] e->B() ss211->ss211".format(name))
  trace_driver(chart,
    "D",
    "[2019-02-23 10:22:16.090842] [{}] e->D() ss211->ss211".format(name))
  trace_driver(chart,
    "H",
    "[2019-02-23 10:23:40.777355] [{}] e->H() ss211->ss11".format(name))
  trace_driver(chart,
    "G",
    "[2019-02-23 10:26:08.725721] [{}] e->G() ss11->ss211".format(name))
  trace_driver(chart,
    "C",
    "[2019-02-23 10:26:49.244554] [{}] e->C() ss211->ss11".format(name))
  trace_driver(chart,
    "C",
    "[2019-02-23 10:27:18.599432] [{}] e->C() ss11->ss211".format(name))
  trace_driver(chart,
    "F",
    "[2019-02-23 10:27:46.127202] [{}] e->F() ss211->ss11".format(name))
  trace_driver(chart,
    "E",
    "[2019-02-23 10:28:14.209865] [{}] e->E() ss11->ss11".format(name))
  trace_driver(chart,
    "F",
    "[2019-02-23 10:28:47.806519] [{}] e->F() ss11->ss211".format(name))
  trace_driver(chart,
    "A",
    "[2019-02-23 10:29:14.099473] [{}] e->A() ss211->ss211".format(name))
  trace_driver(chart,
    "D",
    "[2019-02-23 10:37:42.823554] [{}] e->D() ss211->ss211".format(name))
  trace_driver(chart,
    "D",
    "[2019-02-23 10:37:42.823554] [{}] e->D() ss211->ss211".format(name))
  trace_driver(chart,
    "D",
    "[2019-02-23 10:37:42.823554] [{}] e->D() ss211->ss211".format(name))
  trace_driver(chart,
    "C",
    "[2019-02-23 10:26:49.244554] [{}] e->C() ss211->ss11".format(name))
  trace_driver(chart, "I", "")
  trace_driver(chart, "I", "")

def helper_test_spy_off(chart, start_at):
  '''Test to confirm that the spy is off

  **Args**:
     | ``chart`` (ActiveObject): tested ActiveObject
     | ``name`` (str): name of the statechart
     | ``start_at`` (fn): the starting state (callback)

  **Example(s)**:
    
  .. code-block:: python
     
    chart = ExampleStatechartMock(name='test_group_1')
    helper_test_spy_off(chart, name=name, start_at=s2)

  '''
  chart.start_at(start_at)
  time.sleep(0.01)
  assert(chart.spy() == None)

  for event in [
    Event(signal=signals.A),
    Event(signal=signals.B),
    Event(signal=signals.D),
    Event(signal=signals.H),
    Event(signal=signals.G),
    Event(signal=signals.C),
    Event(signal=signals.C),
    Event(signal=signals.F),
    Event(signal=signals.E),
    Event(signal=signals.F),
    Event(signal=signals.F),
    Event(signal=signals.A),
    Event(signal=signals.B),
    Event(signal=signals.D),
    Event(signal=signals.H),
    Event(signal=signals.D),
    Event(signal=signals.D),
    Event(signal=signals.I),
    Event(signal=signals.I)]:

    chart.clear()
    chart.post_fifo(event)
    time.sleep(0.01)
    assert(chart.spy() == None)

def helper_test_spy_on(chart, start_at):
  '''Test to confirm that the spy is on

  **Args**:
     | ``chart`` (ActiveObject): tested ActiveObject
     | ``start_at`` (fn): the starting state (callback)

  **Example(s)**:
    
  .. code-block:: python
     
    chart = ExampleStatechartMock(name='test_group_1')
    helper_test_spy_on(chart, name=name, start_at=s2)

  '''
  chart.start_at(start_at)
  time.sleep(0.01)

  assert(
    chart.spy() ==
    ['START',
      'SEARCH_FOR_SUPER_SIGNAL:ss2',
      'SEARCH_FOR_SUPER_SIGNAL:ss',
      'ENTRY_SIGNAL:ss',
      'ENTRY_SIGNAL:ss2',
      'INIT_SIGNAL:ss2',
      'SEARCH_FOR_SUPER_SIGNAL:ss211',
      'SEARCH_FOR_SUPER_SIGNAL:ss21',
      'ENTRY_SIGNAL:ss21',
      'ENTRY_SIGNAL:ss211',
      'INIT_SIGNAL:ss211',
      '<- Queued:(0) Deferred:(0)'])

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  assert(
    chart.spy() ==
      ['A:ss211',
        'A:ss21',
        'EXIT_SIGNAL:ss211',
        'SEARCH_FOR_SUPER_SIGNAL:ss211',
        'EXIT_SIGNAL:ss21',
        'ENTRY_SIGNAL:ss21',
        'INIT_SIGNAL:ss21',
        'SEARCH_FOR_SUPER_SIGNAL:ss211',
        'ENTRY_SIGNAL:ss211',
        'INIT_SIGNAL:ss211',
        '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.B))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['B:ss211',
      'B:ss21',
      'EXIT_SIGNAL:ss211',
      'SEARCH_FOR_SUPER_SIGNAL:ss211',
      'SEARCH_FOR_SUPER_SIGNAL:ss211',
      'ENTRY_SIGNAL:ss211',
      'INIT_SIGNAL:ss211',
      '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.D))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['D:ss211',
    'SEARCH_FOR_SUPER_SIGNAL:ss21',
    'SEARCH_FOR_SUPER_SIGNAL:ss211',
    'EXIT_SIGNAL:ss211',
    'INIT_SIGNAL:ss21',
    'SEARCH_FOR_SUPER_SIGNAL:ss211',
    'ENTRY_SIGNAL:ss211',
    'INIT_SIGNAL:ss211',
    '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.H))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['H:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'EXIT_SIGNAL:ss211',
     'EXIT_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'EXIT_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'INIT_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.G))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['G:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'EXIT_SIGNAL:ss11',
     'EXIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss21',
     'ENTRY_SIGNAL:ss211',
     'INIT_SIGNAL:ss211',
     '<- Queued:(0) Deferred:(0)']  
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.C))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['C:ss211',
     'C:ss21',
     'C:ss2',
     'EXIT_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'EXIT_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'EXIT_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss1',
     'INIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.C))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['C:ss11',
     'C:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'EXIT_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss2',
     'INIT_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'ENTRY_SIGNAL:ss21',
     'ENTRY_SIGNAL:ss211',
     'INIT_SIGNAL:ss211',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.F))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['F:ss211',
     'F:ss21',
     'F:ss2',
     'EXIT_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'EXIT_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'EXIT_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.E))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['E:ss11',
     'E:ss1',
     'E:ss',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'EXIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.F))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['F:ss11',
     'F:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'EXIT_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss21',
     'ENTRY_SIGNAL:ss211',
     'INIT_SIGNAL:ss211',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.F))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['F:ss211',
     'F:ss21',
     'F:ss2',
     'EXIT_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'EXIT_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'EXIT_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['A:ss11',
     'A:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'EXIT_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'INIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.B))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['B:ss11',
     'B:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.D))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['D:ss11',
     'EMPTY_SIGNAL:ss11',
     'D:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'EXIT_SIGNAL:ss1',
     'INIT_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.H))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['H:ss11',
    'SEARCH_FOR_SUPER_SIGNAL:ss',
    'SEARCH_FOR_SUPER_SIGNAL:ss11',
    'EXIT_SIGNAL:ss11',
    'EXIT_SIGNAL:ss1',
    'SEARCH_FOR_SUPER_SIGNAL:ss1',
    'INIT_SIGNAL:ss',
    'SEARCH_FOR_SUPER_SIGNAL:ss11',
    'SEARCH_FOR_SUPER_SIGNAL:ss1',
    'ENTRY_SIGNAL:ss1',
    'ENTRY_SIGNAL:ss11',
    'INIT_SIGNAL:ss11',
    '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.D))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['D:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'EXIT_SIGNAL:ss11',
     'INIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']

  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.D))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['D:ss11',
     'EMPTY_SIGNAL:ss11',
     'D:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'EXIT_SIGNAL:ss1',
     'INIT_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.I))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['I:ss11',
     'I:ss1',
     'I:ss',
     'I:ss:HOOK',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear_spy()
  chart.post_fifo(Event(signal=signals.I))
  time.sleep(0.01)
  assert(
    chart.spy() ==
    ['I:ss11',
     'I:ss1',
     'I:ss', 
     'I:ss:HOOK',
     '<- Queued:(0) Deferred:(0)']
  )

def helper_test_live_spy_off(chart, start_at):
  '''Test to confirm that the live spy is off

  **Args**:
     | ``chart`` (ActiveObject): tested ActiveObject
     | ``start_at`` (fn): the starting state (callback)

  **Example(s)**:
    
  .. code-block:: python
     
    chart = ExampleStatechartMock(name='test_group_1')
    helper_test_live_spy_off(chart, name=name, start_at=s2)

  '''
  chart.start_at(start_at)
  time.sleep(0.01)
  def live_spy_callback(spy_stuff):
    chart.live_spy_results.append(spy_stuff)

  assert(chart.live_spy_results == [])

  for event in [
    Event(signal=signals.A),
    Event(signal=signals.B),
    Event(signal=signals.D),
    Event(signal=signals.H),
    Event(signal=signals.G),
    Event(signal=signals.C),
    Event(signal=signals.C),
    Event(signal=signals.F),
    Event(signal=signals.E),
    Event(signal=signals.F),
    Event(signal=signals.F),
    Event(signal=signals.A),
    Event(signal=signals.B),
    Event(signal=signals.D),
    Event(signal=signals.H),
    Event(signal=signals.D),
    Event(signal=signals.D),
    Event(signal=signals.I),
    Event(signal=signals.I)]:

    chart.clear()
    chart.post_fifo(event)
    time.sleep(0.01)
    assert(chart.live_spy_results == [])

def helper_test_live_spy_on(chart, start_at):
  '''Test to confirm that the live spy is on

  **Args**:
     | ``chart`` (ActiveObject): tested ActiveObject
     | ``start_at`` (fn): the starting state (callback)

  **Example(s)**:
    
  .. code-block:: python
     
    chart = ExampleStatechartMock(name='test_group_1')
    helper_test_live_spy_on(chart, name=name, start_at=s2)

  '''
  def live_spy_callback(spy_stuff):
    chart.live_spy_results.append(spy_stuff)
  chart.register_live_spy_callback(live_spy_callback)

  chart.start_at(start_at)
  time.sleep(0.01)

  assert(
    chart.live_spy_results ==
    ['START',
      'SEARCH_FOR_SUPER_SIGNAL:ss2',
      'SEARCH_FOR_SUPER_SIGNAL:ss',
      'ENTRY_SIGNAL:ss',
      'ENTRY_SIGNAL:ss2',
      'INIT_SIGNAL:ss2',
      'SEARCH_FOR_SUPER_SIGNAL:ss211',
      'SEARCH_FOR_SUPER_SIGNAL:ss21',
      'ENTRY_SIGNAL:ss21',
      'ENTRY_SIGNAL:ss211',
      'INIT_SIGNAL:ss211',
      '<- Queued:(0) Deferred:(0)'])

  chart.clear()
  chart.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
      ['A:ss211',
        'A:ss21',
        'EXIT_SIGNAL:ss211',
        'SEARCH_FOR_SUPER_SIGNAL:ss211',
        'EXIT_SIGNAL:ss21',
        'ENTRY_SIGNAL:ss21',
        'INIT_SIGNAL:ss21',
        'SEARCH_FOR_SUPER_SIGNAL:ss211',
        'ENTRY_SIGNAL:ss211',
        'INIT_SIGNAL:ss211',
        '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.B))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['B:ss211',
      'B:ss21',
      'EXIT_SIGNAL:ss211',
      'SEARCH_FOR_SUPER_SIGNAL:ss211',
      'SEARCH_FOR_SUPER_SIGNAL:ss211',
      'ENTRY_SIGNAL:ss211',
      'INIT_SIGNAL:ss211',
      '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.D))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['D:ss211',
    'SEARCH_FOR_SUPER_SIGNAL:ss21',
    'SEARCH_FOR_SUPER_SIGNAL:ss211',
    'EXIT_SIGNAL:ss211',
    'INIT_SIGNAL:ss21',
    'SEARCH_FOR_SUPER_SIGNAL:ss211',
    'ENTRY_SIGNAL:ss211',
    'INIT_SIGNAL:ss211',
    '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.H))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['H:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'EXIT_SIGNAL:ss211',
     'EXIT_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'EXIT_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'INIT_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.G))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['G:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'EXIT_SIGNAL:ss11',
     'EXIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss21',
     'ENTRY_SIGNAL:ss211',
     'INIT_SIGNAL:ss211',
     '<- Queued:(0) Deferred:(0)']  
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.C))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['C:ss211',
     'C:ss21',
     'C:ss2',
     'EXIT_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'EXIT_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'EXIT_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss1',
     'INIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.C))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['C:ss11',
     'C:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'EXIT_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss2',
     'INIT_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'ENTRY_SIGNAL:ss21',
     'ENTRY_SIGNAL:ss211',
     'INIT_SIGNAL:ss211',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.F))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['F:ss211',
     'F:ss21',
     'F:ss2',
     'EXIT_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'EXIT_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'EXIT_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.E))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['E:ss11',
     'E:ss1',
     'E:ss',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'EXIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.F))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['F:ss11',
     'F:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'EXIT_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss21',
     'ENTRY_SIGNAL:ss211',
     'INIT_SIGNAL:ss211',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.F))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['F:ss211',
     'F:ss21',
     'F:ss2',
     'EXIT_SIGNAL:ss211',
     'SEARCH_FOR_SUPER_SIGNAL:ss211',
     'EXIT_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss21',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss2',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'EXIT_SIGNAL:ss2',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['A:ss11',
     'A:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'EXIT_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'INIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.B))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['B:ss11',
     'B:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.D))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['D:ss11',
     'EMPTY_SIGNAL:ss11',
     'D:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'EXIT_SIGNAL:ss1',
     'INIT_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.H))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['H:ss11',
    'SEARCH_FOR_SUPER_SIGNAL:ss',
    'SEARCH_FOR_SUPER_SIGNAL:ss11',
    'EXIT_SIGNAL:ss11',
    'EXIT_SIGNAL:ss1',
    'SEARCH_FOR_SUPER_SIGNAL:ss1',
    'INIT_SIGNAL:ss',
    'SEARCH_FOR_SUPER_SIGNAL:ss11',
    'SEARCH_FOR_SUPER_SIGNAL:ss1',
    'ENTRY_SIGNAL:ss1',
    'ENTRY_SIGNAL:ss11',
    'INIT_SIGNAL:ss11',
    '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.D))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['D:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'EXIT_SIGNAL:ss11',
     'INIT_SIGNAL:ss1',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']

  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.D))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['D:ss11',
     'EMPTY_SIGNAL:ss11',
     'D:ss1',
     'EXIT_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'EXIT_SIGNAL:ss1',
     'INIT_SIGNAL:ss',
     'SEARCH_FOR_SUPER_SIGNAL:ss11',
     'SEARCH_FOR_SUPER_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss1',
     'ENTRY_SIGNAL:ss11',
     'INIT_SIGNAL:ss11',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.I))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['I:ss11',
     'I:ss1',
     'I:ss',
     'I:ss:HOOK',
     '<- Queued:(0) Deferred:(0)']
  )

  chart.clear()
  chart.post_fifo(Event(signal=signals.I))
  time.sleep(0.01)
  assert(
    chart.live_spy_results ==
    ['I:ss11',
     'I:ss1',
     'I:ss', 
     'I:ss:HOOK',
     '<- Queued:(0) Deferred:(0)']
  )

@pytest.mark.hsm
@pytest.mark.comprehensive
@pytest.mark.test_group_1
@pytest.mark.no_spy_on_decorator
@pytest.mark.not_instrumented
@pytest.mark.no_live_spy
@pytest.mark.no_live_trace
def test_group_1(name='test_group_1'):
  '''
  spy_on_decorators: no
  instrumented:      no
  live_spy:          no
  live_trace:        no

    chart must work

    spy_on_decorators: no
      we use s2 as starting state

    instrumented: no
      instrumented off because the chart does not have spy_on decorators; this
      is detected at start_at

      spy must be empty
      trace must be empty

    live_spy: no: 
      live_spy must be empty

    live_trace: no
      live_trace must be empty

  '''
  def get_chart():
    chart = ExampleStatechartMock(name='test_group_1')
    start_at = s2
    return (chart, start_at)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, 'test_group_1', start_at)

  # spy_on_decorators: no
  chart, start_at = get_chart()
  chart.start_at(start_at)
  time.sleep(0.01)
  assert(chart.instrumented == False)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == False)

  # live_trace: no
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == False)

@pytest.mark.comprehensive
@pytest.mark.test_group_2
@pytest.mark.no_spy_on_decorator
@pytest.mark.not_instrumented
@pytest.mark.no_live_spy
@pytest.mark.live_trace
def test_group_2(name='test_group_2'):
  '''
  spy_on_decorators: no
  instrumented:      no
  live_spy:          no
  live_trace:        yes

    chart must work

    spy_on_decorators: no
      we use s2 as starting state

    instrumented: no
      instrumented off because the chart does not have spy_on decorators; this
      is detected at start_at

      spy must be empty
      trace must be empty

    live_spy: no: 
      live_spy must be empty

    live_trace: yes
      live_trace must be empty because the chart does not have spy_on decorators 

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.live_trace = True
    start_at = s2
    return (chart, start_at)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: no
  chart, start_at = get_chart()
  chart.start_at(start_at)
  time.sleep(0.01)
  assert(chart.instrumented == False)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)

  # live_trace: yes -- but live_trace should be off because
  # the chart does not have spy_on decorators
  chart, start_at = get_chart()
  assert(chart.live_trace == True)
  helper_live_trace_off(chart, start_at)


@pytest.mark.comprehensive
@pytest.mark.test_group_3
@pytest.mark.no_spy_on_decorator
@pytest.mark.not_instrumented
@pytest.mark.live_spy
@pytest.mark.no_live_trace
def test_group_3(name='test_group_3'):
  '''
  spy_on_decorators: no
  instrumented:      no
  live_spy:          yes
  live_trace:        no

    chart must work

    spy_on_decorators: no
      we use s2 as starting state

    instrumented: no
      instrumented off because the chart does not have spy_on decorators; this
      is detected at start_at

      spy must be empty
      trace must be empty

    live_spy: yes: 
      live_spy must be empty because the chart does not have spy_on decorators 

    live_trace: no
      live_trace must be empty

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.live_spy = True
    start_at = s2
    return (chart, start_at)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: no
  chart, start_at = get_chart()
  chart.start_at(start_at)
  time.sleep(0.01)
  assert(chart.instrumented == False)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)

  # live_trace: yes -- but live_trace should be off because
  # the chart does not have spy_on decorators
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)


@pytest.mark.comprehensive
@pytest.mark.test_group_4
@pytest.mark.no_spy_on_decorator
@pytest.mark.not_instrumented
@pytest.mark.live_spy
@pytest.mark.live_trace
def test_group_4(name='test_group_4'):
  '''
  spy_on_decorators: no
  instrumented:      no
  live_spy:          yes
  live_trace:        yes

    chart must work

    spy_on_decorators: no
      we use s2 as starting state

    instrumented: no
      instrumented off because the chart does not have spy_on decorators; this
      is detected at start_at

      spy must be empty
      trace must be empty

    live_spy: yes: 
      live_spy must be empty because the chart does not have spy_on decorators 

    live_trace: yes
      live_trace must be empty because the chart does not have spy_on decorators 

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.live_trace = True
    chart.live_spy = True
    return (chart, s2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: no
  chart, start_at = get_chart()
  chart.start_at(start_at)
  time.sleep(0.01)
  assert(chart.instrumented == False)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: yes
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == True)

  # live_trace: yes
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == True)

@pytest.mark.comprehensive
@pytest.mark.test_group_5
@pytest.mark.no_spy_on_decorator
@pytest.mark.instrumented
@pytest.mark.no_live_spy
@pytest.mark.no_live_trace
def test_group_5(name="test_group_5"):
  '''
  spy_on_decorators: no
  instrumented:      yes
  live_spy:          no
  live_trace:        no

    chart must work

    spy_on_decorators: no
      we use s2 as starting state

    instrumented: yes
      spy must be empty
      trace must be empty

    live_spy: no: 
      live_spy must be empty because the chart does not have spy_on decorators 

    live_trace: no
      live_trace must be empty because the chart does not have spy_on decorators 

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.instrumented = True
    return (chart, s2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: no
  # instrumented: yes
  chart, start_at = get_chart()
  assert(chart.instrumented == True)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  assert(chart.instrumented == False)
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == False)

  # live_trace: no
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == False)

@pytest.mark.comprehensive
@pytest.mark.test_group_6
@pytest.mark.no_spy_on_decorator
@pytest.mark.instrumented
@pytest.mark.no_live_spy
@pytest.mark.live_trace
def test_group_6(name="test_group_6"):
  '''
  spy_on_decorators: no
  instrumented:      yes
  live_spy:          no
  live_trace:        yes

    chart must work

    spy_on_decorators: no
      we use s2 as starting state

    instrumented: yes
      spy must be empty
      trace must be empty

    live_spy: no: 
      live_spy must be empty because the chart does not have spy_on decorators 

    live_trace: yes
      live_trace must be empty because the chart does not have spy_on decorators 

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.instrumented = True
    chart.live_trace = True
    return (chart, s2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: no
  # instrumented: yes
  chart, start_at = get_chart()
  assert(chart.instrumented == True)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  assert(chart.instrumented == False)
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == False)

  # live_trace: no
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == True)

@pytest.mark.comprehensive
@pytest.mark.test_group_7
@pytest.mark.no_spy_on_decorator
@pytest.mark.instrumented
@pytest.mark.live_spy
@pytest.mark.no_live_trace
def test_group_7(name="test_group_7"):
  '''
  spy_on_decorators: no
  instrumented:      yes
  live_spy:          yes
  live_trace:        no

    chart must work

    spy_on_decorators: no
      we use s2 as starting state

    instrumented: yes
      spy must be empty
      trace must be empty

    live_spy: yes: 
      live_spy must be empty because the chart does not have spy_on decorators 

    live_trace: no
      live_trace must be empty because the chart does not have spy_on decorators 

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.instrumented = True
    chart.live_spy = True
    return (chart, s2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: no
  # instrumented: yes
  chart, start_at = get_chart()
  assert(chart.instrumented == True)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  assert(chart.instrumented == False)
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == True)

  # live_trace: no
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == False)

@pytest.mark.comprehensive
@pytest.mark.test_group_8
@pytest.mark.no_spy_on_decorator
@pytest.mark.instrumented
@pytest.mark.live_spy
@pytest.mark.live_trace
def test_group_8(name="test_group_8"):
  '''
  spy_on_decorators: no
  instrumented:      yes
  live_spy:          yes
  live_trace:        yes

    chart must work

    spy_on_decorators: no
      we use s2 as starting state

    instrumented: yes
      spy must be empty
      trace must be empty

    live_spy: yes: 
      live_spy must be empty because the chart does not have spy_on decorators 

    live_trace: yes
      live_trace must be empty because the chart does not have spy_on decorators 

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.instrumented = True
    chart.live_spy = True
    chart.live_trace = True
    return (chart, s2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: no
  # instrumented: yes
  chart, start_at = get_chart()
  assert(chart.instrumented == True)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  assert(chart.instrumented == False)
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == True)

  # live_trace: no
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == True)

@pytest.mark.hsm
@pytest.mark.comprehensive
@pytest.mark.test_group_9
@pytest.mark.spy_on_decorator
@pytest.mark.not_instrumented
@pytest.mark.no_live_spy
@pytest.mark.no_live_trace
def test_group_9(name="test_group_9"):
  '''
  spy_on_decorators: yes
  instrumented:      no
  live_spy:          no
  live_trace:        no

    chart must work

    spy_on_decorators: yes
      we use ss2 as starting state

    instrumented: no
      spy must be empty
      trace must be empty

    live_spy: no: 
      live_spy must be empty because the chart instrumented attribute off

    live_trace: no
      live_trace must be empty because the chart instrumented attribute off

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.instrumented = False
    return (chart, ss2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: yes
  # instrumented: no
  chart, start_at = get_chart()
  assert(chart.instrumented == False)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  assert(chart.instrumented == False)
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == False)

  # live_trace: no
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == False)

@pytest.mark.comprehensive
@pytest.mark.test_group_10
@pytest.mark.spy_on_decorator
@pytest.mark.not_instrumented
@pytest.mark.no_live_spy
@pytest.mark.live_trace
def test_group_10(name="test_group_10"):
  '''
  spy_on_decorators: yes
  instrumented:      no
  live_spy:          no
  live_trace:        yes

    chart must work

    spy_on_decorators: yes
      we use ss2 as starting state

    instrumented: no
      spy must be empty
      trace must be empty

    live_spy: no: 
      live_spy must be empty because the chart instrumented attribute off

    live_trace: yes
      live_trace must be empty because the chart instrumented attribute off

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.instrumented = False
    chart.live_trace = True
    return (chart, ss2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: yes
  # instrumented: no
  chart, start_at = get_chart()
  assert(chart.instrumented == False)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  assert(chart.instrumented == False)
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == False)

  # live_trace: yes
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == True)

@pytest.mark.comprehensive
@pytest.mark.test_group_11
@pytest.mark.spy_on_decorator
@pytest.mark.not_instrumented
@pytest.mark.live_spy
@pytest.mark.no_live_trace
def test_group_11(name="test_group_11"):
  '''
  spy_on_decorators: yes
  instrumented:      no
  live_spy:          yes
  live_trace:        no

    chart must work

    spy_on_decorators: yes
      we use ss2 as starting state

    instrumented: no
      spy must be empty
      trace must be empty

    live_spy: yes: 
      live_spy must be empty because the chart instrumented attribute off

    live_trace: no
      live_trace must be empty because the chart instrumented attribute off

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.instrumented = False
    chart.live_spy = True
    return (chart, ss2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: yes
  # instrumented: no
  chart, start_at = get_chart()
  assert(chart.instrumented == False)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  assert(chart.instrumented == False)
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == True)

  # live_trace: yes
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == False)

@pytest.mark.comprehensive
@pytest.mark.test_group_12
@pytest.mark.spy_on_decorator
@pytest.mark.not_instrumented
@pytest.mark.live_spy
@pytest.mark.live_trace
def test_group_12(name="test_group_12"):
  '''
  spy_on_decorators: yes
  instrumented:      no
  live_spy:          yes
  live_trace:        yes

    chart must work

    spy_on_decorators: yes
      we use ss2 as starting state

    instrumented: no
      spy must be empty
      trace must be empty

    live_spy: yes: 
      live_spy must be empty because the chart instrumented attribute off

    live_trace: yes
      live_trace must be empty because the chart instrumented attribute off

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.instrumented = False
    chart.live_trace = True
    chart.live_spy = True
    return (chart, ss2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: yes
  # instrumented: no
  chart, start_at = get_chart()
  assert(chart.instrumented == False)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  assert(chart.instrumented == False)
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_off(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_off(chart, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == True)

  # live_trace: yes
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == True)

@pytest.mark.comprehensive
@pytest.mark.test_group_13
@pytest.mark.instrumented
@pytest.mark.spy_on_decorator
@pytest.mark.no_live_spy
@pytest.mark.no_live_trace
def test_group_13(name="test_group_13"):
  '''
  spy_on_decorators: yes
  instrumented:      yes
  live_spy:          no
  live_trace:        no

    chart must work

    spy_on_decorators: yes
      we use ss2 as starting state

    instrumented: yes
      spy must be full
      trace must be full

    live_spy: no: 
      live_spy must be empty because the feature is off

    live_trace: no
      live_trace must be empty because the feature is off

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    return (chart, ss2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: yes
  # instrumented: yes
  chart, start_at = get_chart()
  assert(chart.instrumented == True)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_on(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_on(chart, name, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == False)

  # live_trace: yes
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == False)

@pytest.mark.comprehensive
@pytest.mark.test_group_14
@pytest.mark.spy_on_decorator
@pytest.mark.instrumented
@pytest.mark.no_live_spy
@pytest.mark.live_trace
def test_group_14(name="test_group_14"):
  '''
  spy_on_decorators: yes
  instrumented:      yes
  live_spy:          no
  live_trace:        yes

    chart must work

    spy_on_decorators: yes
      we use ss2 as starting state

    instrumented: yes
      spy must be full
      trace must be full

    live_spy: no: 
      live_spy must be empty because the feature is off

    live_trace: yes
      live_trace must work

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.live_trace = True
    return (chart, ss2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: yes
  # instrumented: yes
  chart, start_at = get_chart()
  assert(chart.instrumented == True)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_on(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_on(chart, name, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_off(chart, start_at)
  assert(chart.live_spy == False)

  # live_trace: yes
  chart, start_at = get_chart()
  helper_test_live_trace_on(chart, name, start_at)
  assert(chart.live_trace == True)

@pytest.mark.comprehensive
@pytest.mark.test_group_15
@pytest.mark.spy_on_decorator
@pytest.mark.instrumented
@pytest.mark.live_spy
@pytest.mark.no_live_trace
def test_group_15(name="test_group_15"):
  '''
  spy_on_decorators: yes
  instrumented:      yes
  live_spy:          yes
  live_trace:        no

    chart must work

    spy_on_decorators: yes
      we use ss2 as starting state

    instrumented: yes
      spy must be full
      trace must be full

    live_spy: yes: 
      live_spy must work

    live_trace: no
      live_trace must be empty because the feature is off

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.live_spy = True
    return (chart, ss2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: yes
  # instrumented: yes
  chart, start_at = get_chart()
  assert(chart.instrumented == True)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_on(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_on(chart, name, start_at)

  # live_spy: no
  chart, start_at = get_chart()
  helper_test_live_spy_on(chart, start_at)
  assert(chart.live_spy == True)

  # live_trace: yes
  chart, start_at = get_chart()
  helper_live_trace_off(chart, start_at)
  assert(chart.live_trace == False)

@pytest.mark.comprehensive
@pytest.mark.test_group_16
@pytest.mark.spy_on_decorator
@pytest.mark.instrumented
@pytest.mark.live_spy
@pytest.mark.live_trace
def test_group_16(name="test_group_16"):
  '''
  spy_on_decorators: yes
  instrumented:      yes
  live_spy:          yes
  live_trace:        yes

    chart must work

    spy_on_decorators: yes
      we use ss2 as starting state

    instrumented: yes
      spy must be full
      trace must be full

    live_spy: yes: 
      live_spy must work

    live_trace: yes
      live_trace must work

  '''
  def get_chart():
    chart = ExampleStatechartMock(name)
    chart.live_spy = True
    chart.live_trace = True
    return (chart, ss2)

  # chart must work
  chart, start_at = get_chart()
  helper_test_chart_is_working(chart, name, start_at)

  # spy_on_decorators: yes
  # instrumented: yes
  chart, start_at = get_chart()
  assert(chart.instrumented == True)
  chart.start_at(start_at)
  # instrumented will turn off after start_at
  time.sleep(0.01)
  chart, start_at = get_chart()
  helper_test_spy_on(chart, start_at)
  chart, start_at = get_chart()
  helper_test_trace_on(chart, name, start_at)

  # live_spy: yes
  chart, start_at = get_chart()
  helper_test_live_spy_on(chart, start_at)
  assert(chart.live_spy == True)

  # live_trace: yes
  chart, start_at = get_chart()
  helper_test_live_trace_on(chart, name, start_at)
  assert(chart.live_trace == True)


