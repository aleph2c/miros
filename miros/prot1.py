from event import Event, signals, StateReturns

if '__main__' == __name__:
  state_returns = StateReturns()
  state_returns.append("MARY")
  state_returns.append("BOB")
  print(state_returns["MARY"])
  print(state_returns["MARY"])

  event = Event("MARY", payload="nothing")

  #StateReturns = StateReturns.append("MARY")

