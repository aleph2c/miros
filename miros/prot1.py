from event import Event, signals, ReturnCodes

if '__main__' == __name__:
  state_returns = ReturnCodes()
  state_returns.append("MARY")
  state_returns.append("BOB")
  print(state_returns["MARY"])
  print(state_returns["MARY"])

  event = Event("MARY", payload="nothing")

  #ReturnCodes = ReturnCodes.append("MARY")

