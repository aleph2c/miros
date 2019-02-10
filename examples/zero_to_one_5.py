import re
import time
from miros import Event
from miros import spy_on
from miros import signals
from datetime import datetime
from miros import ActiveObject
from miros import return_status

class ToasterOven(ActiveObject):
  
  TOAST_TIME_IN_SEC = 10
  BAKE_TIME_IN_SEC = 20
  
  def __init__(self, name, toast_time_in_sec=None, bake_time_in_sec=None):
    super().__init__(name)
  
    if toast_time_in_sec is None:
      toast_time_in_sec = ToasterOven.TOAST_TIME_IN_SEC
    if bake_time_in_sec is None:
      bake_time_in_sec = ToasterOven.BAKE_TIME_IN_SEC
      
    self.toast_time_in_sec = toast_time_in_sec
    self.bake_time_in_sec = bake_time_in_sec
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
  
class ToasterOvenMock(ToasterOven):
  def __init__(self, name, toast_time_in_sec=None, bake_time_in_sec=None):
    super().__init__(name, toast_time_in_sec, bake_time_in_sec)
   
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
    self.scribble("buzz")
    
    
@spy_on
def common_features(oven, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.Buzz):
    print("buzz")
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
    oven.post_lifo(
      Event(signal=signals.Buzz),
      times=1,
      period=oven.bake_time_in_sec,
      deferred=True
    )
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    oven.cancel_events(
      Event(signal=signals.Buzz)
    )
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
    oven.post_lifo(
      Event(signal=signals.Buzz),
      times=1,
      period=oven.toast_time_in_sec,
      deferred=True
    )
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    oven.cancel_events(
      Event(signal=signals.Buzz)
    )
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

def test_toaster_buzz_one_shot_timing():
  # set toasting time to 100 ms
  oven = ToasterOvenMock(name="oven", toast_time_in_sec=0.100)
  oven.start_at(door_closed)
  oven.post_fifo(Event(signal=signals.Toasting))

  time.sleep(0.104)  

  trace_line = ToasterOvenMock.instrumentation_line_of_match(oven.trace(), "Toasting")
  toasting_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(trace_line))

  spy_line = ToasterOvenMock.instrumentation_line_of_match(oven.spy(), "buzz")
  buzz_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(spy_line))

  delay_in_ms = ToasterOvenMock.time_difference(toasting_time_ms, buzz_time_ms)

  # allow 2 ms of jitter
  assert(98 <= delay_in_ms <= 102)

def test_baking_buzz_one_shot_timing():
  # set toasting time to 200 ms
  oven = ToasterOvenMock(name="oven", bake_time_in_sec=0.200)
  oven.start_at(door_closed)
  oven.post_fifo(Event(signal=signals.Baking))

  time.sleep(0.205)

  trace_line = ToasterOvenMock.instrumentation_line_of_match(oven.trace(), "Baking")
  baking_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(trace_line))

  spy_line = ToasterOvenMock.instrumentation_line_of_match(oven.spy(), "buzz")
  buzz_time_ms = int(ToasterOvenMock.get_100ms_from_timestamp(spy_line))

  delay_in_ms = ToasterOvenMock.time_difference(baking_time_ms, buzz_time_ms)

  # allow 2 ms of jitter
  assert(198 <= delay_in_ms <= 202)

# Test time features (one-shots etc)
test_toaster_buzz_one_shot_timing()
test_baking_buzz_one_shot_timing()
