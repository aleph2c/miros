import pprint
import pytest
import traceback
from miros import (Event, signals, return_status, spy_on, ActiveObject, pp, stripped)
import threading
import time
import sys

class DemoChart(ActiveObject):
  def __init__(self, name):
    super().__init__(name)
    self.foo = None

@spy_on
def s(demochart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
        status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
        status = demochart.trans(s11)
    elif(e.signal == signals.EXIT_SIGNAL):
        status = return_status.HANDLED
    elif(e.signal == signals.E):
        status = demochart.trans(s11)
    elif(e.signal == signals.I):
        if demochart.foo:
            demochart.scribble("settin foo to 0")
            demochart.foo = 0
        status = return_status.HANDLED
    else:
        demochart.temp.fun = demochart.top
        status = return_status.SUPER
    return status

@spy_on
def s1(demochart, e):
    status = return_status.UNHANDLED
    
    if(e.signal == signals.ENTRY_SIGNAL):    
        status = return_status.HANDLED
    elif (e.signal == signals.INIT_SIGNAL):
        status = demochart.trans(s11)
    elif(e.signal == signals.EXIT_SIGNAL):
        status = return_status.HANDLED
    elif(e.signal == signals.A):
        status = demochart.trans(s1)
    elif(e.signal == signals.B):
        status = demochart.trans(s11)
    elif(e.signal == signals.C):
        status = demochart.trans(s2)
    elif(e.signal == signals.D):
        status = return_status.HANDLED
        if demochart.foo == 0:
            demochart.foo = 1
            status = demochart.trans(s)
    elif(e.signal == signals.F):
        status = demochart.trans(s211)
    else:
        demochart.temp.fun = s
        status = return_status.SUPER
    return status   

@spy_on
def s11(demochart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):    
        # b /mnt/c/github/miros/miros/hsm.py:593
        status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
        status = return_status.HANDLED
    elif(e.signal == signals.D):
        status = demochart.trans(s1)            
        if demochart.foo:
            demochart.scribble("settin foo to 0")
            demochart.foo = 0
    elif(e.signal == signals.G):
        status = demochart.trans(s211)
    elif(e.signal == signals.H):
        status = demochart.trans(s)
    else:
        demochart.temp.fun = s1
        status = return_status.SUPER
    return status

@spy_on
def s2(demochart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):    
        status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
        status = demochart.trans(s211)
    elif(e.signal == signals.EXIT_SIGNAL):
        status = return_status.HANDLED    
    elif(e.signal == signals.I):
        if not demochart.foo:
            demochart.scribble("setting foo to 1")
            demochart.foo = 1
        status = return_status.HANDLED
    elif(e.signal == signals.C):
        status = demochart.trans(s1)
    elif(e.signal == signals.F):
        status = demochart.trans(s11)
    else:
        demochart.temp.fun = s
        status = return_status.SUPER
    return status

@spy_on
def s21(demochart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):    
        status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
        status = demochart.trans(s211)
    elif(e.signal == signals.EXIT_SIGNAL):
        status = return_status.HANDLED 
    elif(e.signal == signals.A):
        status = demochart.trans(s21)
    elif(e.signal == signals.B):
        status = demochart.trans(s211)
    elif(e.signal == signals.G):
        status = demochart.trans(s11)
    else:
        demochart.temp.fun = s2
        status = return_status.SUPER
    return status

@spy_on
def s211(demochart, e):
    status = return_status.UNHANDLED
    
    if(e.signal == signals.ENTRY_SIGNAL):    
        status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
        status = return_status.HANDLED   
    elif(e.signal == signals.D):
        status = demochart.trans(s21)
    elif(e.signal == signals.H):
        status = demochart.trans(s)
    else:
        demochart.temp.fun = s21
        status = return_status.SUPER
    return status

@pytest.mark.francis
def test_for_broken_init_bug(spy_chart):
  chart = DemoChart(name='demochart1')
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

  
