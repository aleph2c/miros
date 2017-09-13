from miros.event import StateReturns, Signal, Event

def state_example(chart, event):

  result = StateReturns.RET_UNHANDLED

  if(event.signal == Signal.ENTRY_SIGNAL):
    result = StateReturns.RET_HANDLED

  elif(event.signal == Signal.INIT_SIGNAL):
    result = StateReturns.RET_HANDLED

  else:
    result = StateReturns.RET_SUPER

  return result

