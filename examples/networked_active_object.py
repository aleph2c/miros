import time
import uuid
import random
import logging
# import functools
# from miros.hsm import pp
# from mesh import MirosNets
# from mesh import NetworkedFactory
from  miros_rabbitmq.network import NetworkedActiveObject
# from miros.activeobject import Factory
# from miros.activeobject import ActiveObject
from miros.hsm import spy_on
from miros.event import signals, Event, return_status

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
        '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

def make_name(post):
  return str(uuid.uuid4())[0:5] + '_' + post

def outer_init(chart, e):
  chart.post_fifo(
    Event(signal=signals.to_inner),
    times=1,
    period=random.randint(2, 7),
    deferred=True)
  chart.transmit(Event(signal=signals.other_to_outer, payload=chart.name))
  return return_status.HANDLED

def outer_to_inner(chart, e):
  return chart.trans(inner)

def outer_other_to_inner(chart, e):
  return chart.trans(inner)

def inner_entry(chart, e):
  chart.post_fifo(
    Event(signal=signals.to_outer),
    times=1,
    period=random.randint(2, 7),
    deferred=True)
  chart.transmit(Event(signal=signals.other_to_inner, payload=chart.name))
  return return_status.HANDLED

def inner_exit(chart, e):
  chart.cancel_events(Event(signal=signals.to_outer))
  return return_status.HANDLED

def inner_other_to_inner(chart, e):
  return return_status.HANDLED

def inner_to_inner(chart, e):
  return return_status.HANDLED

def inner_to_outer(chart, e):
  return chart.trans(outer)

def inner_other_to_outer(chart, e):
  return chart.trans(outer)

@spy_on
def inner(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = inner_entry(chart, e)
  elif(e.signal == signals.INIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.to_outer):
    status = inner_to_outer(chart, e)
  elif(e.signal == signals.other_to_outer):
    status = inner_other_to_outer(chart, e)
  elif(e.signal == signals.other_to_inner):
    status = inner_other_to_inner(chart, e)
  elif(e.signal == signals.to_inner):
    status = inner_to_inner(chart, e)
  elif(e.signal == signals.other_to_inner):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = inner_exit(chart, e)
  else:
    status, chart.temp.fun = return_status.SUPER, outer
  return status

@spy_on
def outer(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = outer_init(chart, e)
  elif(e.signal == signals.to_inner):
    status = outer_to_inner(chart, e)
  elif(e.signal == signals.other_to_inner):
    status = outer_other_to_inner(chart, e)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status


if __name__ == '__main__':
  random.seed()
  ao = NetworkedActiveObject(make_name('ao'),
                              rabbit_user='bob',
                              rabbit_password='dobbs',
                              tx_routing_key='heya.man',
                              rx_routing_key='#.man',
                              mesh_encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=')
  ao.enable_snoop_trace()
  # ao.enable_snoop_spy()
  ao.start_at(outer)
  time.sleep(60)


