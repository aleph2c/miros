import pika
from cryptography.fernet import Fernet
from miros.activeobject import Factory
from miros.event import signals, Event, return_status
from miros.hsm import pp
import time
from functools import wraps
import sys, socket

class Mirrored(Factory):

  def __init__(self, chart_name, rabbit_user, rabbit_password, ip, port):
    super().__init__(chart_name + '_' + Mirrored.get_ip())

    self.rabbit_user      = rabbit_user
    self.rabbit_password  = rabbit_password
    self.destination_ip   = ip
    self.destination_port = port

    credentials     = pika.PlainCredentials(rabbit_user, rabbit_password)
    parameters      = pika.ConnectionParameters(ip, port, '/', credentials)
    self.connection = pika.BlockingConnection(parameters=parameters)
    self.channel    = self.connection.channel()

    self.channel.exchange_declare(
        exchange='mirror_exchange',
        exchange_type='direct')

    result     = self.channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    # Our routing key is our IP address
    received_routing_key = Mirrored.get_ip().replace('.', '')
    print(received_routing_key)
    self.channel.queue_bind(
        exchange='mirror_exchange',
        queue=queue_name,
        routing_key=received_routing_key)

    def receive_callback(ch, method, properties, body):
      self.receive_message_from_network(
          ch,
          method,
          properties,
          body)

    self.channel.basic_consume(receive_callback,
        queue=queue_name,
        no_ack=True)

  def publish_over_network(self, message):
    self.channel.basic_publish(
        exchange='mirror_exchange',
        routing_key = self.destination_ip.replace('.',''),
        body=message)

  def receive_message_from_network(self, ch, method, properties, body):
    print(body.decode('utf8'))

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

if __name__ == "__main__":
  other_ip = ' '.join(sys.argv[1:])
  print("sending to {}".format(other_ip))
  mirrored = Mirrored(
      chart_name='chart',
      rabbit_user='bob',
      rabbit_password='dobbs',
      ip=other_ip,
      port = '5672')
  mirrored.publish_over_network("From Pi {}".format(Mirrored.get_ip()))
  mirrored.channel.start_consuming()


