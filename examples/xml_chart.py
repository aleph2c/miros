import re
import time
import logging
from functools import wraps
from functools import partial
from collections import deque
from collections import namedtuple

from miros import Event
from miros import spy_on
from miros import signals
from miros import Factory
from miros import return_status
from miros import HsmWithQueues

parallel = []

def instrumented(fn):
  @wraps(fn)
  def _pspy_on(chart, *args):
    if chart.instrumented:
      status = spy_on(fn)(chart, *args)
      for line in list(chart.rtc.spy):
         chart.outer.live_spy_callback(line)
      chart.rtc.spy.clear()
    else:
      e = args[0] if len(args) == 1 else args[-1]
      status = fn(chart, e)
    return status
  return _pspy_on

@instrumented
def s1_region_top(p, e):
  '''A state which is needed for the exit features of the s1 region to work.'''
  status = return_status.UNHANDLED
  if(e.signal == signals.Start_P):
    status = p.trans(s1_region)
  else:
    p.temp.fun = p.top
    status = return_status.SUPER
  return status

@instrumented
def s1_region(p, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = p.trans(s11)
  else:
    p.temp.fun = s1_region_top
    status = return_status.SUPER
  return status

@instrumented
def s11(p, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    # print('entering s11')
    status = return_status.HANDLED
  elif(e.signal == signals.e4):
    status = p.trans(s12)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.region_exit):
    status = p.trans(s1_region_top)
  else:
    p.temp.fun = s1_region
    status = return_status.SUPER
  return status

@instrumented
def s12(p, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.region_exit):
    status = p.trans(s1_region)
  else:
    p.temp.fun = s1_region
    status = return_status.SUPER
  return status

@instrumented
def s1_region_final(p, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    p.post_final_event_to_other_if_ready()
    status = return_status.HANDLED
    ready = True
    for region in p.regions:
      ready |= True if region.final else False
    if ready:
      p.outer.post_fifo(Event(signal=signals.p_final))
  elif(e.signal == signals.region_exit):
    status = p.trans(s1_region)
  else:
    p.temp.fun = s1_region
    status = return_status.SUPER
  return status

@instrumented
def s2_region_top(p, e):
  '''A state which is needed for the exit features of the s2 region to work.'''
  status = return_status.UNHANDLED
  if(e.signal == signals.Start_P):
    status = p.trans(s1_region)
  else:
    p.temp.fun = p.top
    status = return_status.SUPER
  return status

@instrumented
def s2_region(p, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = p.trans(s21)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    p.temp.fun = s2_region_top
    status = return_status.SUPER
  return status

@instrumented
def s21(p, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.e1):
    status = p.trans(s22)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.region_exit):
    status = p.trans(s2_region_top)
  else:
    p.temp.fun = s2_region
    status = return_status.SUPER
  return status

@instrumented
def s22(p, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.e2):
    status = p.trans(s2_region_final)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.region_exit):
    status = p.trans(s2_region)
  else:
    p.temp.fun = s2_region
    status = return_status.SUPER
  return status

@instrumented
def s2_region_final(p, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    ready = True
    for region in p.regions:
      ready |= region.name.final
    if ready:
      region.outer.post_fifo(Event(signal=signals.p_final))
  elif(e.signal == signals.region_exit):
    status = p.trans(s2_region)
  else:
    p.temp.fun = s2_region
    status = return_status.SUPER
  return status

class Region(HsmWithQueues):

  def __init__(self, name, outer, final_event, instrumented=True):
    super().__init__()
    self.name = name
    self.regions = []
    self.outer = outer
    self.final_event = final_event
    self.final = False
    self.state_fn = None
    self.instrumented = instrumented

  def post_final_event_to_other_if_ready(self):
    ready = True
    for region in p.regions:
      ready |= True if region.final else False
    if ready:
      p.outer.post_fifo(self.final_event)

class InstrumentedFactory(Factory):
  def __init__(self, name, *, log_file=None, live_trace=None, live_spy=None):
    super().__init__(name)
    self.live_trace = False if live_trace == None else live_trace
    self.live_spy = False if live_spy == None else live_spy
    self.log_file = 'xml_chart.log' if log_file == None else log_file

    with open(self.log_file, "w") as fp:
      fp.write("")

    logging.basicConfig(
      format='%(asctime)s %(levelname)s:%(message)s',
      filename=self.log_file,
      level=logging.DEBUG)

    self.register_live_spy_callback(partial(self.spy_callback))
    self.register_live_trace_callback(partial(self.trace_callback))

  def trace_callback(self, trace):
    '''trace without datetimestamp'''
    trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
    print(trace_without_datetime)
    logging.debug("T: " + trace_without_datetime)

  def spy_callback(self, spy):
    '''spy with machine name pre-pending'''
    print(spy)
    logging.debug("S: [{}] {}".format(self.name, spy))

class XmlChart(InstrumentedFactory):
  def __init__(self, name, live_trace=None, live_spy=None):
    '''comment'''
    super().__init__(name, live_trace=live_trace, live_spy=live_spy)
    self.p_regions = []

    self.s1_region = Region(
      's1_region',
      outer=self,
      final_event=Event(signal=signals.p_final),
    )
    self.p_regions.append(self.s1_region)

    self.s2_region = Region(
      's2_region',
      outer=self,
      final_event=Event(signal=signals.p_final),
    )
    self.p_regions.append(self.s2_region)

    for region in self.p_regions:
      for _region in self.p_regions:
        region.regions.append(_region)

    self.outer_state = self.create(state="outer_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.outer_state_entry_signal). \
      catch(signal=signals.to_p,
        handler=self.outer_state_to_p). \
      to_method()

    self.p = self.create(state="p"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.p_entry_signal). \
      catch(signal=signals.e1,
        handler=self.p_e1). \
      catch(signal=signals.e2,
        handler=self.p_e2). \
      catch(signal=signals.e4,
        handler=self.p_e4). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.p_exit). \
      catch(signal=signals.p_final,
        handler=self.p_p_final). \
      catch(signal=signals.to_outer,
        handler=self.p_to_outer). \
      to_method()

    self.some_other_state = self.create(state="someOtherState"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.some_other_state_entry_signal). \
      to_method()

    self.nest(self.outer_state, parent=None). \
      nest(self.p, parent=self.outer_state). \
      nest(self.some_other_state, parent=self.outer_state)

  def outer_state_entry_signal(self, e):
    status = return_status.HANDLED
    return status

  def outer_state_to_p(self, e):
    status = self.trans(self.p)
    return status

  def p_entry_signal(self, e):
    status = return_status.HANDLED

    if self.s1_region.state_fn == s1_region_top:
      self.s1_region.dispatch(Event(signal=signals.Start_P))
    else:
      self.s1_region.start_at(s11)

    if self.s2_region.state_fn == s2_region_top:
      self.s2_region.dispatch(Event(signal=signals.Start_P))
    else:
      self.s2_region.start_at(s21)

    return status

  def p_e1(self, e):
    status = return_status.HANDLED
    [region.dispatch(e) for region in reversed(self.p_regions)]
    return status

  def p_e2(self, e):
    status = return_status.HANDLED
    [region.dispatch(e) for region in self.p_regions]
    return status

  def p_e4(self, e):
    status = return_status.HANDLED
    [region.dispatch(e) for region in self.p_regions]
    return status

  def p_exit(self, e):
    status = return_status.HANDLED
    [region.dispatch(Event(signal=signals.region_exit)) for region in self.p_regions]
    #for region in self.p_regions:
    #  spy_lines = region.spy()
    #  for line in spy_lines:
    #    self.scribble("{}: {}".format(region.name, line))
    #  region.clear_spy()
    return status

  def p_p_final(self, e):
    status = self.trans(self.some_other_state)
    return status

  def p_to_outer(self, e):
    status = self.trans(self.outer_state)
    return status

  def some_other_state_entry_signal(self, e):
    status = return_status.HANDLED
    return status

if __name__ == '__main__':
  example = XmlChart('parallel', live_spy=True)
  example.start_at(example.outer_state)
  time.sleep(0.1)
  example.post_fifo(Event(signal=signals.to_p))
  time.sleep(0.1)
  example.post_fifo(Event(signal=signals.e4))
  time.sleep(0.1)
  example.post_fifo(Event(signal=signals.e1))
  time.sleep(0.1)
  example.post_fifo(Event(signal=signals.to_outer))
  time.sleep(0.1)
  #example.post_fifo(Event(signal=signals.to_p))
  #time.sleep(0.1)
  #example.post_fifo(Event(signal=signals.to_outer))
  #time.sleep(0.1)
  time.sleep(100.1)
