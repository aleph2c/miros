import pytest
from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import reflect, Hsm

################################################################################
#                                 Init test 1                                  #
################################################################################
def init_test_1_d1(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
    print( "entering {}".format(reflect(chart,e)))
  if(e.signal == signals.INIT_SIGNAL):
    pass
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.temp.fun = chart.top
    status = return_status.SUPER

  return status

def init_test_1_d2(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    print( "entering {}".format(reflect(chart,e)))
    status = return_status.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    pass
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.temp.fun = init_test_1_d1
    status = return_status.SUPER

  return status

def init_test_1_d3(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    print( "entering {}".format(reflect(chart,e)))
    status = return_status.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    pass
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.temp.fun = init_test_1_d2
    status = return_status.SUPER

  return status

def init_test_1_d31(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    print( "entering {}".format(reflect(chart,e)))
    status = return_status.HANDLED

  if(e.signal == signals.INIT_SIGNAL):
    status = chart.trans(init_test_1_d311)

  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)

  else:
    chart.temp.fun = init_test_1_d3
    status = return_status.SUPER

  return status

def init_test_1_d32(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    print( "entering {}".format(reflect(chart,e)))
    status = return_status.HANDLED
  if(e.signal == signals.INIT_SIGNAL):
    pass
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.temp.fun = init_test_1_d3
    status = return_status.SUPER

  return status

def init_test_1_d311(chart, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    print( "entering {}".format(reflect(chart,e)))
    status = return_status.HANDLED

  if(e.signal == signals.INIT_SIGNAL):
    pass
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.temp.fun = init_test_1_d31
    status = return_status.SUPER

  return status

@pytest.mark.init
def test_init_test_1():
  chart = Hsm()
  print()
  chart.start_at(init_test_1_d311)

@pytest.mark.init
def test_init_test_2():
  chart = Hsm()
  print()
  chart.start_at(init_test_1_d31)
