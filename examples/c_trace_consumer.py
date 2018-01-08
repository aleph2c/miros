#!/usr/bin/env python3

'''
  Usage:
    Receive spy/trace streams from an HSM running on a different machine
    1) to the foreign hsm consumer:

    > python3 b_trace_consumer.p

    NOTE: if you run more than one of these programs in your terminal, the
    spy/trace logs will be shared between them.  Neither will have a full
    picture about what is happening of the foreign hsm.


  Demonstrates:
    * Ability the ForeignHsm class
    * Monitoring an HSM on another machine

  Monitoring:
    * to view your queus with the RabbitMQ manager:
    localhost:15672 in browser

'''
import pika
import socket
from miros.foreign import ForeignHsm
from miros.hsm import pp
from cryptography.fernet import Fernet
from functools import wraps


class LocalConsumer():
  def __init__(self, rabbit_user, rabbit_password):

    # rabbit related
    self.rabbit_user     = rabbit_user
    self.rabbit_password = rabbit_password
    credentials          = pika.PlainCredentials('bob', 'dobbs')
    parameters           = pika.ConnectionParameters(LocalConsumer.get_ip(), 5672, '/', credentials)
    self.connection      = pika.BlockingConnection(parameters=parameters)
    self.channel         = self.connection.channel()

    # keep a count so we can exit the program
    self.count       = 0
    # make a ForeignHsm to track activity on another machine
    self.foreign_hsm = ForeignHsm()

    @LocalConsumer.decrypt
    def spy_callback(ch, method, properties, body):
      '''create a spy_callback function received messages in the queue'''
      foreign_spy_item = body
      self.foreign_hsm.append_to_spy(foreign_spy_item)
      print(" [x] Spy: {!s}".format(foreign_spy_item))
      ch.basic_ack(delivery_tag = method.delivery_tag)

    @LocalConsumer.decrypt
    def trace_callback(ch, method, properties, body):
      '''create a trace_callback function received messages in the queue'''
      foreign_trace_item = body
      self.foreign_hsm.append_to_trace(foreign_trace_item)
      print(" [x] Trace: {!s}".format(foreign_trace_item))
      ch.basic_ack(delivery_tag = method.delivery_tag)

    def timeout_callback():
      '''callback for outputting the foreign trace and exiting the program'''
      spy = self.foreign_hsm.spy()
      if len(spy) is not 0:
        pp(self.foreign_hsm.spy())
        print(self.foreign_hsm.trace())
      # stop processing or reconnect this callback to a timer
      self.count += 1
      if self.count >= 30:
        self.channel.stop_consuming()
      else:
        self.connection.add_timeout(deadline=1, callback_method=timeout_callback)
        self.foreign_hsm.clear_spy()
        self.foreign_hsm.clear_trace()

    # Add the timeout callback
    self.connection.add_timeout(deadline=10, callback_method=timeout_callback)

    # register the spy_callback and trace_callback with a queue
    self.channel.basic_consume(spy_callback,   queue='spy_queue')
    self.channel.basic_consume(trace_callback, queue='trace_queue')

  def start(self):
    self.channel.start_consuming()

  @staticmethod
  def get_ip():
    '''LocalConsumer.get_ip()'''
    ip = '127.0.0.1'
    s  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      # doesn't have to be reachable
      s.connect(('10.255.255.255', 1))
      ip = s.getsockname()[0]
    finally:
      s.close()
    return ip

  @staticmethod
  def decrypt(fn):
    @wraps(fn)
    def _decrypt(ch, method, properties, cyphertext):
      '''LocalConsumer.decrypt()'''
      key = b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg='
      f = Fernet(key)
      plain_text = f.decrypt(cyphertext).decode()
      fn(ch, method, properties, plain_text)
    return _decrypt


if __name__ == "__main__":
  local_consumer = LocalConsumer(rabbit_user='bob', rabbit_password='dobbs')
  local_consumer.start()