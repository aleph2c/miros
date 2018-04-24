import time
import uuid
import random
import functools
from miros.hsm import pp
from mesh import MirosNets
from miros.foreign import ForeignHsm
from miros.activeobject import Factory
from miros.activeobject import ActiveObject
from miros.hsm import HsmWithQueues, spy_on
from miros.event import signals, Event, return_status

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

class NetworkedActiveObject(ActiveObject):
  def __init__(self,
                name,
                rabbit_user,
                rabbit_password,
                mesh_encryption_key,
                tx_routing_key=None,
                rx_routing_key=None,
                spy_snoop_encryption_key=None,
                trace_snoop_encryption_key=None):
    super().__init__(name)

    on_message_callback = functools.partial(self.on_network_message)
    on_trace_message_callback = functools.partial(self.on_network_trace_message)
    on_spy_message_callback = functools.partial(self.on_network_spy_message)

    if tx_routing_key is None:
      tx_routing_key = "empty"

    if rx_routing_key is None:
      rx_routing_key = tx_routing_key

    if trace_snoop_encryption_key is None:
      trace_snoop_encryption_key = mesh_encryption_key

    if spy_snoop_encryption_key is None:
      spy_snoop_encryption_key = mesh_encryption_key

    self.nets = MirosNets(miros_object = self,
                 rabbit_user=rabbit_user,
                 rabbit_password=rabbit_password,
                 mesh_encryption_key=mesh_encryption_key,
                 trace_snoop_encryption_key=trace_snoop_encryption_key,
                 spy_snoop_encryption_key=spy_snoop_encryption_key,
                 tx_routing_key=tx_routing_key,
                 rx_routing_key=rx_routing_key,
                 on_mesh_rx=on_message_callback,
                 on_trace_rx=on_trace_message_callback,
                 on_spy_rx=on_spy_message_callback)


  def on_network_message(self, unused_channel, basic_deliver, properties, event):
    if isinstance(event, Event):
      # print("heard {} from {}".format(event.signal_name, event.payload))
      if event.payload != self.name:
        self.post_fifo(event)
    else:
      print("rx non-event {}".format(event))

  def on_network_trace_message(self, ch, method, properties, body):
    '''create a on_network_trace_message function received messages in the queue'''
    print(" [+t] {}".format(body.replace('\n', '')))

  def on_network_spy_message(self, ch, method, properties, body):
    '''create a on_network_spy_message function received messages in the queue'''
    print(" [+s] {}".format(body))

  def transmit(self, event):
    self.nets.transmit(event)

  def start_at(self, initial_state):
    super().start_at(initial_state)
    time.sleep(0.1)
    self.nets.start_threads()

  def enable_snoop_trace(self):
    self.live_trace = True
    self.register_live_trace_callback(self.nets.broadcast_trace)
    self.nets.enable_snoop_trace()

  def enable_snoop_spy(self):
    self.live_spy = True
    self.register_live_spy_callback(self.nets.broadcast_spy)
    self.nets.enable_snoop_spy()

if __name__ == '__main__':

  ao = NetworkedActiveObject(make_name('ao'),
                              rabbit_user='bob',
                              rabbit_password='dobbs',
                              tx_routing_key='bob.dobbs',
                              rx_routing_key='#',
                              mesh_encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=')
  ao.enable_snoop_trace()
  random.seed()

  def custom_on_message_callback(unused_channel,
                                 basic_deliver,
                                 properties,
                                 body):
    print("chart rx, Received mesh message # {} from {}: {}".
      format(basic_deliver.delivery_tag, properties.app_id, body))
  ao.start_at(outer)
  time.sleep(60)


