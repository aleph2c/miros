from miros.event import StateReturns, Signal, Event

def state_example(chart, e):

  status = StateReturns.RET_UNHANDLED

  if(e.signal == Signal.ENTRY_SIGNAL):
    status = StateReturns.RET_HANDLED

  elif(e.signal == Signal.INIT_SIGNAL):
    status = StateReturns.RET_HANDLED

  else:
    status = StateReturns.RET_SUPER

  return status

