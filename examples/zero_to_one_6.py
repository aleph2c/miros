import re
import sys
import time
from miros import Event
from miros import spy_on
from miros import signals
from datetime import datetime
from miros import ActiveObject
from miros import return_status
from collections import namedtuple

BuzzSpec = namedtuple(
  "BuzzSpec", ['buzz_times'])

class ToasterOven(ActiveObject):
  
  TOAST_TIME_IN_SEC = 10
  BAKE_TIME_IN_SEC = 20
  PRE_TIME_SEC = 1
  DONE_BUZZ_PERIOD_SEC = 0.5
  
  def __init__(self, name, 
    toast_time_in_sec=None,
    bake_time_in_sec=None,
    get_ready_sec=None,
    done_buzz_period_sec=None):

    super().__init__(name)
  
    if toast_time_in_sec is None:
      toast_time_in_sec = ToasterOven.TOAST_TIME_IN_SEC
    if bake_time_in_sec is None:
      bake_time_in_sec = ToasterOven.BAKE_TIME_IN_SEC
    if get_ready_sec is None:
      get_ready_sec = ToasterOven.PRE_TIME_SEC
    if done_buzz_period_sec is None:
      done_buzz_period_sec = ToasterOven.DONE_BUZZ_PERIOD_SEC
      
    self.toast_time_in_sec = toast_time_in_sec
    self.bake_time_in_sec = bake_time_in_sec
    self.get_ready_sec = get_ready_sec
    self.done_buzz_period_sec = done_buzz_period_sec
    self.history = None

  def light_on(self):
    # call to your hardware's light_on driver
    pass

  def light_off(self):
    # call to your hardware's light_off driver
    pass
    
    
  def heater_on(self):
    # call to your hardware's heater on driver
    pass

  def heater_off(self):
    # call to your hardware's heater off driver
     pass
    
  def buzz(self):
    # call to your hardware's buzzer
    pass

  def cook_time(self, time_in_sec):
    '''Produce ``Get_Ready`` and ``Done`` one-shot events with their respect Buzz
       specifications.

    **Note**:
       This code is used in both the baking and toasting states, so it was moved
       into the ToasterOven class to avoid repeating code in the statemachine.

    **Args**:
       | ``time_in_sec`` (float): the cooking time in seconds
    '''
    get_ready_sec = time_in_sec - self.get_ready_sec

    self.post_fifo(
      Event(signal=signals.Get_Ready, payload=BuzzSpec(buzz_times=1)),
      times=1,
      period=get_ready_sec,
      deferred=True)

    self.post_fifo(
      Event(signal=signals.Done, payload=BuzzSpec(buzz_times=2)),
      times=1,
      period=time_in_sec,
      deferred=True)

  
class ToasterOvenMock(ToasterOven):

  def __init__(self, 
    name, 
    toast_time_in_sec=None,
    bake_time_in_sec=None,
    get_ready_sec=None,
    done_buzz_period_sec=None):

    super().__init__(name,
      toast_time_in_sec,
      bake_time_in_sec,
      get_ready_sec,
      done_buzz_period_sec)
   
  @staticmethod
  def prepend_trace_timestamp(string):
    '''Prepend the trace-style timestamp in front of a string

    **Args**:
       | ``string`` (str): a string you would like timestamped

    **Returns**:
       (string): datetime stamp prepended to input string

    **Example(s)**:
      
    .. code-block:: python

      ToasterOven.prepend_trace_timestamp("example")
      # => [2019-02-04 06:37:04.542346] example

    '''
    return "[{}] {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), string)

  @staticmethod
  def get_100ms_from_timestamp(timestamp_string):
    '''Get the 100ms part of a timestamp provided in the trace style

    **Args**:
       | ``timestamp_string`` (str): string with prepended timestamp

    **Returns**:
       | (string): The first three digits after the seconds decimal point
       | (None): If no match

    **Example(s)**:
      
    .. code-block:: python

      get_my_ms =  "[2019-02-04 06:37:04.542346] example"
      ToasterOven.prepend_trace_timestamp(get_my_ms) # => 542

    '''
    pattern = re.compile(r'\[.+\.([0-9]{3}).+\]')
    try:
      result = pattern.search(timestamp_string).group(1)
    except:
      result = None
    return result

  @staticmethod
  def time_difference(time_1_string, time_2_string, modulo_base=None):
    '''Return the time difference between to ms readings of a timestamp

    **Args**:
       | ``time_1_string`` (str|int): part of a timestamp
       | ``time_2_string`` (str|int): part of a timestamp
       | ``modulo_base`` (int):  defaults to 1000, allows for time raps

    **Returns**:
       (int): (int(time_1_string) - int(time_2_string)) % modulo_base

    **Example(s)**:
      
    .. code-block:: python
      
      # typical usage
      ToasterOvenMock.time_difference('500', '300') #=> 200
      ToasterOvenMock.time_difference('500', '300', modulo_base=1000) #=> 200

      # time wrap
      # time_1_string from 1.010
      # time_2_string from 0.790
      ToasterOvenMock.time_difference('010', '790') #=> 200

    '''
    if modulo_base is None:
      modulo_base = 1000
    time_1 = int(time_1_string)
    time_2 = int(time_2_string)
    diff = time_2 - time_1 if time_1 <= time_2 else (time_2 - time_1) % modulo_base
    return diff

  @staticmethod
  def instrumentation_line_of_match(spy_or_trace, string):
    '''Get the line from a instrumentation collection

    **Args**:
       | ``spy_or_trace`` (str|list): instrumentation output
       | ``string`` (str): thing to search for in the instrumentation output

    **Returns**:
       (str): part of the instrumentation that matches the string

    **Example(s)**:
      
    .. code-block:: python
       
      spy_of_trace = """
        [2019-02-09 10:50:07.784989] [oven] e->start_at() top->off
        [2019-02-09 10:50:07.785844] [oven] e->Toasting() off->toasting"""

      ToasterOvenMock.instrumentation_line_of_match(
        spy_of_trace, "Toasting") 
      # => '[2019-02-09 10:50:07.785844] [oven] e->Toasting() off->toasting'

    '''
    result = None
    i_list = spy_or_trace.split("\n") if type(spy_or_trace) is str else spy_or_trace
    pattern = re.compile(string)
    for line in i_list:
      if pattern.search(line):
        result = line
        break
    return result

  def scribble(self, string):
    '''prepend a scribble string with the trace instrumentation style timestamp

    **Args**:
       | ``string`` (str): String to add to the scribble

    **Example(s)**:
      
    .. code-block:: python

       oven = ToasterOvenMock(name='oven')

       # calls ActiveObject's scribble with something like:
       # "[2019-02-09 10:50:07.785844] buzz"
       oven.scribble("buzz") 

    '''
    super().scribble(ToasterOvenMock.prepend_trace_timestamp(string))
    
  def light_on(self):
    self.scribble("light_on")

  def light_off(self):
    self.scribble("light_off")

  def heater_on(self):
    self.scribble("heater_on")

  def heater_off(self):
    self.scribble("heater_off")
    
  def buzz(self):
    if self.live_spy == False:
      output = ToasterOvenMock.prepend_trace_timestamp("buzz")
      print(output)
    self.scribble("buzz")
    
    
@spy_on
def common_features(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.Buzz):
    oven.buzz()
    status = return_status.HANDLED
  else:
    oven.temp.fun = oven.top
    status = return_status.SUPER
  return status

@spy_on
def door_closed(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.light_off()
    status = return_status.HANDLED
  elif(e.signal == signals.Baking):
    status = oven.trans(baking)
  elif(e.signal == signals.Toasting):
    status = oven.trans(toasting)
  elif(e.signal == signals.INIT_SIGNAL):
    status = oven.trans(off)
  elif(e.signal == signals.Off):
    status = oven.trans(off)
  elif(e.signal == signals.Door_Open):
    status = oven.trans(door_open)
  else:
    oven.temp.fun = common_features
    status = return_status.SUPER
  return status

@spy_on
def heating(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.heater_on()
    status = return_status.HANDLED
  elif(e.signal == signals.Get_Ready):
    oven.post_fifo(Event(signal=signals.Buzz),
      times=e.payload.buzz_times,
      period=oven.done_buzz_period_sec,
      deferred=False)
    status = return_status.HANDLED
  elif(e.signal == signals.Done):
    oven.post_fifo(Event(signal=signals.Buzz),
      times=e.payload.buzz_times,
      period=oven.done_buzz_period_sec,
      deferred=False)
    status = oven.trans(off)
  elif(e.signal == signals.EXIT_SIGNAL):
    oven.heater_off()
    status = return_status.HANDLED
  else:
    oven.temp.fun = door_closed
    status = return_status.SUPER
  return status

@spy_on
def baking(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.history = baking
    oven.cook_time(oven.bake_time_in_sec)
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    oven.cancel_events(Event(signal=signals.Done))
    oven.cancel_events(Event(signal=signals.Get_Ready))
    status = return_status.HANDLED
  else:
    oven.temp.fun = heating
    status = return_status.SUPER
  return status

@spy_on
def toasting(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.history = toasting
    oven.cook_time(oven.toast_time_in_sec)
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    oven.cancel_events(Event(signal=signals.Done))
    oven.cancel_events(Event(signal=signals.Get_Ready))
    status = return_status.HANDLED
  else:
    oven.temp.fun = heating
    status = return_status.SUPER
  return status

@spy_on
def off(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.history = off
    status = return_status.HANDLED
  else:
    oven.temp.fun = door_closed
    status = return_status.SUPER
  return status

@spy_on
def door_open(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    oven.light_on()
  elif(e.signal == signals.Door_Close):
    status = oven.trans(oven.history)
  else:
    oven.temp.fun = common_features
    status = return_status.SUPER
  return status


if __name__ == '__main__':

  #toast_time = 0.1
  #bake_time = 0.2
  #get_ready_sec = 0.05
  #done_buzz_period_sec = 0.01

  #oven = ToasterOvenMock(
  #  name="oven",
  #  toast_time_in_sec=toast_time,
  #  bake_time_in_sec=bake_time,
  #  get_ready_sec=get_ready_sec,
  #  done_buzz_period_sec=done_buzz_period_sec)
  #oven.live_trace = True
  #oven.start_at(off)
  #oven.post_fifo(Event(signal=signals.Toasting))
  #time.sleep(2)
  #oven.post_fifo(Event(signal=signals.Toasting))

  import re
  from miros import stripped

  def trace_through_all_states():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Bake something
    oven.post_fifo(Event(signal=signals.Baking))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    # Toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    # Open the door
    oven.post_fifo(Event(signal=signals.Door_Open))
    # Close the door
    oven.post_fifo(Event(signal=signals.Door_Close))
    time.sleep(0.01)
    return oven.trace()

  def spy_on_light_on():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Open the door to turn on the light
    oven.post_fifo(Event(signal=signals.Door_Open))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())

  def spy_on_light_off():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())
    
  def spy_on_buzz():
    oven = ToasterOvenMock(name="oven")
    oven.start_at(door_closed)
    # Send the buzz event
    oven.post_fifo(Event(signal=signals.Buzz))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())

  def spy_on_heater_on():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    oven.post_fifo(Event(signal=signals.Toasting))
    time.sleep(0.02)
    # turn our array into a paragraph
    return "\n".join(oven.spy())

  def spy_on_heater_off():
    oven = ToasterOvenMock(name="oven")
    # The light should be turned off when we start
    oven.start_at(door_closed)
    oven.post_fifo(Event(signal=signals.Toasting))
    oven.clear_spy()
    oven.post_fifo(Event(signal=signals.Off))
    time.sleep(0.01)
    # turn our array into a paragraph
    return "\n".join(oven.spy())

  def test_buzz_timing():
    # Test in the range of ms so we don't have to wait around
    toast_time, bake_time = 0.1, 0.2
    get_ready_sec = 0.01
    done_buzz_period_sec = 0.03

    oven = ToasterOvenMock(
      name="oven",
      toast_time_in_sec=toast_time,
      bake_time_in_sec=bake_time,
      get_ready_sec=get_ready_sec,
      done_buzz_period_sec=done_buzz_period_sec)

    # start our oven in the door_closed state
    oven.start_at(door_closed)

    # Buzz timing testing specifications and helper functions
    TS = namedtuple('TargetAndToleranceSpec', ['desc', 'offset', 'tolerance'])

    def make_test_spec(cook_time_sec, get_ready_sec, done_buzz_period_sec, tolernance_in_ms=3):
      "create as specification where define everything in ms"
      ts = [
        TS(desc="get ready buzz",
          offset=1000*(cook_time_sec-get_ready_sec),
          tolerance=tolernance_in_ms),
        TS(desc="first done buzz" , 
          offset=1000*(cook_time_sec), 
          tolerance=tolernance_in_ms),
        TS(desc="second done buzz", 
          offset=1000*(cook_time_sec+done_buzz_period_sec), 
          tolerance=tolernance_in_ms)]
      return ts

    def test_buzz_events(test_type, start_time, spec, buzz_times):
      for (desc, offset, tolerance), buzz_time in zip(spec, buzz_times):

        # only keep track of ms, allow for wrapping of time
        bottom_bound = (start_time+offset-tolerance) % 1000
        top_bound = (start_time+offset+tolerance) % 1000
        
        # allow for wrapping of time
        if bottom_bound > top_bound:
          bottom_bound -= 1000
        try:
          assert(bottom_bound <= float(buzz_time) <= top_bound)
        except:
          print("FAILED: testing {} {}".format(test_type, desc))
          print("{} <= {} <= {}".format(bottom_bound, buzz_time, top_bound))

    toasting_buzz_test_spec = make_test_spec(toast_time, get_ready_sec, done_buzz_period_sec)

    # Toast something
    oven.post_fifo(Event(signal=signals.Toasting))
    time.sleep(1)
    trace_line = ToasterOvenMock.instrumentation_line_of_match(oven.trace(), "Toasting")
    toasting_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(trace_line))
    buzz_times = [int(ToasterOvenMock.get_100ms_from_timestamp(line)) for
                  line in re.findall(r'\[.+\] buzz', "\n".join(oven.spy()))]
    test_buzz_events('toasting', toasting_time_ms, toasting_buzz_test_spec, buzz_times)

    # clear the spy and trace logs for another test
    oven.clear_spy()
    oven.clear_trace()

    baking_buzz_test_spec = make_test_spec(bake_time, get_ready_sec, done_buzz_period_sec)

    # Bake something
    oven.post_fifo(Event(signal=signals.Baking))
    time.sleep(1)
    oven.post_fifo(Event(signal=signals.Baking))
    trace_line = ToasterOvenMock.instrumentation_line_of_match(oven.trace(), "Baking")
    baking_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(trace_line))
    buzz_times = [int(ToasterOvenMock.get_100ms_from_timestamp(line)) for
                  line in re.findall(r'\[.+\] buzz', "\n".join(oven.spy()))]
    test_buzz_events('baking', baking_time_ms, baking_buzz_test_spec, buzz_times)

  # Confirm our graph's structure
  trace_target = """
  [2019-02-04 06:37:04.538413] [oven] e->start_at() top->off
  [2019-02-04 06:37:04.540290] [oven] e->Door_Open() off->door_open
  [2019-02-04 06:37:04.540534] [oven] e->Door_Close() door_open->off
  [2019-02-04 06:37:04.540825] [oven] e->Baking() off->baking
  [2019-02-04 06:37:04.541109] [oven] e->Door_Open() baking->door_open
  [2019-02-04 06:37:04.541393] [oven] e->Door_Close() door_open->baking
  [2019-02-04 06:37:04.541751] [oven] e->Toasting() baking->toasting
  [2019-02-04 06:37:04.542083] [oven] e->Door_Open() toasting->door_open
  [2019-02-04 06:37:04.542346] [oven] e->Door_Close() door_open->toasting
  """

  with stripped(trace_target) as stripped_target, \
       stripped(trace_through_all_states()) as stripped_trace_result:
    
    for target, result in zip(stripped_target, stripped_trace_result):
      assert(target == result)

  # Confirm the our statemachine is triggering the methods we want when we want them
  assert re.search(r'light_off', spy_on_light_off())

  # Confirm our light turns on
  assert re.search(r'light_on', spy_on_light_on())

  # Confirm the heater turns on
  assert re.search(r'heater_on', spy_on_heater_on())

  # Confirm the heater turns off
  assert re.search(r'heater_off', spy_on_heater_off())

  # Confirm our buzzer works
  assert re.search(r'buzz', spy_on_buzz())

  # Confirm the buzzer timing features
  test_buzz_timing()
