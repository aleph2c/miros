import os
import re
import time
import uuid
import pickle
import socket
import netifaces  # pip3 install netifaces --user
import functools
import subprocess
import ipaddress
from miros.event import Event
from g_pika_consumer import PikaTopicConsumer
from g_pika_producer import PikaTopicPublisher


import pprint
def pp(item):
  pprint.pprint(item)

class Attribute():
  def __init__(self):
    pass

class LocalAreaNetwork():
  '''Provides the ip_addresses of the local area network (LAN)

  Example:
    lan = LocalAreaNetwork()

    print(lan.addresses)  # => \
      ['192.168.1.66', '192.168.1.69', '192.168.1.70', '192.168.1.71', '192.168.1.75', '192.168.1.254']

    print(lan.this.address)  # => '192.168.1.75'

    print(lan.other.addresses)  # => \
      ['192.168.1.66', '192.168.1.69', '192.168.1.70', '192.168.1.71', '192.168.1.254']

    print(LocalAreaNetwork.get_working_ip_address())  # => '192.168.1.75'

  '''
  def __init__(self):
    self.this  = Attribute()
    self.other = Attribute()
    self.this.address = LocalAreaNetwork.get_working_ip_address()
    self.addresses = self.candidate_ip_addresses()
    self.other.addresses = list(set(self.addresses) - set([self.this.address]))

  @staticmethod
  def get_working_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      s.connect(('10.255.255.255', 1))
      ip = s.getsockname()[0]
    except:
      ip = '127.0.0.1'
    finally:
      s.close()
    return ip

  def get_ipv4_network(self):
    ip_address = LocalAreaNetwork.get_working_ip_address()
    netmask    = self.get_netmask_on_this_machine()
    inet4 = ipaddress.ip_network(ip_address + '/' + netmask, strict=False)
    return inet4

  def fill_arp_table(self):
    linux_cmd = 'ping -b {}'
    inet4 = self.get_ipv4_network()

    if inet4.num_addresses <= 256:
      broadcast_address = inet4[-1]
      fcmd = linux_cmd.format(broadcast_address)
      fcmd_as_list = fcmd.split(" ")
      try:
        ps = subprocess.Popen(fcmd_as_list, stdout=open(os.devnull, "wb"))
        ps.wait(2)
      except:
        ps.kill()
    return

  def ip_addresses_on_lan(self):
    wsl_cmd   = 'cmd.exe /C arp.exe -a'
    linux_cmd = 'arp -a'

    grep_cmd = 'grep -Po 192\.\d+\.\d+\.\d+'
    candidates = []

    for cmd in [wsl_cmd, linux_cmd]:
      cmd_as_list = cmd.split(" ")
      grep_as_list = grep_cmd.split(" ")
      output = ''
      try:
        ps = subprocess.Popen(cmd_as_list, stdout=subprocess.PIPE)
        output = subprocess.check_output(grep_as_list, stdin=ps.stdout, timeout=0.5)
        ps.wait()
        if output is not '':
          candidates = output.decode('utf-8').split('\n')
          if len(candidates) > 0:
            break
      except:
        # our windows command did not work on Linux
        pass
    return list(filter(None, candidates))

  def get_netmask_on_this_machine(self):
    interfaces = [interface for interface in netifaces.interfaces()]
    local_netmask = None
    working_address = LocalAreaNetwork.get_working_ip_address()
    for interface in interfaces:
      interface_network_types = netifaces.ifaddresses(interface)
      if netifaces.AF_INET in interface_network_types:
        if interface_network_types[netifaces.AF_INET][0]['addr'] == working_address:
          local_netmask = interface_network_types[netifaces.AF_INET][0]['netmask']
          break
    return local_netmask

  def ip_addresses_on_this_machine(self):
    interfaces = [interface for interface in netifaces.interfaces()]
    local_ip_addresses = []
    for interface in interfaces:
      interface_network_types = netifaces.ifaddresses(interface)
      if netifaces.AF_INET in interface_network_types:
        ip_address = interface_network_types[netifaces.AF_INET][0]['addr']
        local_ip_addresses.append(ip_address)
    return local_ip_addresses

  def candidate_ip_addresses(self):
    self.fill_arp_table()
    lan_ip_addresses = []
    a = set(self.ip_addresses_on_lan())
    b = set(self.ip_addresses_on_this_machine())
    c = set([LocalAreaNetwork.get_working_ip_address()])
    candidates = list(a - b ^ c)
    inet4 = self.get_ipv4_network()
    for host in inet4.hosts():
      shost = str(host)
      if shost in candidates:
        lan_ip_addresses.append(shost)
    return lan_ip_addresses

class RabbitHelper():
  CONNECTION_ATTEMPTS    = 3
  HEARTBEAT_INTERVAL_SEC = 3600
  PORT                   = 5672

  @staticmethod
  def make_amqp_url(ip_address,
               rabbit_user,
               rabbit_password,
               rabbit_port=None,
               connection_attempts=None,
               heartbeat_interval=None):
    '''Make a RabbitMq url.

      Example:
        amqp_url = \
          RabbitHelper.make_amqp_url(
              ip_address=192.168.1.1,
              rabbit_user='bob',
              rabbit_password='dobb',
              connection_attempts='3',
              heartbeat_interval='3600')

        print(amqp_url)  # => \
          'amqp://bob:dobbs@192.168.1.1:5672/%2F?connection_attempts=3&heartbeat_interval=3600'

    '''
    if rabbit_port is None:
      rabbit_port = RabbitHelper.PORT
    if connection_attempts is None:
      connection_attempts = RabbitHelper.CONNECTION_ATTEMPTS
    if heartbeat_interval is None:
      heartbeat_interval = RabbitHelper.HEARTBEAT_INTERVAL_SEC

    amqp_url = \
      "amqp://{}:{}@{}:{}/%2F?connection_attempts={}&heartbeat_interval={}".format(
          rabbit_user,
          rabbit_password,
          ip_address,
          rabbit_port,
          connection_attempts,
          heartbeat_interval)
    return amqp_url

class RabbitScout():
  '''Scouts a list of ip_addresses or your LAN ip_addresses for RabbitMq servers running clients
  with the correction encryption_key and routing_key.

  Example:
    rs = RabbitScout(
          rabbit_user='bob',
          rabbit_password='dobbs',
          routing_key='pub_thread.text',
          exchange_name='sex_change',
          queue_name='g_queue',
          encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=')

    print(rs.addresses)      # => ['192.168.1.69', '192.168.1.75']
    print(rs.this.address)   # => '192.168.1.75'
    print(rs.other.addresss) # => ['192.168.1.69']

    print(rs.urls) # => \
      [amqp://bob:dobbs@192.168.1.69:5672/%2F?connection_attempts=3&heartbeat_interval=3600',
      'amqp://bob:dobbs@192.168.1.75:5672/%2F?connection_attempts=3&heartbeat_interval=3600']

    print(rs.this.url) # => \
      'amqp://bob:dobbs@192.168.1.75:5672/%2F?connection_attempts=3&heartbeat_interval=3600'

    print(rs.other.urls) # => \
      [amqp://bob:dobbs@192.168.1.69:5672/%2F?connection_attempts=3&heartbeat_interval=3600']

  Notes:
    The RabbitScout determines is an address has a rabbitmq server with a client
    using the correct encryption_key and routing_key by starting a
    PikaTopicPublisher thread using URL which will will not try to reconnect if
    an error is detected.  It tries to establish a connection, but only waits
    the scout_timeout_sec (default of 0.3 second/address).  If the connection is
    not made the PikaTopicPublisher indicates this with a 'connect_error' flag.
    If this flag is detected the address is disqualified.

    If you notice that some of your addresses are not being picked up by the
    RabbRabbitScout increase the scout_timeout_sec parameter.  The downside of
    doing this is it will take more time to get through your list of searched
    IP addresses to find the other RabbitMq clients in the address list or on
    the LAN.

  '''

  CONNECTION_ATTEMPTS    = 3
  HEARTBEAT_INTERVAL_SEC = 3600
  PORT                   = 5672

  SCOUT_TEMPO_SEC        = 0.01
  SCOUT_TIMEOUT_SEC      = 0.4

  def __init__(self,
               rabbit_user,
               rabbit_password,
               routing_key,
               exchange_name,
               queue_name,
               encryption_key,
               addresses=None,
               rabbit_port=None,
               connection_attempts=None,
               heartbeat_interval=None,
               scout_timeout_sec=None):

    self.this  = Attribute()
    self.other = Attribute()

    self.queue_name = queue_name
    self.routing_key = routing_key
    self.exchange_name = exchange_name
    self.encryption_key = encryption_key

    if addresses is None:
      lan = LocalAreaNetwork()
      self.candidates = lan.addresses
    else:
      self.candidates = addresses

    if rabbit_port is None:
      self.rabbit_port = self.PORT

    if connection_attempts is None:
      self.connection_attempts = self.CONNECTION_ATTEMPTS

    if heartbeat_interval is None:
      self.heartbeat_interval = self.HEARTBEAT_INTERVAL_SEC

    if scout_timeout_sec is None:
      self._scout_timeout_sec = self.SCOUT_TIMEOUT_SEC

    self.rabbit_user = rabbit_user
    self.rabbit_password = rabbit_password
    self.this.address = LocalAreaNetwork.get_working_ip_address()
    self.urls, self.addresses = self.scout_candidates()
    self.this.url = self.make_amqp_url(ip_address=self.this.address)
    self.other.urls = list(set(self.urls) - set([self.this.url]))

  def possible_amqp_urls(self, connection_attempts=None, addresses=None):
    if connection_attempts is None:
      connection_attempts = connection_attempts
    if addresses is None:
      addresses = self.candidates
    amqp_urls = []
    for ip_address in addresses:
      amqp_url = self.make_amqp_url(
        rabbit_user=self.rabbit_user,
        rabbit_password=self.rabbit_password,
        ip_address=ip_address,
        connection_attempts=connection_attempts,
      )
      amqp_urls.append(amqp_url)
    return amqp_urls

  def make_amqp_url(self,
                    ip_address,
                    rabbit_user=None,
                    rabbit_password=None,
                    rabbit_port=None,
                    connection_attempts=None,
                    heartbeat_interval=None):

    if rabbit_user is None:
      rabbit_user = self.rabbit_user
    if rabbit_password is None:
      rabbit_password = self.rabbit_password
    if rabbit_port is None:
      rabbit_port = self.rabbit_port
    if connection_attempts is None:
      connection_attempts = self.connection_attempts
    if heartbeat_interval is None:
      heartbeat_interval = self.heartbeat_interval

    amqp_url = \
      RabbitHelper.make_amqp_url(
          ip_address=ip_address,
          rabbit_user=rabbit_user,
          rabbit_password=rabbit_password,
          connection_attempts=connection_attempts,
          heartbeat_interval=heartbeat_interval)
    return amqp_url

  def scout_candidates(self):
    possible_amqp_urls = self.possible_amqp_urls(connection_attempts=1)
    scouting_amqp_urls = possible_amqp_urls[:]

    for amqp_url in possible_amqp_urls:
      thread = PikaTopicPublisher(
        amqp_url=amqp_url,
        routing_key=self.routing_key,
        publish_tempo_sec=self.SCOUT_TEMPO_SEC,
        exchange_name=self.exchange_name,
        queue_name=self.queue_name,
        encryption_key=self.encryption_key)

      thread.start_thread()
      # send a unexpected message to make it harder to decrypt
      thread.post_fifo(uuid.uuid4().hex.upper()[0:12])
      time.sleep(self._scout_timeout_sec)
      thread.stop_thread()
      if thread.connect_error:
        scouting_amqp_urls.remove(amqp_url)

    candidate_amqp_urls = [
     re.sub(r"connection_attempts=\d+", "connection_attempts={}".format(3), candidate)
      for candidate in scouting_amqp_urls
    ]
    candidate_ip_addresses = [
        re.sub(r'.+@(.+):.+', r'\1', candidate)
        for candidate in scouting_amqp_urls
    ]
    return candidate_amqp_urls, candidate_ip_addresses

class MirosApiException(BaseException):
  pass

class MirosNets:

  TRACE_ROUTING_KEY = 'snoop.trace'
  SPY_ROUTING_KEY   = 'snoop.spy'

  MESH_EXCHANGE     = 'miros.mesh.exchange'
  TRACE_EXCHANGE    = 'miros.snoop.trace.exchange'
  SPY_EXCHANGE      = 'miros.snoop.spy.exchange'

  MESH_QUEUE   = 'miros.mesh.queue'
  TRACE_QUEUE  = 'miros.snoop.trace.queue'
  SPY_QUEUE    = 'miros.snoop.spy.queue'

  def __init__(self,
                miros_object,
                rabbit_user,
                rabbit_password,
                mesh_encryption_key,
                routing_key,
                on_mesh_rx=None,
                on_spy_rx=None,
                on_trace_rx=None,
                spy_snoop_encryption_key=None,
                trace_snoop_encryption_key=None):

    self.this = Attribute()
    self.mesh = Attribute()
    self.snoop = Attribute()
    self.snoop.spy = Attribute()
    self.snoop.trace = Attribute()

    self.mesh.encryption_key = mesh_encryption_key
    self._rabbit_user = rabbit_user
    self._rabbit_password = rabbit_password

    if spy_snoop_encryption_key is None:
      self.snoop.spy.encryption_key = mesh_encryption_key
    else:
      self.snoop.spy.encryption = spy_snoop_encryption_key

    if trace_snoop_encryption_key is None:
      self.snoop.trace.encryption_key = mesh_encryption_key
    else:
      self.snoop.trace.encryption = trace_snoop_encryption_key

    self.mesh.routing_key        = routing_key
    self.snoop.spy.routing_key   = routing_key + '.' + MirosNets.SPY_ROUTING_KEY
    self.snoop.trace.routing_key = routing_key + '.' + MirosNets.TRACE_ROUTING_KEY

    self.mesh.queue_name        = MirosNets.MESH_QUEUE
    self.snoop.spy.queue_name   = MirosNets.SPY_QUEUE
    self.snoop.trace.queue_name = MirosNets.TRACE_QUEUE

    self.mesh.exchange_name        = MirosNets.MESH_EXCHANGE
    self.snoop.spy.exchange_name   = MirosNets.SPY_EXCHANGE
    self.snoop.trace.exchange_name = MirosNets.TRACE_EXCHANGE

    self.mesh.on_message_callback = \
      functools.partial(MirosNets.on_mesh_message_callback,
        custom_rx_callback=on_mesh_rx)

    self.snoop.spy.on_message_callback =  \
      functools.partial(MirosNets.on_snoop_spy_message_callback,
        custom_rx_callback=on_spy_rx)

    self.snoop.trace.on_message_callback = \
      functools.partial(MirosNets.on_snoop_trace_message_callback,
        custom_rx_callback=on_trace_rx)

    def custom_serializer(obj):
      if isinstance(obj, Event):
        obj = Event.dumps(obj)
      pobj = pickle.dumps(obj)
      return pobj

    def custom_deserializer(ppobj):
      pobj = pickle.loads(ppobj)
      try:
        obj = Event.loads(pobj)
      except:
        obj = pobj

      return obj

    self.mesh.serializer = custom_serializer
    self.mesh.deserializer = custom_deserializer

    api_ok = True
    api_ok &= hasattr(miros_object.__class__, 'post_fifo')
    api_ok &= hasattr(miros_object.__class__, 'post_lifo')
    api_ok &= hasattr(miros_object.__class__, 'start_at')
    api_ok &= hasattr(miros_object.__class__, 'register_live_spy_callback')
    api_ok &= hasattr(miros_object.__class__, 'register_live_trace_callback')

    if api_ok is False:
      raise MirosApiException("miros_object {} doesn't have the required attributes".format(miros_object))

    rabbit_scout = RabbitScout(
                    rabbit_user = self._rabbit_user,
                    rabbit_password=self._rabbit_password,
                    routing_key=self.mesh.routing_key,
                    exchange_name=self.mesh.exchange_name,
                    queue_name=self.mesh.queue_name,
                    encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=')

    self._urls = rabbit_scout.urls
    self.this.url = rabbit_scout.this.url
    self.build_mesh_network()
    self.build_snoop_networks()

    self.snoop.spy.enabled = False
    self.snoop.trace.enabled = False
    
    self.mesh.started = False
    self.snoop.spy.started = False
    self.snoop.trace.started = False

  def enable_snoop_spy(self):
    self.snoop.spy.enabled = True

  def enable_snoop_trace(self):
    self.snoop.trace.enabled = True

  def start_threads(self):

    if self.mesh.started is False:
      for producer in self.mesh.producers:
        producer.start_thread()
      self.mesh.consumer.start_thread()
      self.mesh.started = True

    if self.snoop.spy.started is False and self.snoop.spy.enabled:
      for spy_producer in self.snoop.spy.producers:
        spy_producer.start_thread()
      self.snoop.spy.consumer.start_thread()
      self.snoop.spy.enabled = True

    if self.snoop.trace.started is False and self.snoop.trace.enabled:
      for trace_producer in self.snoop.trace.producers:
        trace_producer.start_thread()
      self.snoop.trace.consumer.start_thread()
      self.snoop.trace.enabled = True

  def stop_threads(self):
    if self.mesh.started is True:
      for producer in self.mesh.producers:
        producer.stop_thread()
      self.mesh.consumer.stop_thread()
      self.mesh.started = False

    if self.snoop.spy.started is True:
      for spy_producer in self.snoop.spy.producers:
        spy_producer.stop_thread()
      self.snoop.spy.consumer.stop_thread()
      self.snoop.spy.enabled = False

    if self.snoop.trace.started is True:
      for trace_producer in self.snoop.trace.producers:
        trace_producer.stop_thread()
      self.snoop.trace.consumer.stop_thread()
      self.snoop.trace.enabled = False

  def build_mesh_network(self):
    self.mesh.producers = [
      PikaTopicPublisher(
        amqp_url=amqp_url,
        routing_key=self.mesh.routing_key,
        publish_tempo_sec=1.0,
        exchange_name=self.mesh.exchange_name,
        queue_name=self.mesh.queue_name,
        serialization_function=self.mesh.serializer,
        encryption_key=self.mesh.encryption_key)
      for amqp_url in self._urls
    ]

    self.mesh.consumer = \
      PikaTopicConsumer(
        amqp_url=self.this.url,
        routing_key=self.mesh.routing_key,
        exchange_name=self.mesh.exchange_name,
        queue_name=self.mesh.queue_name,
        message_callback=self.mesh.on_message_callback,
        deserialization_function=self.mesh.deserializer,
        encryption_key=self.mesh.encryption_key)

  def build_snoop_networks(self):

    self.snoop.spy.producers = [
      PikaTopicPublisher(
        amqp_url=amqp_url,
        routing_key=self.snoop.spy.routing_key,
        publish_tempo_sec=1.0,
        exchange_name=self.snoop.spy.exchange_name,
        queue_name=self.snoop.spy.queue_name,
        encryption_key=self.snoop.spy.encryption_key)
      for amqp_url in self._urls
    ]

    self.snoop.spy.consumer = \
      PikaTopicConsumer(
        amqp_url=self.this.url,
        routing_key=self.snoop.spy.routing_key,
        exchange_name=self.snoop.spy.exchange_name,
        queue_name=self.snoop.spy.queue_name,
        message_callback=self.snoop.spy.on_message_callback,
        encryption_key=self.snoop.spy.encryption_key)

    self.snoop.trace.producers = [
      PikaTopicPublisher(
        amqp_url=amqp_url,
        routing_key=self.snoop.trace.routing_key,
        publish_tempo_sec=1.0,
        exchange_name=self.snoop.trace.exchange_name,
        queue_name=self.snoop.trace.queue_name,
        encryption_key=self.snoop.trace.encryption_key)
      for amqp_url in self._urls
    ]

    self.snoop.trace.consumer = \
      PikaTopicConsumer(
        amqp_url=self.this.url,
        routing_key=self.snoop.trace.routing_key,
        exchange_name=self.snoop.trace.exchange_name,
        queue_name=self.snoop.trace.queue_name,
        message_callback=self.snoop.trace.on_message_callback,
        encryption_key=self.snoop.trace.encryption_key)

  @staticmethod
  def on_mesh_message_callback(unused_channel, basic_deliver, properties, body, custom_rx_callback):
    if custom_rx_callback is None:
      print("Received mesh message # {} from {}: {}".format(
            basic_deliver.delivery_tag, properties.app_id, body))
    else:
      custom_rx_callback(unused_channel, basic_deliver, properties, body)

  @staticmethod
  def on_snoop_spy_message_callback(unused_channel, basic_deliver, properties, body, custom_rx_callback):
    if custom_rx_callback is None:
      print("Received snoop-spy message # {} from {}: {}".format(
            basic_deliver.delivery_tag, properties.app_id, body))
    else:
      custom_rx_callback(unused_channel, basic_deliver, properties, body, custom_rx_callback)

  @staticmethod
  def on_snoop_trace_message_callback(unused_channel, basic_deliver, properties, body, custom_rx_callback):
    if custom_rx_callback is None:
      print("Received snoop-spy message # {} from {}: {}".format(
            basic_deliver.delivery_tag, properties.app_id, body))
    else:
      custom_rx_callback(unused_channel, basic_deliver, properties, body, custom_rx_callback)

  def transmit(self, event):
    for producer in self.mesh.producers:
      producer.post_fifo(event)

  def broadcast_spy(self, message):
    for producer in self.snoop.spy.producers:
      producer.post_fifo(message)

  def broadcast_trace(self, message):
    for producer in self.snoop.trace.producers:
      producer.post_fifo(message)

  def change_mesh_encyption_key(self, encryption_key):
    for producer in self.mesh.producers:
      producer.change_encyption_key(encryption_key)
    self.mesh.consumer.change_encyption_key(encryption_key)

  def change_spy_encyption_key(self, encryption_key):
    for producer in self.snoop.spy.producers:
      producer.change_encyption_key(encryption_key)
    self.snoop.spy.consumer.change_encyption_key(encryption_key)

  def change_trace_encyption_key(self, encryption_key):
    for producer in self.snoop.trace.producers:
      producer.change_encyption_key(encryption_key)
    self.snoop.trace.consumer.change_encyption_key(encryption_key)

if __name__ == '__main__':
  from miros.activeobject import ActiveObject
  lan = LocalAreaNetwork()
  print(lan.this.address)
  print(lan.addresses)
  print(lan.other.addresses)

  rn = RabbitScout(
      'bob',
      'dobbs',
      routing_key='pub_thread.text',
      exchange_name='sex_change',
      queue_name='g_queue',
      encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=',
      addresses=lan.addresses,
  )
  pp(rn.urls)
  pp(rn.addresses)
  pp(rn.this.url)
  pp(rn.other.urls)

  ao = ActiveObject(name='testing')

  def custom_on_message_callback(unused_channel, basic_deliver, properties, body):
      print("Custom rx, Received mesh message # {} from {}: {}".format(basic_deliver.delivery_tag, properties.app_id, body))

  mn = MirosNets(miros_object = ao,
                  rabbit_user='bob',
                  rabbit_password='dobbs',
                  mesh_encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=',
                  routing_key="testing",
                  on_mesh_rx=custom_on_message_callback,
                  )
  pp(mn._urls)

  print("transmitting something")
  mn.start_threads()
  for i in range(100):
    mn.transmit("bob {}".format(i))
    if i % 53 is 0:
      mn.stop_threads()
    if i % 54 is 0:
      mn.start_threads()
    time.sleep(0.1)
  time.sleep(1)
