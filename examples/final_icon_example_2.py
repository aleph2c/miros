import time

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status

class InstrumentedFactory(Factory):
  def __init__(self, name, live_trace=None, live_spy=None):
    super().__init__(name)
    self.live_trace = False if live_trace == None else live_trace
    self.live_spy = False if live_spy == None else live_spy

class FinalIconExample(InstrumentedFactory):
  def __init__(self, name, condition, live_trace=None, live_spy=None):
    '''statechart demonstration the final icon

    **Args**:
       | ``name`` (str): name of the statechart
       | ``condition`` (bool): do we want to transition into the inner state?
       | ``live_trace=None``: enable live_trace feature?
       | ``live_spy=None``: enable live_spy feature?

    **Example(s)**:
      
    .. code-block:: python
       
       FinalIconExample(name='final_icon', condition=True)

    '''
    super().__init__(name, live_trace, live_spy)
    self.condition = condition

    self.outer_state = self.create(state="outer_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.outer_state_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.outer_state_init_signal). \
      catch(signal=signals.Retry,
        handler=self.outer_state_retry). \
      to_method()

    self.inner_state = self.create(state="inner_state"). \
      to_method()

    self.nest(self.outer_state, parent=None). \
         nest(self.inner_state, parent=self.outer_state)

    self.start_at(self.outer_state)

  @staticmethod
  def outer_state_entry_signal(chart, e):
    chart.condition = False if chart.condition == None else chart.condition
    status = return_status.HANDLED
    return status

  @staticmethod
  def outer_state_init_signal(chart, e):
    if chart.condition:
      status = chart.trans(chart.inner_state)
    else:
      chart.scribble("run code, but don't transition out of outer_state")
      status = return_status.HANDLED
    return status

  @staticmethod
  def outer_state_retry(chart, e):
    chart.condition = False if chart.condition else True
    status = chart.trans(chart.outer_state)
    return status

if __name__ == "__main__":
  ao = FinalIconExample(name='final_icon', condition=True, live_spy=True)
  ao.post_fifo(Event(signal=signals.Retry))
  ao.post_fifo(Event(signal=signals.Retry))
  time.sleep(0.01)
