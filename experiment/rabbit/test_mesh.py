import time
import uuid
import random
from miros.hsm import pp
from miros.activeobject import Factory
from miros.hsm import HsmWithQueues, spy_on
from miros.activeobject import ActiveObject
from miros.event import signals, Event, return_status

chart = Factory('test_' + str(uuid.uuid4())[0:5])

def outer_init(chart, e):
  chart.post_fifo(
    Event(signal=signals.to_inner),
    times=1,
    period=random.randint(2, 5),
    deferred=True)
  return return_status.HANDLED

def outer_to_inner(chart, e):
  return chart.trans(inner)

def inner_entry(chart, e):
  chart.post_fifo(
    Event(signal=signals.to_outer),
    times=1,
    period=random.randint(2, 5),
    deferred=True)
  return return_status.HANDLED

def inner_exit(chart, e):
  chart.cancel_events(Event(signal=signals.to_outer))
  return return_status.HANDLED

def inner_to_outer(chart, e):
  return chart.trans(outer)

outer = chart.create(state='outer'). \
    catch(signal=signals.INIT_SIGNAL, handler=outer_init). \
    catch(signal=signals.to_inner, handler=outer_to_inner). \
    to_method()

inner = chart.create(state='inner'). \
    catch(signal=signals.ENTRY_SIGNAL, handler=inner_entry). \
    catch(signal=signals.EXIT_SIGNAL, handler=inner_exit). \
    catch(signal=signals.to_outer, handler=inner_to_outer). \
    to_method()

chart.nest(outer, parent=None). \
    nest(inner, parent=outer)

if __name__ == '__main__':
  chart.live_trace = True
  chart.start_at(outer)
  time.sleep(60)

