import time
from miros.hsm import spy_on, pp, state_method_template, HsmWithQueues
from miros.activeobject import ActiveObject, Factory
from miros.event import signals, Event, return_status
from datetime import datetime
import random

def t_question():
  '''
  +----------------------------- s -------------------------------+
  | +-------- s1 ---------+                 +-------- s2 -------+ |
  | | exit / b()          |                 | entry / c()       | |
  | |    +--- s11 ----+   |                 |  +---- s21 -----+ | |
  | |    | exit / a() |   |                 |  | entry / e()  | | |
  | |    |            |   |                 |  |              | | |
  | |    |            |   +- T [g()] / t() ->  |              | | |
  | |    +------------+   |                 |  +-----------/--+ | |
  | |                     |                 |   *-- / d() -+    | |
  | +---------------------+                 +-------------------+ |
  +---------------------------------------------------------------+

  '''

  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def s_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, chart.top
    return status

  @spy_on
  def s1_state(chart, e):
    def b(chart):
      chart.scribble("Running b()")

    def g(chart):
      chart.scribble("Running g() -- the guard, which return False")
      return False

    def t(chart):
      chart.scribble("Running t() -- funtion run on event")

    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      b(chart)
      status = return_status.HANDLED
    elif(e.signal == signals.T):
      if g(chart):
        t(chart)
        status = chart.trans(s2_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status

  @spy_on
  def s11_state(chart, e):
    def a(chart):
      chart.scribble("Running a()")

    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      a(chart)
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s1_state
    return status

  @spy_on
  def s2_state(chart, e):

    def c(chart):
      chart.scribble("running c()")

    def d(chart):
      chart.scribble("running d()")

    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      c(chart)
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      d(chart)
      status = chart.trans(s21_state)
    else:
      status, chart.temp.fun = return_status.SUPER, s_state
    return status

  @spy_on
  def s21_state(chart, e):
    def e_function(chart):
      chart.scribble("running e()")

    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
      e_function(chart)
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      status = return_status.HANDLED
    else:
      status, chart.temp.fun = return_status.SUPER, s2_state
    return status

  ao = ActiveObject(name="T_question")
  ao.start_at(s11_state)

  ao.clear_spy()
  ao.post_fifo(Event(signal=signals.T))
  time.sleep(0.2)
  pp(ao.spy())

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


def multiunit_example():

  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status
  import time

  # This statechart tests topology B in a multichart situation,
  # statechart built using a factory
  #  
  #  +------- fb --------------s-----+
  #  |  +---- fb1 -------t-------+   |
  #  |  | i/pub(BB)              |   l --> BB
  #  |  |  +- fb11---------+     |   |
  #  |  |  |               |     |   |
  #  |  |  |               <-b-+ <-a-+
  #  |  |  +---------------+   +-+   |
  #  |  +------------------------+   |
  #  +-------------------------------+
  #

  def trans_to_fb(chart, e):
    return chart.trans(fb)

  def trans_to_fb1(chart, e):
    return chart.trans(fb1)

  def trans_to_fb11(chart, e):
    return chart.trans(fb11)

  def publish_BB(chart, e):
    chart.publish(Event(signal=signals.BB,
      payload="information from b_chart riding within the BB signal"))
    return return_status.HANDLED

  b_chart = Factory('b_chart')
  fb = b_chart.create(state='fb'). \
          catch(signal=signals.a, handler=trans_to_fb1). \
          to_method()

  fb1 = b_chart.create(state='fb1'). \
          catch(signal=signals.b, handler=trans_to_fb11). \
          catch(signal=signals.INIT_SIGNAL, handler=publish_BB). \
          to_method()

  fb11 = b_chart.create(state='fb11'). \
          to_method()

  b_chart.nest(fb, parent=None). \
          nest(fb1, parent=fb). \
          nest(fb11, parent=fb1)

  def trans_to_fc(chart, e):
    return chart.trans(fc)

  def trans_to_fc1(chart, e):
    return chart.trans(fc1)

  def bb_handler(chart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.BB):
      chart.scribble(e.payload)
      status = chart.trans(fc)
    return status

  def trans_to_fc2(chart, e):
    return chart.trans(fc2)

  # The following state chart is used to test topology C
  # in a multichart situation, statechart built using the factory
  #
  #        +------------------ fc ---------------+
  #        |   +----- fc1----+   +-----fc2-----+ |
  #        | * |             |   |             | +----+
  #        | | |             +-a->             | |    |
  #        | +->             <-a-+             | |    BB
  #        |   |             |   |             | |    |
  #        |   |             |   |             | <----+
  #        |   +-------------+   +-------------+ |
  #        +-------------------------------------+
  #

  c_chart = Factory('c_chart')
  fc = c_chart.create(state='fc'). \
        catch(signal=signals.INIT_SIGNAL, handler=trans_to_fc1). \
        catch(signal=signals.BB, handler=bb_handler). \
        to_method()

  fc1 = c_chart.create(state='fc1'). \
        catch(signal=signals.a, handler=trans_to_fc2). \
        to_method()

  fc2 = c_chart.create(state='fc2'). \
        catch(signal=signals.a, handler=trans_to_fc1). \
        to_method()

  c_chart.nest(fc,  parent=None). \
          nest(fc1, parent=fc). \
          nest(fc2, parent=fc)

  # subscribe to BB signals sent to the active fabric
  # c_chart.subscribe(Event(signal=signals.BB))
  c_chart.subscribe(signals.BB)

  # Start up the charts and post an event to how they interact
  c_chart.start_at(fc)
  b_chart.start_at(fb)
  b_chart.post_fifo(Event(signal=signals.a))

  time.sleep(0.1)
  print(c_chart.trace())
  pp(c_chart.spy())
  print(b_chart.trace())
  pp(b_chart.spy())


def ultimate_hook_example1():
  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  ao = ActiveObject()
  ao.start_at(outer_state)
  ao.post_fifo(Event(signal=signals.BEHAVIOR_NAME))
  time.sleep(0.001)
  pp(ao.spy())

def ultimate_hook_example2():
  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status


  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your outer_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  @spy_on
  def inner_state(chart, e):
    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your inner_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = outer_state
      status = return_status.SUPER
    return status

  ao = ActiveObject()
  ao.start_at(inner_state)
  ao.post_fifo(Event(signal=signals.BEHAVIOR_NAME))
  time.sleep(0.001)
  pp(ao.spy())

def ultimate_hook_example3():
  import time
  from miros.hsm import spy_on, pp
  from miros.activeobject import ActiveObject
  from miros.event import signals, Event, return_status

  @spy_on
  def outer_state(chart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.BEHAVIOR_NAME):
      # your code would go here
      chart.scribble("your outer_state code here")
      status = return_status.HANDLED
    else:
      chart.temp.fun = chart.top
      status = return_status.SUPER
    return status

  @spy_on
  def inner_state(chart, e):
    #if(e.signal == signals.BEHAVIOR_NAME):
    #  # your code would go here
    #  chart.scribble("your inner_state code here")
    #  status = return_status.HANDLED
    #else:
    #  chart.temp.fun = outer_state
    #  status = return_status.SUPER
    chart.temp.fun = outer_state
    status = return_status.SUPER
    return status

  ao = ActiveObject()
  ao.start_at(inner_state)
  ao.post_fifo(Event(signal=signals.BEHAVIOR_NAME))
  time.sleep(0.001)
  pp(ao.spy())

def ultimate_hook_example4():
  import time
  from miros.hsm import pp
  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status

  def process_a_generic(chart, e):
    chart.scribble('processing a generic')
    return return_status.HANDLED

  def process_b_generic(chart, e):
    chart.scribble('processing b generic')
    return return_status.HANDLED

  # overrides the generic hook while in the specific state
  def process_a_specific(chart, e):
    chart.scribble('processing a specific')
    return return_status.HANDLED

  chart = Factory('ultimate_hook_example')
  generic = chart.create(state='generic'). \
    catch(signal=signals.a, handler=process_a_generic). \
    catch(signal=signals.b, handler=process_b_generic). \
    to_method()

  specific = chart.create(state='specific'). \
      catch(signal=signals.a, handler=process_a_specific). \
      to_method()

  chart.nest(generic, parent=None). \
        nest(specific, parent=generic)

  chart.start_at(specific)
  chart.post_fifo(Event(signal=signals.b))
  chart.post_fifo(Event(signal=signals.a))
  time.sleep(0.001)
  pp(chart.spy())

def augment_example():
  import time
  from miros.hsm import pp
  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status

  def process_a_generic(chart, e):
    chart.scribble('processing a generic')
    return return_status.HANDLED

  def process_b_generic(chart, e):
    chart.scribble('processing b generic')
    return return_status.HANDLED

  # overrides the generic hook while in the specific state
  def process_a_specific(chart, e):
    chart.scribble('processing a specific')
    return return_status.HANDLED

  chart = Factory('ultimate_hook_example')
  chart.augment(other=0, name='counter')
  assert(chart.counter == 0)
  generic = chart.create(state='generic'). \
    catch(signal=signals.a, handler=process_a_generic). \
    catch(signal=signals.b, handler=process_b_generic). \
    to_method()

  specific = chart.create(state='specific'). \
      catch(signal=signals.a, handler=process_a_specific). \
      to_method()

  chart.nest(generic, parent=None). \
        nest(specific, parent=generic)

  chart.start_at(specific)
  chart.post_fifo(Event(signal=signals.b))
  chart.post_fifo(Event(signal=signals.a))
  time.sleep(0.001)
  pp(chart.spy())


def reminder1():

  import time
  from miros.hsm import pp
  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status

  def polling_time_out(chart, e):
    return chart.trans(polling)

  def polling_enter(chart, e):
    chart.scribble("polling")
    return return_status.HANDLED

  def polling_init(chart, e):
    # illegal (init can't leave parent states)
    return chart.trans(processing)

  def processing_entry(chart, e):
    chart.processing_count += 1
    chart.scribble("processing")
    return return_status.HANDLED

  def processing_init(chart, e):
    status = None
    if chart.processing_count >= 5:
      status = chart.trans(busy)
    else:
      # illegal (init can't leave parent states)
      status = chart.trans(polling)
    return status

  def processing_exit(chart, e):
    chart.processing_count = 0
    return return_status.HANDLED

  def busy_entry(chart, e):
    chart.busy_count = 0
    return return_status.HANDLED

  def busy_time_out(chart, e):
    chart.busy_count += 1
    status = return_status.HANDLED
    if chart.busy_count >= 5:
      status = chart.trans(polling)
    return status

  chart = Factory('reminder_pattern_needed_1')
  chart.augment(other=0, name="processing_count")
  chart.augment(other=0, name="busy_count")

  polling = chart.create(state="polling"). \
              catch(signal=signals.TIME_OUT, handler=polling_time_out). \
              catch(signal=signals.INIT_SIGNAL, handler=polling_init). \
              to_method()

  processing = chart.create(state="processing"). \
              catch(signal=signals.ENTRY_SIGNAL, handler=processing_entry). \
              catch(signal=signals.INIT_SIGNAL, handler=processing_init). \
              catch(signal=signals.EXIT_SIGNAL, handler=processing_exit). \
              to_method()

  busy = chart.create(state="busy"). \
          catch(signal=signals.ENTRY_SIGNAL, handler=busy_entry). \
          catch(signal=signals.TIME_OUT, handler=busy_time_out). \
          to_method()

  chart.nest(polling, parent=None). \
        nest(processing, parent=None). \
        nest(busy, parent=processing)

  chart.start_at(polling)
  chart.post_fifo(Event(signal=signals.TIME_OUT), times=20, period=0.1)
  time.sleep(5)
  pp(chart.spy())

def reminder2():

  import time
  from miros.hsm import pp
  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status

  def polling_time_out(chart, e):
    chart.scribble("polling")
    chart.post_fifo(
      Event(signal=signals.PROCESS))
    return return_status.HANDLED

  def polling_process(chart, e):
    return chart.trans(processing)

  def processing_entry(chart, e):
    chart.processing_count += 1
    chart.scribble("processing")
    return return_status.HANDLED

  def processing_init(chart, e):
    status = return_status.HANDLED
    if chart.processing_count >= 3:
      chart.processing_count = 0
      status = chart.trans(busy)
    else:
      chart.post_fifo(
        Event(signal=signals.POLL))
    return status

  def processing_poll(chart, e):
    return chart.trans(polling)

  def processing_exit(chart, e):
    return return_status.HANDLED

  def busy_entry(chart, e):
    chart.busy_count = 0
    return return_status.HANDLED

  def busy_time_out(chart, e):
    chart.scribble("busy")
    chart.busy_count += 1
    status = return_status.HANDLED
    if chart.busy_count >= 2:
      status = chart.trans(polling)
    return status

  chart = Factory('reminder_pattern_needed_2')
  chart.augment(other=0, name="processing_count")
  chart.augment(other=0, name="busy_count")

  polling = chart.create(state="polling"). \
              catch(signal=signals.TIME_OUT, handler=polling_time_out). \
              catch(signal=signals.PROCESS,  handler=polling_process). \
              to_method()

  processing = chart.create(state="processing"). \
              catch(signal=signals.ENTRY_SIGNAL, handler=processing_entry). \
              catch(signal=signals.INIT_SIGNAL, handler=processing_init). \
              catch(signal=signals.EXIT_SIGNAL, handler=processing_exit). \
              catch(signal=signals.POLL, handler=processing_poll). \
              to_method()

  busy = chart.create(state="busy"). \
          catch(signal=signals.ENTRY_SIGNAL, handler=busy_entry). \
          catch(signal=signals.TIME_OUT, handler=busy_time_out). \
          to_method()

  chart.nest(polling,    parent=None). \
        nest(processing, parent=None). \
        nest(busy, parent=processing)

  chart.start_at(polling)
  chart.post_fifo(Event(signal=signals.TIME_OUT), times=20, period=0.1)
  time.sleep(1.0)
  pp(chart.spy())
  print(chart.trace())


def reminder3():
  import time
  from miros.hsm import pp
  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status

  def polling_time_out_hook(chart, e):
    '''generic TIME_OUT ultimate hook for all states,
       injects artificial event DATA_READY'''
    chart.scribble("polling")
    chart.processing_count += 1
    if(chart.processing_count >= 3):
      chart.post_fifo(Event(signal=signals.DATA_READY))
    return return_status.HANDLED

  def polling_init(chart, e):
    return chart.trans(processing)

  def processing_init(chart, e):
    return chart.trans(idle)

  def idle_data_ready(chart, e):
    return chart.trans(busy)

  def busy_entry(chart, e):
    chart.busy_count, chart.busy_count = 0, 0
    return return_status.HANDLED

  def busy_time_out_hook(chart, e):
    '''specific TIME_OUT hook for busy state'''
    status = return_status.HANDLED
    chart.scribble("busy")
    chart.busy_count += 1
    if(chart.busy_count >= 2):
      status = chart.trans(idle)
    return status

  chart = Factory('reminder')
  chart.augment(other=0, name="processing_count")
  chart.augment(other=0, name="busy_count")

  polling = chart.create(state="polling"). \
              catch(signal=signals.INIT_SIGNAL, handler=polling_init). \
              catch(signal=signals.TIME_OUT, handler=polling_time_out_hook). \
              to_method()

  processing = chart.create(state="processing"). \
                catch(signal=signals.INIT_SIGNAL, handler=processing_init). \
                to_method()

  idle = chart.create(state="idle"). \
          catch(signal=signals.DATA_READY, handler=idle_data_ready). \
          to_method()

  busy = chart.create(state="busy"). \
          catch(signal=signals.ENTRY_SIGNAL, handler=busy_entry). \
          catch(signal=signals.TIME_OUT, handler=busy_time_out_hook). \
              to_method()

  chart.nest(polling, parent=None). \
        nest(processing, parent=polling). \
        nest(idle, parent=processing). \
        nest(busy, parent=polling)

  chart.start_at(polling)
  chart.post_fifo(Event(signal=signals.TIME_OUT), times=20, period=0.1)
  time.sleep(1.0)
  pp(chart.spy())
  print(chart.trace())

def deferred1():
  import random
  import time
  from datetime import datetime
  from miros.hsm import pp
  from miros.activeobject import Factory
  from miros.event import signals, Event, return_status

 
  def processing_entry(chart, e):
    chart.defer(e)
    chart.scribble("deferred at {}". \
        format(datetime.now().strftime("%M:%S:%f")))
    return return_status.HANDLED

  def processing_init(chart, e):
    return chart.trans(idle)

  def idle_entry(chart, e):
    chart.recall()
    chart.scribble("recalled at {}". \
        format(datetime.now().strftime("%M:%S:%f")))
    return return_status.HANDLED

  def idle_new_request(chart, e):
    return chart.trans(receiving)

  def receiving_entry(chart, e):
    chart.scribble("receiving")
    chart.post_fifo(
      Event(signal=signals.RECEIVED),
      times=1,
      period=1.0,
      deferred=True)
    return return_status.HANDLED

  def receiving_received(chart, e):
    return chart.trans(authorizing)

  def authorizing_entry(chart, e):
    chart.scribble("authorizing")
    chart.post_fifo(
      Event(signal=signals.COMPLETED),
      times=1,
      period=2.0,
      deferred=True)
    return return_status.HANDLED

  def authorizing_authorized(chart, e):
    return chart.trans(idle)

  chart = Factory('deferred')

  processing = chart.create(state="processing"). \
                catch(signal=signals.NEW_REQUEST, handler=processing_entry). \
                catch(signal=signals.INIT_SIGNAL, handler=processing_init). \
                to_method()

  idle = chart.create(state='idle'). \
          catch(signal=signals.ENTRY_SIGNAL, handler=idle_entry). \
          catch(signal=signals.NEW_REQUEST, handler=idle_new_request). \
          to_method()

  receiving = chart.create(state='receiving'). \
                catch(signal=signals.ENTRY_SIGNAL, handler=receiving_entry). \
                catch(signal=signals.RECEIVED, handler=receiving_received). \
                to_method()

  authorizing = chart.create(state='authorizing'). \
                  catch(signal=signals.ENTRY_SIGNAL, 
                      handler=authorizing_entry). \
                  catch(signal=signals.COMPLETED,
                      handler=authorizing_authorized). \
                  to_method()

  chart.nest(processing, parent=None). \
        nest(idle, parent=processing). \
        nest(receiving, parent=processing). \
        nest(authorizing, parent=processing)

  chart.start_at(processing)

  def burst_event(event, bursts, fastest_time, slowest_time):
    for i in range(bursts):
      time.sleep(random.uniform(fastest_time, slowest_time))
      chart.post_fifo(event)

  burst_event(Event(signal=signals.NEW_REQUEST),
               bursts=15,
               fastest_time=0.2,
               slowest_time=1.0)

  print(chart.trace())
  time.sleep(6)
  pp(chart.spy())


def composite_pattern_1():
  # Make Something that can generate numbers for us
  # 1) needs to return a function
  # 2) needs to be tunable
  # 3) needs to be stochastic
  class FakeNewsSpec:
    ''' provides the following syntax:
        spec.initial_value
        spec.aggression
        spec.minimum
        spec.maximum
    '''
    def __init__(self,
                  aggression=0,
                  initial_value=None,
                  minimum=None,
                  maximum=None):
      if minimum is None:
        assert(0)
      if maximum is None:
        assert(0)
      if minimum >= maximum:
        assert(0)

      if initial_value is None:
        initial_value = (maximum - minimum) / 2.0
      elif initial_value < minimum:
        initial_value = minimum
      elif initial_value > maximum:
        initial_value = maximum

      self.initial_value = initial_value
      self.aggression    = aggression
      self.minimum       = minimum
      self.maximum       = maximum

  def fake_news(spec):
    '''
      # aggression ranges from 1 to 100.  1 is the least aggressive and 100 is
      # the most agressive
      fn = fake_news(FakeNewsSpec(minimum=0, maximum=100, initial_value=45, aggression=50))

      for i in range(5):
        print(fn())

      # 70.40052265431565
      # 98.55643192543394
      # 63.607687838082626
      # 96.33858152348765
      # 47.2780049249278

    '''
    AGGRESSION_MAX = 100
    '''returns a function that will generate the kind of fake news specified'''
    random.seed()

    if 1 <= spec.aggression <= AGGRESSION_MAX:
      aggression = spec.aggression
    elif spec.aggression < 1:
      aggression = 1
    else:
      aggression = AGGRESSION_MAX

    def _fake_news_generator():
      '''provides an infinite set of number within the spec'''
      current_number = spec.initial_value

      while(True):
        random_number  = random.uniform(spec.minimum, spec.maximum)
        # IIR (infinite impulse response)
        current_number = ((aggression * random_number +
                           (AGGRESSION_MAX - aggression) *
                           current_number)) / AGGRESSION_MAX
        yield current_number

    def _fake_news():
      '''just hides the next syntax'''
      return next(_fake_news_generator())

    return _fake_news

  # Try it out
  fake_transducer = fake_news(FakeNewsSpec(minimum=0, maximum=100, initial_value=45, aggression=20))
  for i in range(3):
    print(fake_transducer())

  # Define a method which will determine if the piston is ready to fire ..
  # keep it separate and easy to change.  We will inject it into the Piston
  # class when we build it
  def is_this_piston_ready(piston):

    comp  = piston.get_composite_reading()
    temp  = piston.get_temperature_reading()

    if 0 <= comp <= 20 and 50 <= temp <= 100:
       ready = True
    elif 25  <= comp <= 50 and 200 <= temp <= 333:
       ready = True
    elif 30  <= comp <= 66 and 403 <= temp <= 600:
       ready = True
    elif 70  <= comp <= 100 and 670 <= temp <= 1500:
       ready = True
    else:
      ready = False

    return ready

  class FusionReactor(Factory):
    def __init__(self, name):
      super().__init__(name)
      self.pistons = []
      self.count = 0

  class Piston(HsmWithQueues):
    def __init__(self,
                 get_composite_reading,
                 get_temperature_reading,
                 is_this_piston_ready,
                 number):
      super().__init__()

      self.is_this_piston_ready    = is_this_piston_ready
      self.get_composite_reading   = get_composite_reading
      self.get_temperature_reading = get_temperature_reading
      self.number                  = number
      self.count                   = 0
      self.armed                   = False

  # This is the piston's HSM, it will be shared by all pistons
  @spy_on
  def piston_ready(piston, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      piston.armed = False
      status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
      status = piston.trans(relaxing)
    else:
      status, piston.temp.fun = return_status.SUPER, piston.top
    return status

  @spy_on
  def relaxing(piston, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      piston.scribble("relaxing")
    elif(e.signal == signals.TIME_OUT):
      status = return_status.HANDLED
      piston.count += 1
      if piston.count >= 7:
        piston.count = 0
        status = piston.trans(pending_optimal_conditions)
    elif(e.signal == signals.PRIMING):
      return piston.trans(pending_optimal_conditions)
    else:
      status, piston.temp.fun = return_status.SUPER, piston_ready
    return status

  @spy_on
  def triggered(piston, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      piston.scribble("piston_slamming! at {}". \
        format(datetime.now().strftime("%M:%S:%f")))
    elif(e.signal == signals.TIME_OUT):
      status = piston.trans(relaxing)
    else:
      status, piston.temp.fun = return_status.SUPER, piston_ready
    return status

  @spy_on
  def pending_optimal_conditions(piston, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.TIME_OUT):
      if piston.is_this_piston_ready(piston):
        status = piston.trans(ready)
      else:
        status = piston.trans(pending_optimal_conditions)
    else:
      status, piston.temp.fun = return_status.SUPER, piston_ready
    return status

  @spy_on
  def ready(piston, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):
      piston.armed = True
      status = return_status.HANDLED
    elif(e.signal == signals.FIRE):
      status = piston.trans(triggered)
    elif(e.signal == signals.TIME_OUT):
      status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
      piston.armed = False
      status = return_status.HANDLED
    else:
      status, piston.temp.fun = return_status.SUPER, pending_optimal_conditions
    return status

  # A function for building pistons
  def build_piston(number, starting_state):
    # We would change the get_composite_reading and get_temperature_reading
    # with the actual functions that would return these values in production
    piston = Piston(
      get_composite_reading=fake_news(
        FakeNewsSpec(
          minimum=0,
          maximum=100,
          initial_value=89,
          aggression=21)),
      get_temperature_reading=fake_news(
        FakeNewsSpec(
          minimum=0,
          maximum=1500,
          initial_value=798,
          aggression=16)),
      is_this_piston_ready=is_this_piston_ready,
      number=number
    )
    piston.start_at(starting_state)
    return piston

  # The fusion statechart callbacks
  def reactor_on_entry(reactor, e):
    status = return_status.HANDLED
    reactor.count = 0
    reactor.pistons = \
      [build_piston(piston_number, starting_state=piston_ready)
            for piston_number in range(255)]
    return status

  def reactor_on_time_out(reactor, e):
    status = return_status.HANDLED

    # provide a relaxing TIME_OUT pulse to each piston
    for piston in reactor.pistons:
      piston.dispatch(e)

    reactor.count += 1
    if reactor.count >= 10:
      reactor.count = 0
      reactor.post_fifo(
        Event(signal=signals.COOL_ENOUGH))
    return status

  def reactor_on_init(reactor, e):
    status = reactor.trans(energy_generation)
    return status

  def reactor_on_priming(reactor, e):
    status = return_status.HANDLED
    reactor.pistons[e.payload].dispatch(e)
    return status

  def energy_generation_init(reactor, e):
    status = reactor.trans(pending_on_pistons)
    return status

  def fusion_active_entry(reactor, e):
    status = return_status.HANDLED
    for piston in reactor.pistons:
      piston.dispatch(
        Event(signal=signals.FIRE))
    return status

  def fusion_active_fire_primed(reactor, e):
    status = reactor.trans(pending_on_pistons)
    return status

  def fusion_waiting_time_out(reactor, e):
    status = return_status.HANDLED
    all_ready = True
    for piston in reactor.pistons:
      piston.dispatch(e)
      all_ready &= piston.armed
    if all_ready:
      status = reactor.trans(fusion_and_heat_transfer)
    return status

  def fusion_waiting_fire(reactor, e):
    status = return_status.HANDLED
    return status

  # Create a fusion reactor object and its HSM
  fusion_reactor = FusionReactor("fusion_reactor")

  fusion_active = \
    fusion_reactor.create(state="fusion_active"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=reactor_on_entry). \
      catch(signal=signals.INIT_SIGNAL,
        handler=reactor_on_init). \
      catch(signal=signals.TIME_OUT,
        handler=reactor_on_time_out). \
      catch(signal=signals.PRIMING,
        handler=reactor_on_priming). \
      to_method()

  energy_generation = \
    fusion_reactor.create(state="energy_generation"). \
      catch(signal=signals.INIT_SIGNAL,
        handler=energy_generation_init). \
      to_method()

  fusion_and_heat_transfer = \
    fusion_reactor.create(state="fusion_and_heat_transfer"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=fusion_active_entry). \
      catch(signal=signals.COOL_ENOUGH,
        handler=fusion_active_fire_primed). \
      to_method()

  pending_on_pistons = \
    fusion_reactor.create(state='pending_on_pistons'). \
      catch(signal=signals.TIME_OUT,
        handler=fusion_waiting_time_out). \
      catch(signal=signals.FIRE,
        handler=fusion_waiting_time_out). \
      to_method()

  fusion_reactor.nest(fusion_active, parent=None). \
    nest(energy_generation, parent=fusion_active). \
    nest(fusion_and_heat_transfer, parent=energy_generation). \
    nest(pending_on_pistons, parent=energy_generation)

  fusion_reactor.start_at(fusion_active)

  fusion_reactor.post_fifo(Event(signal=signals.TIME_OUT),
                         times=100,
                         period=0.1,
                         deferred=False)
  time.sleep(10)
  print(fusion_reactor.trace())
  # pp(fusion_reactor.pistons[0].spy())
  # pp(fusion_reactor.pistons[1].spy())
  print(fusion_reactor.pistons[1].trace())

if __name__ == '__main__':
  # t_question()
  # example_1()
  # example_2()
  # example_3()
  # example_4()
  # example_5()
  # multiunit_example()
  # ultimate_hook_example1()
  # ultimate_hook_example3()
  # ultimate_hook_example4()
  # augment_example()
  # reminder1()
  # reminder2()
  # reminder3()
  # deferred1()
  composite_pattern_1()



