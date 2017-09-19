import pytest
from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import reflect, Hsm

def state_example(chart, e):
  '''A very simple example state'''

  status = ReturnStatus.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = ReturnStatus.HANDLED

  if(e.signal == signals.INIT_SIGNAL):
    pass

  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)

  else:
    status = ReturnStatus.SUPER

  return status

@pytest.mark.reflect
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

