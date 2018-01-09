#!/usr/bin/env python3
'''
  Usage:
    Sends a new task request to "c_trace_consumer.py" running on a different
    machine.

    1) start up a couple of c_trace_consumer.py sessions

    > python3 c_trace_producer.py

  Demonstrates:
    * Exchanges
    * 'fanout' routing
    * Work queues
    * Sending encrypted spy/trace information to another computer

  Monitoring:
    * to view the results with the RabbitMQ manager:
    <hostname>:15672 in browser

    Where <hostname> is the results of your `hostname` command

'''

import pika
from cryptography.fernet import Fernet
from miros.activeobject import Factory
from miros.event import signals, Event, return_status
from miros.hsm import pp
import time
from functools import wraps


class RabbitProducer(Factory):
  '''
  The networking side of the RabbitProducer looks like this:

  |--- RabbitProducer ---------------------->|

                            +----------------+  +---------+
  +------------------+   +->| spy exchange   +->| spy_c   |
  |                  |   |  +----------------+  +---------+
  | startchart emit  +-->|
  |                  |   |
  +------------------+   |  +----------------+  +---------+
                         +->| trace exchange +->| trace_c |
                            +----------------+  +---------+

  The RabbitProducer ties a rabbitmq producer and some exchanges to an active
  object.   The live spy/trace output are encrypted then routed into two
  separate exchanges, which transmit their messaging to the ``spy_c` and
  ``trace_c`` consumers, running on a different machine (see c_trace_consumer.py
  for this code).

  To build a chart with this rabbitmq producer you would slightly adjust how
  you build a factory:

      chart = RabbitProducer(chart_name="rabbit_producer",
          rabbit_user="bob",
          rabbit_password="dobbs",
          ip="192.168.1.72",
          port=5672)

  The chart would have a typical factory api, and with it you could build and
  start your statechart.

  To turn off the networking:

      chart.connection.close()

  '''
  def __init__(self, chart_name, rabbit_user, rabbit_password, ip, port):
    super().__init__(chart_name + '_' + ip)
    self.rabbit_user = rabbit_user
    self.rabbit_password = rabbit_password
    self.destination_ip = ip
    self.destination_port = port

    credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
    parameters = pika.ConnectionParameters(ip, port, '/', credentials)
    self.connection = pika.BlockingConnection(parameters=parameters)

    self.channel = self.connection.channel()
    self.channel.exchange_declare(exchange='spy', exchange_type='fanout')
    self.channel.exchange_declare(exchange='trace', exchange_type='fanout')

    def strip_trace(fn):
      @wraps(fn)
      def _strip_trace(trace_live):

        trace_live = trace_live.replace("\n", "")
        fn(trace_live)
      return _strip_trace

    def encrypt(fn):
      @wraps(fn)
      def _encrypt(plain_text):
        key = b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg='
        f = Fernet(key)
        cyphertext = f.encrypt(plain_text.encode())
        # broadcast_trace
        fn(cyphertext)
      return _encrypt

    @encrypt
    def broadcast_spy(spy_live):
      self.channel.basic_publish(
          exchange='spy',
          routing_key='',
          body=spy_live
      )

    @strip_trace
    @encrypt
    def broadcast_trace(trace_live):
      self.channel.basic_publish(
          exchange='trace',
          routing_key='',
          body=trace_live
      )

    self.register_live_spy_callback(broadcast_spy)
    self.register_live_trace_callback(broadcast_trace)
    self.live_spy   = True
    self.live_trace = True


def producer_outer_entry(chart, e):
  status = return_status.UNHANDLED
  return status


def producer_outer_exit(chart, e):
  status = return_status.UNHANDLED
  return status


def producer_outer_init(chart, e):
  status = return_status.UNHANDLED
  return status


def producer_outer_B(chart, e):
  status = chart.trans(producer_outer)
  return status


def c1_entry(chart, e):
  status = return_status.UNHANDLED
  return status


def c1_exit(chart, e):
  status = return_status.UNHANDLED
  return status


def c1_A(chart, e):
  status = return_status.UNHANDLED
  return status


def c2_entry(chart, e):
  status = return_status.UNHANDLED
  return status


def c2_exit(chart, e):
  status = return_status.UNHANDLED
  return status


def c2_A(chart, e):
  status = return_status.UNHANDLED
  return status


chart = RabbitProducer(
  chart_name="rabbit_producer",
  rabbit_user="bob",
  rabbit_password="dobbs",
  ip="192.168.1.72",
  port=5672
)

producer_outer = chart.create(state='producer_outer'). \
  catch(signal=signals.ENTRY_SIGNAL, handler=producer_outer_entry). \
  catch(signal=signals.EXIT_SIGNAL, handler=producer_outer_exit). \
  catch(signal=signals.INIT_SIGNAL, handler=producer_outer_init). \
  catch(signal=signals.B, handler=producer_outer_B). \
  to_method()

c1 = chart.create(state='c1'). \
  catch(signal=signals.ENTRY_SIGNAL, handler=c1_entry). \
  catch(signal=signals.EXIT_SIGNAL, handler=c1_exit). \
  catch(signal=signals.A, handler=c1_A). \
  to_method()

c2 = chart.create(state='c2'). \
  catch(signal=signals.ENTRY_SIGNAL, handler=c2_entry). \
  catch(signal=signals.EXIT_SIGNAL, handler=c2_exit). \
  catch(signal=signals.A, handler=c2_A). \
  to_method()

chart.nest(producer_outer, parent=None). \
  nest(c1, parent=producer_outer). \
  nest(c2, parent=producer_outer)

chart.start_at(producer_outer)
chart.post_fifo(Event(signal=signals.B))
time.sleep(0.1)
pp(chart.spy())
print(chart.trace())
chart.connection.close()
