import re
import time
import logging
from collections import deque
from functools import partial
from collections import namedtuple

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status

class InstrumentedFactory(Factory):
  def __init__(self, name, *, log_file=None, live_trace=None, live_spy=None):
    super().__init__(name)
    self.live_trace = False if live_trace == None else live_trace
    self.live_spy = False if live_spy == None else live_spy
    self.log_file = 'valgrind_simple_2.log' if log_file == None else log_file

    self._output = deque(maxlen=1)
    self._output.append(None)

    with open(self.log_file, "w") as fp:
      fp.write("")

    logging.basicConfig(
      format='%(asctime)s %(levelname)s:%(message)s',
      filename=self.log_file,
      level=logging.DEBUG)

    self.register_live_spy_callback(partial(self.spy_callback))
    self.register_live_trace_callback(partial(self.trace_callback))

  @property
  def output(self):
    return self._output[-1]

  @output.setter
  def output(self, item):
    self._output.append(item)

  def trace_callback(self, trace):
    '''trace without datetimestamp'''
    trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
    logging.debug("T: " + trace_without_datetime)

  def spy_callback(self, spy):
    '''spy with machine name pre-pending'''
    logging.debug("S: [{}] {}".format(self.name, spy))


class SimpleChartToTestWithValgrind(InstrumentedFactory):
  def __init__(self, name, live_trace=None, live_spy=None):
    '''Testing a statechart that doesn't share attributes with valgrind

    **Args**:
       | ``name`` (str): name of the chart
       | ``live_trace=None``: enable live_trace feature?
       | ``live_spy=None``: enable live_spy feature?

    **Example(s)**:
      
    .. code-block:: python
       
       ao = SimpleChartToTestWithValgrind('valgrind_test')

    '''
    super().__init__(name, live_trace=live_trace, live_spy=live_spy)

    self.c = self.create(state="c"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.c_init_signal). \
      catch(signal=signals.B,
        handler=self.c_b). \
      to_method()

    self.c1 = self.create(state="c1"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c1_entry_signal). \
      catch(signal=signals.A,
        handler=self.c1_a). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.c1_exit_signal). \
      to_method()

    self.c2 = self.create(state="c2"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.c2_entry_signal). \
      catch(signal=signals.A,
        handler=self.c2_a). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.c2_exit_signal). \
      to_method()
    
    self.nest(self.c, parent=None). \
         nest(self.c1, parent=self.c). \
         nest(self.c2, parent=self.c)

    self.start_at(self.c)

  def c_entry_signal(self, e):
    status = return_status.HANDLED
    return status

  def c_init_signal(self, e):
    status = self.trans(self.c1)
    return status

  def c_b(self, e):
    status = self.trans(self.c)
    return status

  def c1_entry_signal(self, e):
    status = return_status.HANDLED
    return status

  def c1_a(self, e):
    status = self.trans(self.c2)
    return status

  def c1_exit_signal(self, e):
    status = return_status.HANDLED
    return status

  def c2_entry_signal(self, e):
    status = return_status.HANDLED
    return status

  def c2_a(self, e):
    status = self.trans(self.c1)
    return status

  def c2_exit_signal(self, e):
    status = return_status.HANDLED
    return status

if __name__ == '__main__':
  ao = SimpleChartToTestWithValgrind('valgrind_test', live_trace=True)
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.B))
  ao.post_fifo(Event(signal=signals.A))
  ao.post_fifo(Event(signal=signals.B))
  ao.post_fifo(Event(signal=signals.A))
  time.sleep(0.5)

