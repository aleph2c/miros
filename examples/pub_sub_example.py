# pub_sub_example.py
import time
from collections import namedtuple

from miros import Event
from miros import spy_on
from miros import signals
from miros import Factory
from miros import ActiveObject
from miros import return_status

Coordinate = \
  namedtuple('Coordinate', ['x','y', 'z'])

class Chart1(ActiveObject):
  def __init__(self, name):
    super().__init__(name)
    self.x, self.y, self.z = None, None, None

  def print_payload(self):
    print("x: {}, y: {}, z: {}".format(self.x, self.y, self.z))

@spy_on
def c_1_outer_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.subscribe(Event(signal=signals.Chart_2_Started))
    status = return_status.HANDLED
  elif(e.signal == signals.Chart_2_Started):
    chart.x = e.payload.x
    chart.y = e.payload.y
    chart.z = e.payload.z
    status = chart.trans(c_1_inner_state)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER
  return status

@spy_on
def c_1_inner_state(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.print_payload()
    chart.post_lifo(Event(signal=signals.Reset))
    status = return_status.HANDLED
  elif(e.signal == signals.Reset):
    status = chart.trans(c_1_outer_state)
  elif(e.signal == signals.INIT_SIGNAL):
    status = return_status.HANDLED
  else:
    chart.temp.fun = c_1_outer_state
    status = return_status.SUPER
  return status


class Chart2(Chart1, Factory):

  def __init__(self, name, live_trace=None, live_spy=None):
    super().__init__(name)
    self.x = 0
    self.live_spy = False if live_spy == None else live_spy
    self.live_trace = False if live_trace == None else live_trace

    self.c_2_outer_state = self.create(state="c_2_outer_state"). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.c_2_outer_state_init_signal). \
      catch(signal=signals.Reset,
        handler=self.c_2_outer_state_reset). \
      to_method()

    self.c_2_inner_state = self.create(state="c_2_inner_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c_2_outer_state_entry_signal). \
      to_method()

    self.nest(self.c_2_outer_state, parent=None). \
         nest(self.c_2_inner_state, parent=self.c_2_outer_state)

    self.start_at(self.c_2_inner_state)

  def increment_x(self):
    self.x += 1

  @staticmethod
  def c_2_outer_state_init_signal(chart, e):
    status = chart.trans(chart.c_2_inner_state)
    return status

  @staticmethod
  def c_2_outer_state_reset(chart, e):
    chart.increment_x()
    status = chart.trans(chart.c_2_outer_state)
    return status

  @staticmethod
  def c_2_outer_state_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.publish(Event(signal=signals.Chart_2_Started,
      payload=Coordinate(x=chart.x, y=2, z=3)))
    return status

if __name__ == '__main__':
  # need to create an active object
  # set it's live trace attribute
  # then start it in the correct state
  c_1 = Chart1('c_1')
  c_1.live_trace = True
  c_1.start_at(c_1_outer_state)

  # Chart2 starts itself in the correct state
  c_2 = Chart2(name='c_2', live_trace=True)
  c_2.post_fifo(Event(signal=signals.Reset))
  c_2.post_fifo(Event(signal=signals.Reset))
  time.sleep(0.1)
  
