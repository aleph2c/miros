import socket
import netifaces  # pip3 install netifaces --user
import subprocess
from g_pika_consumer import PikaTopicConsumer
from g_pika_producer import PikaTopicPublisher

def get_working_ip_address():
  '''
  Get the ip of this computer:

  Example:
    my_ip = NetworkTool.get_working_ip_address()

  '''
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    s.connect(('10.255.255.255', 1))
    ip = s.getsockname()[0]
  except:
    ip = '127.0.0.1'
  finally:
    s.close()
  return ip

def ip_addresses_on_lan():
  '''
  The Windows Linux Subsystem is currently broken, it does not support a lot
  of Linux networking commands - so, we can't use the nice tooling provided
  by the community.  Instead I call out to the cmd.exe file of DOS and send it
  the DOS version of arp to get a list of IP addresses on the LAN.

  The 'grep -Po 192\.\d+\.\d+\.\d+' applies the Perl regular expression
  with matching output only to our stream.  This will return all of the IP
  addresses in the class C family (192.xxx.xxx.xxx)

  Example:
    ip_addresses = NetworkTool.ip_addresses_on_lan()
  '''
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

def ip_addresses_on_this_machine():
  '''
  There are situations where we would like to know all of the IP addresses
  connected to this one machine.

  Example:
    list_of_my_ips_address = NetworkTool.ip_addresses_on_this_machine()
  '''
  interfaces = [interface for interface in netifaces.interfaces()]
  local_ip_addresses = []
  for interface in interfaces:
    interface_network_types = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in interface_network_types:
      ip_address = interface_network_types[netifaces.AF_INET][0]['addr']
      local_ip_addresses.append(ip_address)
  return local_ip_addresses

if __name__ == '__main__':
  print("IP addresses LAN {}".format(ip_addresses_on_lan()))
  print("IP addresses on this machine {}".format(ip_addresses_on_this_machine()))
  print("Working IP address on this machine {}".format(get_working_ip_address()))

