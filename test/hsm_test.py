from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import reflect, Hsm

def state_example(chart, e):
  '''A very simple example state'''

  status = ReturnStatus.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = ReturnStatus.HANDLED

  elif(e.signal == signals.INIT_SIGNAL):
    status = ReturnStatus.HANDLED

  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)

  else:
    status = ReturnStatus.SUPER

  return status

def init_test_d1(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED

  return (chart.top, return_status.RET_TRAN)

def init_test_d2(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED

  return (init_test_d1, return_status.RET_TRAN)

def init_test_d3(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED

  return (init_test_d2, return_status.RET_TRAN)

def init_test_d31(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED

  return (init_test_d3, return_status.RET_TRAN)

def init_test_d32(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED

  return (init_test_d3, return_status.RET_TRAN)

def init_test_d311(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED

  return (init_test_d31, return_status.RET_TRAN)

def test_reflection():
  '''
  Confirm that you can extract the function name from any function calling
  reflect.
  '''
  # Test the function
  def example_function():
    return reflect()
  assert(example_function() == 'example_function')

  # Test how to function would be called in an hsm
  class Nothing(): # could be the Hsm class
    pass

  hsm = Nothing()
  e   = Event(signals.REFLECTION_SIGNAL)
  hsm.reflect = reflect
  assert(state_example(hsm, e) == 'state_example')

def test_init():
  chart = Hsm()
  chart.start_at(init_test_d311)
