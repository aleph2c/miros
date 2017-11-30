import time
from miros.hsm import spy_on, pp, state_method_template
from miros.activeobject import ActiveObject
from miros.event import signals, Event, return_status


def example_1():
  @spy_on
  def c(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.INIT_SIGNAL):
      status = chart.trans(c1)
    elif(e.signal == signals.BB):
      status = chart.trans(c)
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

  @spy_on
  def c1(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.A):
      status = chart.trans(c2)
    else:
      status, chart.temp.fun = return_status.SUPER, c
    return status

  @spy_on
  def c2(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.A):
      status = chart.trans(c1)
    else:
      status, chart.temp.fun = return_status.SUPER, c
    return status

  ao = ActiveObject()
  ao.start_at(c2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)  # give your active object a moment to respond
  pp(ao.spy())


def example_2():

  @spy_on
  def tc(chart, e):

    with chart.signal_callback(e, tc) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

  @spy_on
  def tc1(chart, e):

    with chart.signal_callback(e, tc1) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

  @spy_on
  def tc2(chart, e):

    with chart.signal_callback(e, tc2) as fn:
      status = fn(chart, e)

    if(status == return_status.UNHANDLED):
      with chart.parent_callback() as parent:
        status, chart.temp.fun = return_status.SUPER, parent

    return status

  def trans_to_tc(chart, e):
    return chart.trans(tc)

  def trans_to_tc1(chart, e):
    return chart.trans(tc1)

  def trans_to_tc2(chart, e):
    return chart.trans(tc2)

  def do_nothing(chart, e):
    return return_status.HANDLED

  ao = ActiveObject()

  ao.register_signal_callback(tc, signals.BB, trans_to_tc)
  ao.register_signal_callback(tc, signals.ENTRY_SIGNAL, do_nothing)
  ao.register_signal_callback(tc, signals.EXIT_SIGNAL,  do_nothing)
  ao.register_signal_callback(tc, signals.INIT_SIGNAL,  trans_to_tc1)
  ao.register_parent(tc, ao.top)

  ao.register_signal_callback(tc1, signals.A, trans_to_tc2)
  ao.register_signal_callback(tc1, signals.ENTRY_SIGNAL, do_nothing)
  ao.register_signal_callback(tc1, signals.EXIT_SIGNAL,  do_nothing)
  ao.register_signal_callback(tc1, signals.INIT_SIGNAL,  do_nothing)
  ao.register_parent(tc1, tc)

  ao.register_signal_callback(tc2, signals.A, trans_to_tc1)
  ao.register_signal_callback(tc2, signals.ENTRY_SIGNAL, do_nothing)
  ao.register_signal_callback(tc2, signals.EXIT_SIGNAL,  do_nothing)
  ao.register_signal_callback(tc2, signals.INIT_SIGNAL,  do_nothing)
  ao.register_parent(tc2, tc)

  ao.start_at(tc2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  pp(ao.spy())


def example_3():

  # create the specific behavior we want in our state chart
  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  # create the states
  fc  = state_method_template('fc')
  fc1 = state_method_template('fc1')
  fc2 = state_method_template('fc2')

  # build an active object, which has an event processor
  ao = ActiveObject()

  # write the design information into the fc state
  ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  ao.register_signal_callback(fc, signals.INIT_SIGNAL,  trans_to_fc1)
  ao.register_parent(fc, ao.top)

  # write the design information into the fc1 state
  ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  ao.register_signal_callback(fc1, signals.A, trans_to_fc2)
  ao.register_parent(fc1, fc)

  # write the design information into the fc2 state
  ao.register_signal_callback(fc2, signals.A, trans_to_fc1)
  ao.register_parent(fc2, fc)

  # start up the active object what what it does
  ao.start_at(fc2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  pp(ao.spy())

  print(ao.to_code(fc))
  print(ao.to_code(fc1))
  print(ao.to_code(fc2))


def example_4():

  # create the specific behavior we want in our state chart
  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  @spy_on
  def fc(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = trans_to_fc1(chart, e)
    elif(e.signal == signals.BB):
      status = trans_to_fc(chart, e)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

  @spy_on
  def fc1(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.A):
      status = trans_to_fc2(chart, e)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, fc
    return status

  @spy_on
  def fc2(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.A):
      status = trans_to_fc1(chart, e)
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, fc
    return status
  # # create the states
  # fc  = state_method_template('fc')
  # fc1 = state_method_template('fc1')
  # fc2 = state_method_template('fc2')

  # build an active object, which has an event processor
  ao = ActiveObject()

  # write the design information into the fc state
  # ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  # ao.register_signal_callback(fc, signals.INIT_SIGNAL,  trans_to_fc1)
  # ao.register_parent(fc, ao.top)

  # # write the design information into the fc1 state
  # ao.register_signal_callback(fc, signals.BB, trans_to_fc)
  # ao.register_signal_callback(fc1, signals.A, trans_to_fc2)
  # ao.register_parent(fc1, fc)

  # # write the design information into the fc2 state
  # ao.register_signal_callback(fc2, signals.A, trans_to_fc1)
  # ao.register_parent(fc2, fc)

  # start up the active object what what it does
  ao.start_at(fc2)
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  pp(ao.spy())


def example_5():

  from miros.activeobject import Factory

  # the statechart's event callback methods
  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  # Factory is a type of ActiveObject, so it will have it's methods
  chart = Factory('factory_class_example')

  fc = chart.create(state='fc'). \
    catch(signal=signals.B, handler=trans_to_fc). \
    catch(signal=signals.INIT_SIGNAL, handler=trans_to_fc1). \
    to_method()

  fc1 = chart.create(state='fc1'). \
    catch(signal=signals.A, handler=trans_to_fc2). \
    to_method()

  fc2 = chart.create(state='fc2'). \
    catch(signal=signals.A, handler=trans_to_fc1). \
    to_method()

  chart.nest(fc,  parent=None). \
        nest(fc1, parent=fc). \
        nest(fc2, parent=fc)

  chart.start_at(fc)
  chart.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
  pp(chart.spy())
  print(chart.to_code(fc))
  print(chart.to_code(fc1))
  print(chart.to_code(fc2))


if __name__ == '__main__':
  # example_1()
  # example_2()
  # example_3()
  # example_4()
  example_5()
