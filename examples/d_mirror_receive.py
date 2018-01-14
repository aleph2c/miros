#!/usr/bin/env python3
import pika
import sys
import socket

class Connection():

  @staticmethod
  def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      # doesn't have to be reachable
      s.connect(('10.255.255.255', 1))
      IP = s.getsockname()[0]
    except:
      IP = '127.0.0.1'
    finally:
      s.close()
    return IP

  @staticmethod
  def get_blocking_connection(user, password, ip, port):
    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(ip, port, '/', credentials)
    connection = pika.BlockingConnection(parameters=parameters)
    return connection

class ReceiveConnections():
  def __init__(self, user, password):
    self.connection = Connection.get_blocking_connection(user, password, Connection.get_ip(), 5672)
    self.channel = self.connection.channel()
    self.channel.exchange_declare(exchange='mirror', exchange_type='direct')
    # destroy queue when done
    result = self.channel.queue_declare(exclusive=True)
    self.queue_name = result.method.queue
    self.channel.queue_bind(exchange='mirror', queue=self.queue_name, routing_key=Connection.get_ip())

    print(' [x] Waiting for logs. To exit press CTRL-C')
    def callback(ch, method, properties, body):
      self.callback(ch, method, properties, body)
    self.channel.basic_consume(callback, queue=self.queue_name, no_ack=True)

  def callback(self, ch, method, properties, body):
    print(" [x] {}:{}".format(method.routing_key, body.decode('utf8')))

  def start_consuming(self):
    self.channel.start_consuming()

  def stop_consuming(self):
    self.channel.stop_consuming()

#severities = sys.argv[1:]
#if not severities:
#  sys.stderr.write("Usage: {} [info] [warning] [error]\n".format(sys.argv[0]))
#  sys.exit(1)


input_ = ReceiveConnections('bob', 'dobbs')

input_.start_consuming()
