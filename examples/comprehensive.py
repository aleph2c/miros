import sys
import time
from miros import pp
from miros import Event
from miros import spy_on
from miros import signals
from threading import Thread
from miros import ActiveObject
from miros import HsmWithQueues
from miros import return_status
from threading import Event as ThreadEvent

class ExampleStatechart(ActiveObject):

  def __init__(self, name):
    super().__init__(name)
    self.foo = None
    self.mode = InstrumentationMode('mode')
    self.mode.start_at(naked_mode)
    self.write = self.mode.wrapper(self, self._write)

  def _write(self, string):
    pass

class InstrumentationMode(HsmWithQueues):

  def __init__(self, name):
    super().__init__(name)
    self.wrapper = InstrumentationMode._write

  @staticmethod
  def _write(other, fn):
    def write(string):
      print(string, end=';')
      fn(string)
    return write

  @staticmethod
  def _muted_write(other, fn):
    def write(string):
      fn(string)
    return write

  @staticmethod
  def _scribble(other, fn):
    def write(string):
      other.scribble(string)
      fn(string)
    return write

class HsmTester(Thread):

  def __init__(self, chart):
    super().__init__()
    self.thread_event = ThreadEvent()
    self.chart = chart
    def make_post_function(signal_name):
      def post_event():
        self.chart.post_fifo(Event(signal=signal_name))
      def quit():
        self.thread_event.clear()
      return quit if signal_name == 'T' else post_event
    self.thread_event.set()
    self.post_functions = {
      character:make_post_function(character) for character in 'ABCDEFGHIMT'}

  def run(self):

    def print_signal_char_on_windows(character):
      print("{}:{}".format(character))

    def print_signal_char(character):
      print("\033[F{}:{}  ".format(self.chart.mode.state_name[0], character), end='')

    pfn = print_signal_char_on_windows if sys.platform == 'win32' else print_signal_char

    while self.thread_event.is_set():
      self.chart.clear_spy()
      self.chart.clear_trace()
      character = input("\n{}:".format(self.chart.mode.state_name[0]))
      character = character.upper()
      pfn(character)  # print the signal we are going to send to the terminal
      if len(character) != 1 or character not in self.post_functions: 
        print("Event not defined.") 
      else:
        self.post_functions[character]()  # call the post function with our event
      time.sleep(0.01) # give the statechart's thread a moment to catch up

      if self.chart.mode.state_name == 'trace_mode':
        trace = self.chart.trace()
        if trace == '\n':
          print("", end='')
        else:
          print(trace[1:-1], end='')

      elif self.chart.mode.state_name == 'spy_mode':
        print("\n"+"-"*78)
        for item in self.chart.spy():
          print(item)
        print("-"*78)
      time.sleep(0.1)

    print ("Terminating")
    self.chart.stop()  # not needed, active object threads are daemonic

def naked_mode(mode, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    mode.wrapper = InstrumentationMode._write
    status = return_status.HANDLED
  elif(e.signal == signals.M):
    status = mode.trans(trace_mode)
  else:
    mode.temp.fun = mode.top
    status = return_status.SUPER
  return status

def trace_mode(mode, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    mode.wrapper = InstrumentationMode._muted_write
    status = return_status.HANDLED
  elif(e.signal == signals.M):
    status = mode.trans(spy_mode)
  else:
    mode.temp.fun = mode.top
    status = return_status.SUPER
  return status

def spy_mode(mode, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    mode.wrapper = InstrumentationMode._scribble
    status = return_status.HANDLED
  elif(e.signal == signals.M):
    status = mode.trans(naked_mode)
  else:
    mode.temp.fun = mode.top
    status = return_status.SUPER
  return status

@spy_on
def s(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    me.write('foo = {}'.format(me.foo))
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
  elif(e.signal == signals.M):
    me.mode.dispatch(e)
    me.write = me.mode.wrapper(me, me._write)
    me.write('s-M')
    status = return_status.HANDLED
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

if __name__ == "__main__":
  me = ExampleStatechart(name='me')
  me.foo = 0;
  me.start_at(s2)  
  hsm_tester = HsmTester(me)
  hsm_tester.start()
  
