#!/usr/bin/env python3
import pika
import sys
from types import SimpleNamespace

'''
  Usage:
    Sends a routed message (set from cli) to "d_receive_logs_direct.py"
    1) start up a couple of d_receive_logs_direct.py sessions with different
       routes:
    > python3 d_receive_logs_direct.py info warning error
    > python3 d_receive_logs_direct.py error

    2) send routed messages:

    > python3 d_emit_log_direct.py error all_should_see_this
    > python3 d_emit_log_direct.py info first_should_see_this


  Demonstrates:
    * Publish Subscribe
    * Direct exchange


    * to view the results with the RabbitMQ manager:
    <hostname>:15672 in browser

    where <hostname> is the results of your hostname command

'''
import socket

class Connections():
  def __init__(self, base, start, end, user, password):
    self.possible_ips = [base+str(i) for i in [*range(start,end)]]
    targets = Connections.scout_targets(self.possible_ips, user, password)
    self.channels = Connections.get_channels(self.possible_ips, user, password)

  def message_to_other_channels(self, message):
    for channel in self.channels:
      ip = channel.extension.ip_address
      # find target in channel
      channel.basic_publish(exchange='mirror',
          routing_key=ip, body=message)
      print(" [x] Sent \"{}\" to {}".format(message, ip))

  @staticmethod
  def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      s.connect(('10.255.255.255', 1))
      ip = s.getsockname()[0]
    except:
      ip = '127.0.0.1'
    finally:
      s.close()
    return ip

  @staticmethod
  def scout_targets(targets, user, password):
    possible_targets = targets[:]
    possible_targets.remove(Connections.get_ip())
    credentials = pika.PlainCredentials(user, password)
    message = 'discovery probe'

    for target in possible_targets:
      parameters = pika.ConnectionParameters(target, 5672, '/', credentials)
      try:
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange='mirror', exchange_type='direct')
        channel.basic_publish(exchange='mirror', routing_key=target, body=message)
        print(" [x] Sent \"{}\" to {}".format(message, target))
        connection.close()
      except:
        possible_targets.remove(target)
    return possible_targets

  @staticmethod
  def get_channels(targets, user, password):
    channels = []
    credentials = pika.PlainCredentials(user, password)
    for target in targets:
      parameters = pika.ConnectionParameters(target, 5672, '/', credentials)
      try:
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange='mirror', exchange_type='direct')
        channel.extension = SimpleNamespace()
        setattr(channel.extension, 'ip_address', target)
        channels.append(channel)
      except:
        pass
    return channels

rabbit = Connections(base="192.168.1.", start=70, end=80, user="bob", password="dobbs")
rabbit.message_to_other_channels(channels, "an actual message")
