import sys
import time
from miros import pp
from miros import Event
from miros import signals
from threading import Thread
from miros import ActiveObject
from miros import return_status
from threading import Event as ThreadEvent

class ExampleStatechart(ActiveObject):

  def __init__(self, name):
    super().__init__(name)
    self.foo = 0

  def write(self, string):
    try:
      print(string, end=';')
    except:
      pass

class HsmTester(Thread):

  def __init__(self, chart):
    super().__init__()
    self.thread_event = ThreadEvent()
    self.chart = chart
    def make_post_function(signal_name):
      def post_event():
        chart.post_fifo(Event(signal=signal_name))
      def quit():
        self.thread_event.clear()
      return quit if signal_name == 'T' else post_event
    self.thread_event.set()
    self.post_functions = {
      character:make_post_function(character) for character in 'ABCDEFGHIT'}

  def run(self):
    def print_signal_char_on_windows(character):
      '''print a character in dos'''
      print(" {}".format(character))
    def print_signal_char(character):
      '''print a character on the same line that we received input in linux'''
      print("\033[F:{}  ".format(character), end='')  # print on the same line
    pfn = print_signal_char_on_windows if sys.platform == 'win32' else print_signal_char
    while self.thread_event.is_set():
      character = input("\n:")
      character = character.upper()
      pfn(character)  # print the signal we are going to send to the terminal
      if len(character) != 1 or character not in self.post_functions: 
        print("Event not defined.") 
      else:
        self.post_functions[character]()  # call the post function
      time.sleep(0.1)

    pp(self.chart.spy())
    print(self.chart.trace())
    self.chart.stop()  # not needed, active object threads are daemonic

    print ("Terminating")

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

if __name__ == "__main__":
  me = ExampleStatechart(name='me')
  #me.instrumented = False 
  # To Do:
  # when the instrumentation is false, spy() and trace() should output nothing
  # the statechart is currently broke (e, g) if no spy_on and me.instrumented=True (default)
  # add extensive tests based on this chart
  me.foo = 0; me.write('foo = 0')
  me.start_at(s2)  
  #me.post_fifo(Event(signal=signals.E))
  #print("")
  #me.post_fifo(Event(signal=signals.D))
  #print("")
  #time.sleep(1000)
  hsm_tester = HsmTester(me)
  hsm_tester.start()
  
