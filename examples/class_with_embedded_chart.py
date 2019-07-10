import time
from collections import namedtuple

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status

class ClassWithEmbeddedChart(Factory):
  def __init__(self, name, live_trace=None):
    '''demonstration of a miros hierarchical statemachine within a class.

    **Args**:
       | ``name`` (str): The name of this object in the trace instrumentation
       | ``live_trace=None`` (str): set to true to get a live trace of the chart
    '''
    super().__init__(name)
   
    self.live_trace = True if live_trace else False
    self.outer_state = self.create(state="outer_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.outer_state_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.outer_state_init_signal). \
      catch(signal=signals.Hook,
        handler=self.outer_state_hook). \
      to_method()

    self.inner_state_1 = self.create(state="inner_state_1"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.inner_state_1_entry_signal). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.inner_state_1_exit_signal). \
      catch(signal=signals.B,
        handler=self.inner_state_1_b). \
      to_method()

    self.inner_state_2 = self.create(state="inner_state_2"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.inner_state_2_entry_signal). \
      catch(signal=signals.A,
        handler=self.inner_state_2_a). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.inner_state_2_exit_signal). \
      to_method()

    self.nest(self.outer_state, parent=None). \
      nest(self.inner_state_1, parent=self.outer_state). \
      nest(self.inner_state_2, parent=self.outer_state)

    # this is the attachment point on the diagram
    self.start_at(self.outer_state)

  @staticmethod
  def outer_state_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.attribute_1 = False
    chart.attribute_2 = False
    return status

  @staticmethod
  def outer_state_init_signal(chart, e):
    status = chart.trans(chart.inner_state_1)
    return status

  @staticmethod
  def outer_state_hook(chart, e):
    status = return_status.HANDLED
    print("hook")
    return status

  @staticmethod
  def inner_state_1_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.method_1()
    return status

  @staticmethod
  def inner_state_1_exit_signal(chart, e):
    status = return_status.HANDLED
    chart.method_2()
    return status

  @staticmethod
  def inner_state_1_b(chart, e):
    status = chart.trans(chart.inner_state_2)
    return status

  @staticmethod
  def inner_state_2_entry_signal(chart, e):
    status = return_status.HANDLED
    chart_attribute_1 = True
    chart_attribute_2 = True
    return status

  @staticmethod
  def inner_state_2_a(chart, e):
    status = chart.trans(chart.inner_state_1)
    return status

  @staticmethod
  def inner_state_2_exit_signal(chart, e):
    status = return_status.HANDLED
    chart_attribute_1 = False
    chart_attribute_2 = False
    return status

  def method_1(self):
    print("calling method_1")

  def method_2(self):
    print("calling method_2")

if __name__ == "__main__":
  cwec = ClassWithEmbeddedChart('cwec', live_trace=True)
  cwec.post_fifo(Event(signal=signals.B))
  cwec.post_fifo(Event(signal=signals.Hook))
  cwec.post_fifo(Event(signal=signals.A))
  time.sleep(0.01)
