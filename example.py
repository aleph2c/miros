from miros.event import ReturnStatus, signals, Event

def state_example(chart, e):
  '''A very simple example state'''

  status = ReturnStatus.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = ReturnStatus.HANDLED

  elif(e.signal == signals.INIT_SIGNAL):
    status = ReturnStatus.HANDLED

  else:
    status = ReturnStatus.SUPER

  return status

