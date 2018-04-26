import time
import uuid
import random
import logging
from mesh import NetworkedFactory
from miros.event import signals, Event, return_status

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
        '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

def make_name(post):
  return str(uuid.uuid4())[0:5] + '_' + post

def on_outer_init(chart, e):
  chart.post_fifo(Event(signal=signals.to_inner),
    times=1,
    period=random.randint(2, 7),
    deferred=True)
  chart.transmit(Event(signal=signals.other_to_outer))
  return return_status.HANDLED

def on_outer_to_inner(chart, e):
  return chart.trans(inner)

def on_outer_other_to_inner(chart, e):
  return chart.trans(inner)

def on_inner_entry(chart, e):
  chart.post_fifo(Event(signal=signals.to_outer),
    times=1,
    period=random.randint(2, 7))
  chart.transmit(Event(signal=signals.other_to_inner))
  return return_status.HANDLED

def on_inner_exit(chart, e):
  chart.snoop_scribble("cancelling {}".format('to_outer'))
  chart.cancel_events(
    Event(signal=signals.to_outer))
  return return_status.HANDLED

def on_inner_other_to_inner(chart, e):
  chart.snoop_scribble("ignoring {}".format(e.signal_name))
  return return_status.HANDLED

def on_inner_to_inner(chart, e):
  chart.snoop_scribble("ignoring {}".format(e.signal_name))
  return return_status.HANDLED

def on_inner_to_outer(chart, e):
  return chart.trans(outer)

def on_inner_other_to_outer(chart, e):
  return chart.trans(outer)

chart = NetworkedFactory(make_name('fo'),
         rabbit_user='bob',
         rabbit_password='dobbs',
         tx_routing_key='heya.man',
         rx_routing_key='#.man',
         mesh_encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=')

outer = chart.create(state='outer'). \
          catch(signal=signals.to_inner, handler=on_outer_to_inner). \
          catch(signal=signals.other_to_inner, handler=on_outer_other_to_inner). \
          catch(signal=signals.INIT_SIGNAL, handler=on_outer_init). \
          to_method()

inner = chart.create(state='inner'). \
          catch(signal=signals.ENTRY_SIGNAL, handler=on_inner_entry). \
          catch(signal=signals.EXIT_SIGNAL, handler=on_inner_exit). \
          catch(signal=signals.other_to_inner, handler=on_inner_other_to_inner). \
          catch(signal=signals.to_inner, handler=on_inner_to_inner). \
          catch(signal=signals.to_outer, handler=on_inner_to_outer). \
          catch(signal=signals.other_to_outer, handler=on_inner_other_to_outer). \
          to_method()

chart.nest(outer, parent=None). \
      nest(inner, parent=outer)

if __name__ == '__main__':
  random.seed()
  #chart.enable_snoop_spy()
  chart.start_at(outer)
  time.sleep(60)


