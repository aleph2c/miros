#!/usr/bin/env python3
import pika
import socket

'''
  Usage:
    Receives all messages transmitted from "c_emit_log_fanout.py"
    1) start up a couple of c_receive_logs_fanout.py sessions
    2) send a message

    > python3 c_emit_log_fanout.py <some message>

    Both receivers should see the emitted messages

  Demonstrates:
    * Publish Subscribe
    * Fanout exchange

  Monitoring:
    * to view the results with the RabbitMQ manager:
    <hostname>:15672 in browser

    where <hostname> is the results of your hostname command

'''


# Taken from Jamieson Becker
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


# create a connection and a channel
credentials = pika.PlainCredentials('bob', 'dobbs')
parameters = pika.ConnectionParameters(get_ip(), 5672, '/', credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()


# create an exchange and bind it to an exclusive queue
channel.exchange_declare(exchange='logs', exchange_type='fanout')
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL-C')


def callback(ch, method, properties, body):
  print(" [x] {!s}".format(body.decode('utf8')))


channel.basic_consume(callback,
    queue=queue_name,
    no_ack=True)
channel.start_consuming()
