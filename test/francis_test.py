import pprint
import pytest
import traceback
from miros import (Event, signals, return_status, spy_on, ActiveObject, pp, stripped)
import threading
import time
import sys

# -----------------------------------------------------------------------------
# | test scenarios | spy_on_decorators | instrumented | live_spy | live_trace |
# | Test_Group_1   | no                | no           | no       | no         |
# | Test_Group_2   | no                | no           | no       | yes        |
# | Test_Group_3   | no                | no           | yes      | no         |
# | Test_Group_4   | no                | no           | yes      | yes        |
# | Test_Group_5   | no                | yes          | no       | no         |
# | Test_Group_6   | no                | yes          | no       | yes        |
# | Test_Group_7   | no                | yes          | yes      | no         |
# | Test_Group_8   | no                | yes          | yes      | yes        |
# | Test_Group_9   | yes               | no           | no       | no         |
# | Test_Group_10  | yes               | no           | no       | yes        |
# | Test_Group_11  | yes               | no           | yes      | no         |
# | Test_Group_12  | yes               | no           | yes      | yes        |
# | Test_Group_13  | yes               | yes          | no       | no         |
# | Test_Group_14  | yes               | yes          | no       | yes        |
# | Test_Group_15  | yes               | yes          | yes      | no         |
# | Test_Group_16  | yes               | yes          | yes      | yes        |
# -----------------------------------------------------------------------------

# typical test:
# 
# a,b,d,h,g,c,c,f,e,f,f,a,b,d,h
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


class ExampleStatechart(ActiveObject):

  def __init__(self, name):
    super().__init__(name)
    self.foo = None

  def write(self, string):
    print(string, end=';')

@spy_on
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

@spy_on
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
    me.write("s1-D")
    status = return_status.HANDLED
    if me.foo == 0:
      me.foo = 1; me.write("foo = 1")
      status = me.trans(s)
  elif(e.signal == signals.F):
    me.write("s1-F")
    status = me.trans(s211)
  elif(e.signal == signals.I):
    me.write("s1-I")
    status = return_status.HANDLED
  else:
    me.temp.fun = s
    status = return_status.SUPER
  return status   

@spy_on
def s11(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):  
    me.write('s11-ENTRY')
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    me.write('s11-EXIT')
    status = return_status.HANDLED
  elif(e.signal == signals.D):
    me.write('s11-D')
    if me.foo:
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

@spy_on
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

@spy_on
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

@spy_on
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

@pytest.mark.francis
def test_for_broken_init_bug(spy_chart):
  chart = ExampleStatechart(name='demochart1')
  chart.start_at(s2)
  chart.post_fifo(Event(signal=signals.E))
  time.sleep(0.1)
  chart.clear_spy()
  chart.clear_trace()
  chart.post_fifo(Event(signal=signals.C))
  time.sleep(0.1)
  expected_spy = \
    ['C:s11',
     'C:s1',
     'EXIT_SIGNAL:s11',
     'SEARCH_FOR_SUPER_SIGNAL:s11',
     'SEARCH_FOR_SUPER_SIGNAL:s2',
     'SEARCH_FOR_SUPER_SIGNAL:s1',
     'EXIT_SIGNAL:s1',
     'ENTRY_SIGNAL:s2',
     'INIT_SIGNAL:s2',
     'SEARCH_FOR_SUPER_SIGNAL:s211',
     'SEARCH_FOR_SUPER_SIGNAL:s21',
     'ENTRY_SIGNAL:s21',
     'ENTRY_SIGNAL:s211',
     'INIT_SIGNAL:s211',
     '<- Queued:(0) Deferred:(0)']
  assert(chart.spy() == expected_spy)

  expected_trace = '''
    [2019-02-19 11:47:14.617768] [demochart1] e->C() s11->s211'''
  with stripped(expected_trace) as stripped_target, stripped(chart.trace()) as stripped_result:
   assert(stripped_target == stripped_result)

@pytest.mark.francis
def test_for_broken_H(spy_chart):
  chart = ExampleStatechart(name='demochart1')
  chart.start_at(s2)
  chart.post_fifo(Event(signal=signals.E))
  chart.post_fifo(Event(signal=signals.H))
  time.sleep(1)
  print(chart.trace())
  pp(chart.spy())


@pytest.mark.francis
def test_for_broken_G(spy_chart):
  chart = ExampleStatechart(name='demochart1')
  chart.start_at(s2)
  time.sleep(1)
  chart.post_fifo(Event(signal=signals.E))
  print()
  time.sleep(1)
  chart.post_fifo(Event(signal=signals.G))
  print()
  time.sleep(1)
  print(chart.trace())
  pp(chart.spy())
