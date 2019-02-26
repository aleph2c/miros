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

  def _write(self, string):
    '''the default write behavior; do nothing let the wrappers control the behavior'''
    pass

class Mode(HsmWithQueues):
  '''Mode is an HsmWithQueues without a thread.  To have its event processor respond to
  events, you will have to use its ``dispatch`` method.

  The Mode object contains function wrappers (decorators) which can control the
  write functionality of the ExampleStatechart object and the post_action
  functionality of the HsmTester thread.  The write functionality will change
  the behavior of the ``write`` calls seen in the ExampleStatechart HSM.  The
  post_action functionality can output instrumentation results or even terminate
  the program.

  The wrappers are just object attributes that are set by the attached HSM; mode
  control.
  '''

  def __init__(self, name):
    super().__init__(name)
    self.write_wrapper = Mode._write
    self.post_action_wrapper = Mode._no_instrumentation

  @staticmethod
  def _write(other, fn):
    '''ExampleStatechart write decorator: write output to terminal

    **Note**:
       Wraps the empty _write function of the example state chart object, giving
       it its true write functionality based on the mode of operation.

       | ``other`` (ActiveObject): example state chart
       | ``fn`` (type1): our main chart's _write method

    '''
    def write(string):
      print(string, end=';')
      fn(string)
    return write

  @staticmethod
  def _muted_write(other, fn):
    '''ExampleStatechart write decorator: write nothing from example state chart 

    **Note**:
       Wraps the empty _write function of the example state chart object, giving
       it its true write functionality based on the mode of operation.

       | ``other`` (ActiveObject): example state chart
       | ``fn`` (type1): our main chart's _write method

    '''
    def write(string):
      fn(string)
    return write

  @staticmethod
  def _scribble(other, fn):
    '''ExampleStatechart write decorator: write directly into the example state
    chart's spy instrumentation stream using its scribble method

    **Note**:
       Wraps the empty _write function of the example state chart object, giving
       it its true write functionality based on the mode of operation.

       | ``other`` (ActiveObject): example state chart
       | ``fn`` (type1): our main chart's _write method

    '''
    def write(string):
      other.scribble("write('{}')".format(string))
      fn(string)
    return write
    
  @staticmethod
  def _no_instrumentation(other, fn):
    '''HsmTester post_action decorator: output no instrumentation, clear both
    instrumentation streams

    **Note**:
       Wraps the empty _post_action function of the HsmTester thread, this
       allows us to write instrumentation, clear instrumenation buffers or even
       terminate the program. (see above for this wrapper's purpose)

       | ``other`` (Thread): hsm tester thread
       | ``fn`` (type1): hsm tester thread's _post_action function

    '''
    def post_action():
      '''don't write instrumentation after transitions are complete, but clear the
         instrumenation buffers'''
      other.chart.clear_trace()
      other.chart.clear_spy()
    return post_action

  @staticmethod
  def _trace(other, fn):
    '''HsmTester post_action decorator: output trace instrumentation, clear both
    instrumentation streams

    **Note**:
       Wraps the empty _post_action function of the HsmTester thread, this
       allows us to write instrumentation, clear instrumenation buffers or even
       terminate the program. (see above for this wrapper's purpose)

       | ``other`` (Thread): hsm tester thread
       | ``fn`` (type1): hsm tester thread's _post_action function

    '''
    def post_action():
      trace = other.chart.trace()
      if trace == '\n':
        print("", end='')
      else:
        print(trace[1:-1], end='')
      other.chart.clear_trace()
      other.chart.clear_spy()
    return post_action

  @staticmethod
  def _spy(other, fn):
    '''HsmTester post_action decorator: output spy instrumentation, clear both
    instrumentation streams

    **Note**:
       Wraps the empty _post_action function of the HsmTester thread, this
       allows us to write instrumentation, clear instrumenation buffers or even
       terminate the program. (see above for this wrapper's purpose)

       | ``other`` (Thread): hsm tester thread
       | ``fn`` (type1): hsm tester thread's _post_action function

    '''
    def post_action():
      print("\n"+"- "*35)
      for item in other.chart.spy():
        print(item)
      print("- "*35, end='')
      other.chart.clear_trace()
      other.chart.clear_spy()
    return post_action

  @staticmethod
  def _terminate(other, fn):
    '''HsmTester post_action decorator: clear the thread event, causing the main
    program to exit, stop the chart's thread, then print 'Terminate' so user
    knows they have shut down the program.

    **Note**:
       Wraps the empty _post_action function of the HsmTester thread, this
       allows us to write instrumentation, clear instrumenation buffers or even
       terminate the program. (see above for this wrapper's purpose)

       | ``other`` (Thread): hsm tester thread
       | ``fn`` (type1): hsm tester thread's _post_action function

    '''
    def post_action():
      other.thread_event.clear()
      other.chart.stop()
      print ("Terminating")
    return post_action

class HsmTester(Thread):
  '''Creates the ExampleStatechart object, attach it to it's HSM, then
  dispatches the user input to the ExampleStatechart's HSM.'''

  def __init__(self, chart):
    super().__init__()
    self.chart = chart
    self.thread_event = ThreadEvent()
    self.signal_names = 'ABCDEFGHIMT'
    self.post_action = self._post_action

    self.thread_event.set()

  def _post_action(self):
    '''the default post_action; do nothing let the wrappers control the behavior'''
    pass

  def run(self):

    def print_signal_char_on_windows(character):
      print("- "*35)
      print("{} {}".format("posting", character))

    def print_signal_char(character):
      # keeps input and output on oneline (looks better)
      print("\033[F{}:{}  ".format(self.chart.mode.state_name[0], character), end='')

    print_signal = print_signal_char_on_windows \
      if sys.platform == 'win32' else print_signal_char

    while self.thread_event.is_set():

      # indicate the mode state with one character in the signal input prompt
      character = input("\n{}:".format(self.chart.mode.state_name[0]))
      character = character.upper()

      print_signal(character)

      if len(character) != 1 or character not in self.signal_names: 
        print("Event not defined.") 
      else:
        self.chart.post_fifo(Event(signal=character))

      # give the statechart's thread a moment to catch up
      time.sleep(0.01)

      # after the statemachine has finished its work we may want to look
      # at its instrumentation output (depending on the mode of operation),
      # or even terminate the program.
      self.post_action = self.chart.mode.post_action_wrapper(self, self._post_action)
      self.post_action()
      time.sleep(0.1)

def mode_control(mode, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.INIT_SIGNAL):
    status = mode.trans(no_instrumentation_mode)
  elif(e.signal == signals.T):
    status = mode.trans(terminate)
  else:
    mode.temp.fun = mode.top
    status = return_status.SUPER
  return status

def no_instrumentation_mode(mode, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    mode.write_wrapper = Mode._write
    mode.post_action_wrapper = Mode._no_instrumentation
    status = return_status.HANDLED
  elif(e.signal == signals.M):
    status = mode.trans(trace_mode)
  else:
    mode.temp.fun = mode_control
    status = return_status.SUPER
  return status

def trace_mode(mode, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    mode.write_wrapper = Mode._muted_write
    mode.post_action_wrapper = Mode._trace
    status = return_status.HANDLED
  elif(e.signal == signals.M):
    status = mode.trans(spy_mode)
  else:
    mode.temp.fun = mode_control
    status = return_status.SUPER
  return status

def spy_mode(mode, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    mode.write_wrapper = Mode._scribble
    mode.post_action_wrapper = Mode._spy
    status = return_status.HANDLED
  elif(e.signal == signals.M):
    status = mode.trans(no_instrumentation_mode)
  else:
    mode.temp.fun = mode_control
    status = return_status.SUPER
  return status

def terminate(mode, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    mode.post_action_wrapper = Mode._terminate
  else:
    mode.temp.fun = mode_control
    status = return_status.SUPER
  return status

@spy_on
def s(me, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    me.mode = Mode('mode')
    me.mode.start_at(mode_control)
    me.write = me.mode.write_wrapper(me, me._write)
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
    me.write = me.mode.write_wrapper(me, me._write)
    me.write('s-M')
    status = return_status.HANDLED
  elif(e.signal == signals.T):
    me.mode.dispatch(e)
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
  
