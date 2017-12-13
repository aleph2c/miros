import time
from miros.hsm import spy_on, pp, state_method_template
from miros.activeobject import ActiveObject, Factory
from miros.event import signals, Event, return_status


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
    return return_state.HANDLED

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
    return chart.trans(polling)

  def polling_enter(chart, e):
    chart.scribble("polling")
    return return_state.HANDLED

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
  reminder1()
