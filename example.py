from miros.event import ReturnStatus, signals, Event
from miros.hsm   import reflect


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
    status = reflect()
  else:
    status = ReturnStatus.SUPER

  return status


ReturnStatus()


class Nothing():
  pass


print(state_example(Nothing(), Event(signals.REFLECTION_SIGNAL)))

