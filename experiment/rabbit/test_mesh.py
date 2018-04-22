import time
import uuid
import random
from miros.hsm import pp
from miros.activeobject import Factory
from miros.hsm import HsmWithQueues, spy_on
from miros.activeobject import ActiveObject
from miros.event import signals, Event, return_status
from mesh import MirosNets

def make_name(pre):
  return pre + str(uuid.uuid4())[0:5]

def outer_init(chart, e):
  chart.post_fifo(
    Event(signal=signals.to_inner),
    times=1,
    period=random.randint(2, 5),
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
    period=random.randint(2, 5),
    deferred=True)
  chart.transmit(Event(signal=signals.other_to_inner, payload=chart.name))
  return return_status.HANDLED

def inner_exit(chart, e):
  chart.cancel_events(Event(signal=signals.to_outer))
  return return_status.HANDLED

def inner_other_to_inner(chart, e):
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
  elif(e.signal == signals.inner_other_to_inner):
    status = inner_other_to_inner(chart, e)
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
  def __init__(self, name):
    super().__init__(name)

    def on_message_callback(unused_channel,
                             basic_deliver,
                             properties,
                             body):
      self.on_network_message(body)

    self.nets = MirosNets(miros_object = self,
                 rabbit_user='bob',
                 rabbit_password='dobbs',
                 mesh_encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=',
                 routing_key="testing",
                 on_mesh_rx=on_message_callback)

    self.nets.start_threads()

  def on_network_message(self, event):
    if isinstance(event, Event):
      # print("heard {} from {}".format(event.signal_name, event.payload))
      if event.payload != self.name:
        self.post_fifo(event)
    else:
      print("rx non-event {}".format(event))

  def transmit(self, event):
    self.nets.transmit(event)

if __name__ == '__main__':
  ao = NetworkedActiveObject(make_name('active_object'))
  ao.live_trace = True

  def custom_on_message_callback(unused_channel,
                                 basic_deliver,
                                 properties,
                                 body):
    print("chart rx, Received mesh message # {} from {}: {}".
      format(basic_deliver.delivery_tag, properties.app_id, body))


  ao.start_at(outer)

  time.sleep(30)


