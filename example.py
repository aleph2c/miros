from miros.event import Ret, Signal, Event

def state_example(chart, e):
  '''A very simple example state'''

  r = Ret.UNHANDLED

  if(e.signal == Signal.ENTRY_SIGNAL):
    r = Ret.HANDLED

  elif(e.signal == Signal.INIT_SIGNAL):
    r = Ret.HANDLED

  else:
    r = Ret.SUPER

  return r

