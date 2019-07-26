# simple_state_1.py
import time

from miros import Event
from miros import signals
from miros import ActiveObject
from miros import return_status

def outer_state(chart, e):
  chart.temp.fun = chart.top
  status = return_status.SUPER
  return status

def inner_state(chart, e):
  chart.temp.fun = outer_state
  status = return_status.SUPER
  return status

if __name__ == '__main__':
  ao = ActiveObject('bob')
  ao.start_at(outer_state)
  time.sleep(1)
  
