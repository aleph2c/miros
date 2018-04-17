import os
import re
import time
import uuid
import socket
import netifaces  # pip3 install netifaces --user
import subprocess
import ipaddress
from g_pika_consumer import PikaTopicConsumer
from g_pika_producer import PikaTopicPublisher

import pprint
def pp(item):
  pprint.pprint(item)

class LocalAreaNetwork():
  '''Provides the addresses of the local area network (LAN)

  Example:
    lan = LocalAreaNetwork()
    lan.addresses  # => contains all the addresses that answered to ping on this LAN
    lan.this       # => this computer's primary IP address

  '''
  def __init__(self):
    self.this = self.get_working_ip_address()
    self.addresses = self.candidate_ip_addresses()

  def get_working_ip_address(self):
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
    ip_address = self.get_working_ip_address()
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
    working_address = self.get_working_ip_address()
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
    c = set([self.get_working_ip_address()])
    candidates = list(a - b ^ c)
    inet4 = self.get_ipv4_network()
    for host in inet4.hosts():
      shost = str(host)
      if shost in candidates:
        lan_ip_addresses.append(shost)
    return lan_ip_addresses

class RabbitNetwork():

  def __init__(self,
               rabbit_user,
               rabbit_password,
               routing_key,
               exchange_name,
               queue_name,
               encryption_key,
               addresses=None):

    self.queue_name = queue_name
    self.routing_key = routing_key
    self.exchange_name = exchange_name
    self.encryption_key = encryption_key

    if addresses is None:
      lan = LocalAreaNetwork()
      self.candidates = lan.addresses
    else:
      self.candidates = addresses

    self.rabbit_user = rabbit_user
    self.rabbit_password = rabbit_password
    self.urls, self.addresses = self.scout_candidates()

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
                    rabbit_user,
                    rabbit_password,
                    ip_address,
                    rabbit_port=None,
                    port=None,
                    connection_attempts=None,
                    heartbeat_interval=None):

    if port is None:
      port = 5672
    if connection_attempts is None:
      connection_attempts = 3
    if heartbeat_interval is None:
      heartbeat_interval = 3600

    amqp_url = \
      "amqp://{}:{}@{}:{}/%2F?connection_attempts={}&heartbeat_interval={}".format(
          rabbit_user,
          rabbit_password,
          ip_address,
          port,
          connection_attempts,
          heartbeat_interval)
    return amqp_url

  def scout_candidates(self):
    possible_amqp_urls = self.possible_amqp_urls(connection_attempts=1)
    scouting_amqp_urls = possible_amqp_urls[:]

    for amqp_url in possible_amqp_urls:
      thread = PikaTopicPublisher(
        amqp_url=amqp_url,
        routing_key=self.routing_key,
        publish_tempo_sec=0.01,
        exchange_name=self.exchange_name,
        queue_name=self.queue_name,
        encryption_key=self.encryption_key)

      thread.start_thread()
      thread.post_fifo(uuid.uuid4().hex.upper()[0:12])
      time.sleep(0.3)
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

if __name__ == '__main__':
  lan = LocalAreaNetwork()
  print(lan.this)
  print(lan.addresses)

  rn = RabbitNetwork(
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
