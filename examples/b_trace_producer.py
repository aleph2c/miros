#!/usr/bin/env python3
'''
  Usage:
    Sends a new task request to "b_trace_consumer.py"
    1) start up a couple of b_trace_consumer.py sessions

    > python3 b_trace_consumer.py message....

  Demonstrates:
    * Work queues

  Monitoring:
    * to view the results with the RabbitMQ manager:
    <hostname>:15672 in browser

    where <hostname> is the results of your hostname command

'''

import pika
import sys
import os.path, sys
from miros.activeobject import Factory
from miros.event import signals, Event, return_status
from miros.hsm import pp
import time

class RabbitProducer(Factory):
  def __init__(self, chart_name, rabbit_user, rabbit_password, ip, port):
    super().__init__(chart_name+'_'+ip)
    self.rabbit_user = rabbit_user
    self.rabbit_password = rabbit_password
    self.destination_ip = ip
    self.destination_port = port

    self.credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
    self.parameters  = pika.ConnectionParameters(ip, port, '/', self.credentials)
    self.connection  = pika.BlockingConnection(parameters=self.parameters)
    self.channel     = self.connection.channel()
    self.channel.queue_declare(queue='spy_queue', durable=True)
    self.channel.queue_declare(queue='trace_queue', durable=True)

    def live_spy_callback_rabbit(spy_live):
      self.channel.basic_publish(exchange='',
          routing_key='spy_queue',
          body=spy_live,
          properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
          ))

    def live_trace_callback_rabbit(trace_live):
      trace = trace_live.replace('\n', '')
      self.channel.basic_publish(exchange='',
          routing_key='trace_queue',
          body=trace,
          properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
          ))

    self.register_live_spy_callback(live_spy_callback_rabbit)
    self.register_live_trace_callback(live_trace_callback_rabbit)
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

chart = RabbitProducer(chart_name="rabbit_producer",
    rabbit_user="bob",
    rabbit_password="dobbs",
    ip="192.168.1.72",
    port=5672)

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
