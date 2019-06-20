
import time

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status

class ClassWithStatechartInIt(Factory):
  Default_Name = 'default_name'
  def __init__(self, name=None, live_trace=None, live_spy=None):
    # call the Factory ctor
    super().__init__(
      ClassWithStatechartInIt.Default_Name if name == None else name
    )
    # determine how this object will be instrumented
    self.live_spy = False if live_spy == None else live_spy
    self.live_trace = False if live_trace == None else live_trace
    
    # define our states and their statehandlers
    self.common_behaviors = self.create(state="common_behaviors"). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.common_behaviors_init). \
      catch(signal=signals.hook_1,
        handler=self.common_behaviors_hook_1). \
      catch(signal=signals.hook_2,
        handler=self.common_behaviors_hook_2). \
      catch(signal=signals.reset,
        handler=self.common_behaviors_reset). \
      to_method()

    self.a1 = self.create(state="a1"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.a1_entry). \
      catch(signal=signals.to_b1,
        handler=self.a1_to_b1). \
      to_method()

    self.b1 = self.create(state="b1"). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.b1_init). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.b1_entry). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.b1_exit). \
      to_method()

    self.b11 = self.create(state="b11"). \
      to_method()

    # nest our states within other states
    self.nest(self.common_behaviors, parent=None). \
        nest(self.a1, parent=self.common_behaviors). \
        nest(self.b1, parent=self.common_behaviors). \
        nest(self.b11, parent=self.b1)

    # start our statechart, which will start its thread
    self.start_at(self.common_behaviors)

    # let the internal statechart initialize before you give back control
    # to the synchronous part of your program
    time.sleep(0.001)

  @staticmethod
  def common_behaviors_init(chart, e):
    status = chart.trans(chart.a1)
    return status

  @staticmethod
  def common_behaviors_hook_1(chart, e):
    status = return_status.HANDLED
    # call the ClassWithStatechartInIt work2 method
    chart.worker1()
    return status

  @staticmethod
  def common_behaviors_hook_2(chart, e):
    status = return_status.HANDLED
    # call the ClassWithStatechartInIt work2 method
    chart.worker2()
    return status

  @staticmethod
  def common_behaviors_reset(chart, e):
    status = chart.trans(chart.common_behaviors)
    return status

  @staticmethod
  def a1_entry(chart, e):
    status = return_status.HANDLED
    # post an event to ourselves
    chart.post_fifo(Event(signal=signals.to_b1))
    return status

  @staticmethod
  def a1_to_b1(chart, e):
    status = chart.trans(chart.b1)
    return status

  @staticmethod
  def b1_init(chart, e):
    status = return_status.HANDLED
    return status

  @staticmethod
  def b1_entry(chart, e):
    status = return_status.HANDLED
    # post an event to ourselves
    chart.post_fifo(Event(signal=signals.hook_1))
    return status

  @staticmethod
  def b1_exit(chart, e):
    status = return_status.HANDLED
    # post an event to ourselves
    chart.post_fifo(Event(signal=signals.hook_2))
    return status

  def worker1(self):
    print('worker1 called')

  def worker2(self):
    print('worker2 called')

if __name__ == '__main__':
  chart = ClassWithStatechartInIt(name='chart', live_trace=True)
  chart.post_fifo(Event(signal=signals.reset))
  time.sleep(1)

