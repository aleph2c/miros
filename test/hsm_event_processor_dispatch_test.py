import pytest
import traceback
from miros.event import ReturnStatus, Signal, signals, Event, return_status
from miros.hsm   import HsmEventProcessor, HsmTopologyException
import pprint
def pp(item):
  print("")
  pprint.pprint(item)

def reflect(hsm=None,e=None):
  '''
  This will return the callers function name as a string:
  Example:

    def example_function():
      return reflect()

    print(example_function) #=> "example_function"

  '''
  fnt  = traceback.extract_stack(None,2)
  fnt1 = fnt[0]
  fnt2 = fnt1[2]
  return fnt2
################################################################################
#                             Dispatch Graph A1                                #
################################################################################
'''           The following state chart is used to test topology A

                            +- graph_a1_s1 -+
                            |               +-----+
                            |               |     |
                            |               |     a
                            |               |     |
                            |               <-----+
                            +---------------+

This is used for testing the type A topology in the trans_ method of the Hsm
class.
  * test_trans_topology_a_1 (diagram)
'''
def dispatch_graph_a1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    status = chart.trans(dispatch_graph_a1_s1)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status
################################################################################
#                             Dispatch Graph B1                                #
################################################################################
'''           The following state chart is used to test topology B

                       +------- graph_b1_s1 -----s-----+
                       |  +---- graph_b1_s2 -----t-+   |
                       |  |  +- graph_b1_s3 -+     |   |
                       |  |  |               |   +-+   |
                       |  |  |               <-b-+ <-a-+
                       |  |  +---------------+     |   |
                       |  +------------------------+   |
                       +-------------------------------+

This is used for testing the type B topology in the trans_ method of the Hsm
class.
  * test_trans_topology_b1_1 - start in graph_b1_s2 (diagram)
  * test_trans_topology_b1_2 - start in graph_b1_s3 (diagram)
'''
def dispatch_graph_b1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    status = chart.trans(dispatch_graph_b1_s2)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_b1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.B):
    status = chart.trans(dispatch_graph_b1_s3)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_b1_s1
  return status

def dispatch_graph_b1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_b1_s2
  return status
################################################################################
#                             Dispatch Graph C1                                #
################################################################################
'''           The following state chart is used to test topology C

                       +-graph_c1_s1-+   +-graph_c1_s2-+
                       |             |   |             |
                       |             +-a->             |
                       |             <-a-+             |
                       |             |   |             |
                       +-------------+   +-------------+

This is used for testing the type C topology in the trans_ method of the Hsm
class.
  * test_trans_topology_c1_1 (diagram)
  * test_trans_topology_c1_2 (diagram)
'''
def dispatch_graph_c1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_c1_s2)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_c1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_c1_s1)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status
################################################################################
#                             Dispatch Graph C2                                #
################################################################################
'''           The following state chart is used to test topology C

                    +------------- graph_c2_s1 -----------+
                    |   +-graph_c2_s2-+   +-graph_c2_s3-+ |
                    | * |             |   |             | |
                    | | |             +-a->             | |
                    | +->             <-a-+             | |
                    |   |             |   |             | |
                    |   +-------------+   +-------------+ |
                    +-------------------------------------+

This is used for testing the type C topology within another state, in the trans_
method of the Hsm class.
  * test_trans_topology_c2_1 (diagram)
  * test_trans_topology_c2_2 (diagram)
'''
def dispatch_graph_c2_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    chart.trans(dispatch_graph_c2_s2)
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_c2_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_c2_s3)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_c2_s1
  return status

def dispatch_graph_c2_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_c2_s2)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_c2_s1
  return status
################################################################################
#                             Dispatch Graph D1                                #
################################################################################
'''           The following state chart is used to test topology D

                       +------- graph_d1_s1 -----s-----+
                       |  +---- graph_d1_s2 -----t-+   |
                       |  |  +- graph_d1_s3 -+     |   |
                       |  |  |               |   +->   |
                       |  |  |               +-b-+ +-a->
                       |  |  +---------------+     |   |
                       |  +------------------------+   |
                       +-------------------------------+

This is used for testing the type D topology in the trans_ method of the Hsm
class.
  * test_trans_topology_d1_1 - start in graph_d1_s2 (diagram)
  * test_trans_topology_d1_2 - start in graph_d1_s3 (diagram)
'''
def dispatch_graph_d1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_d1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_d1_s1)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_d1_s1
  return status

def dispatch_graph_d1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.B):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_d1_s2)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_d1_s2
  return status
################################################################################
#                             Dispatch Graph E1                                #
################################################################################
'''           The following state chart is used to test topology E

                     +---------- graph_e1_s1 -----------+
                     |\e (print('handled")              | 
                     | +-------- graph_e1_s2 -------+   |
                     | | +------ graph_e1_s3 -----+ |   |
                     | | | +---- graph_e1_s4 ---+ | |   |
                     | | | |  +- graph_e1_s5 -+ | | |   |
                     | | | |  |               | | | |   |
                     | +-b->  |               <-----a---+
                     | | | |  |               | | | |   |
                     | | +c>  +---------------+ | | |   |
                     +d> | +--------------------+ | |   |
                     | | +------------------------+ |   |
                     | +----------------------------+   |
                     +----------------------------------+
This is used for testing the type E topology in the tran|_ m|thod of the Hsm
class.
  * test_trans_topology_e1_1 - start in graph_e1_s5 (diagram - a)
  * test_trans_topology_e1_2 - start in graph_e1_s5 (diagram - b)
  * test_trans_topology_e1_3 - start in graph_e1_s5 (diagram - c)
  * test_trans_topology_e1_3 - start in graph_e1_s5 (diagram - d)
  * test_trans_topology_e1_4 - start in graph_e1_s5 (diagram - d)
  * test_trans_topology_e1_5 - start in graph_e1_s5 (diagram - e)
'''
def dispatch_graph_e1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_e1_s5)
  elif(e.signal == signals.D):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_e1_s2)
  elif(e.signal == signals.E):
    chart.spy_log.append("{}:{}:Hook".format(e.signal_name, reflect(chart,e)))
    print("handled")
    status = return_status.HANDLED
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_e1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.B):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_e1_s4)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_e1_s1
  return status

def dispatch_graph_e1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.C):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = chart.trans(dispatch_graph_e1_s4)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_e1_s2
  return status

def dispatch_graph_e1_s4(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_e1_s3
  return status

def dispatch_graph_e1_s5(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_e1_s4
  return status

################################################################################
#                             Dispatch Graph F1                                #
################################################################################
'''           The following state chart is used to test topology F

                   +------------------------------------- f1_s1 --------------+
   +-f1_s0-+       |                                                          |
   |       |       |              +----------------------f1_s22 ----------+   |
   |       +----------c----------->                                       |   |
   |       |       |              | +--------------------f1_s3 ---------+ |   |
   |       |       |  +-f1_s21-+  | |  +-f1_s31--+    +----f1_s32-----+ | |   |
   +-------+       |  |        |  | |  |         |    |  +-f1_s321--+ | | |   |
                   |  |        |  | |  |         |    |  |          | | | |   |
                   |  |        |  | |  +---+-----+    |  |          | | | |   |
                   |  |        |  | |      +-----a------->          | | | |   |
                   |  |        |  | |                 |  |          | | | |   |
                   |  |        |  | |      +-----b---->  +----------+ | | |   |
                   |  +---+----+  | |      |          +---------------+ | |   |
                   |      |       | +------|----------------------------+ |   |
                   |      +----------------+                              |   |
                   |              +---------------------------------------+   |
                   |                                                          |
                   +----------------------------------------------------------+


This is used for testing the type E topology in the trans_ method of the Hsm
class.
  * test_trans_topology_f1_1 - start in graph_f1_s31 (diagram -> a)
  * test_trans_topology_f1_2 - start in graph_f1_s21 (diagram -> b)
  * test_trans_topology_f1_3 - start in graph_f1_s0  (diagram -> c)
'''
def dispatch_graph_f1_s0(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.C):
    status = chart.trans(dispatch_graph_f1_s22)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_f1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_f1_s21(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.B):
    status = chart.trans(dispatch_graph_f1_s32)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_f1_s1
  return status

def dispatch_graph_f1_s22(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_f1_s1
  return status

def dispatch_graph_f1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_f1_s22
  return status

def dispatch_graph_f1_s31(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    status = chart.trans(dispatch_graph_f1_s321)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_f1_s3
  return status

def dispatch_graph_f1_s32(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_f1_s3
  return status

def dispatch_graph_f1_s321(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_f1_s32
  return status

################################################################################
#                             Dispatch Graph G1                                #
################################################################################
'''           The following state chart is used to test topology G

                  +-------------------------------- g1_s1 --------------+
   +---g1_s0---+  |                                                     |
   |+-g1_s01--+|  |                      +---------g1_s22 ----------+   |
   ||         ++-----c------------------->                          |   |
   ||         ||  |                      | +-------g1_s3 ---------+ |   |
   |+---------+|  | +-------g1_s21----+  | |    +----g1_s32-----+ | |   |
   +-----------+  | | +--g1_s211-----+|  | |    |  +-g1_s321--+ | | |   |
                  | | |+-g1_s2111+   ||  | |    |  |          | | | |   |
                  | | ||         |   ||  | |    |  |          | | | |   |
                  | | ||         |   |+-------b---->          | | | |   |
                  | | ||         |   ||  | |    |  |          | | | |   |
                  | | ||         |   ||  | |    |  |          | | | |   |
                  | | ||         |   ||  | |  +---->          | | | |   |
                  | | ||         |   ||  | |  | |  |          | | | |   |
                  | | |++--------+   ||  | |  | |  |          | | | +-d->
                  | | +-|------------+|  | |  | |  +----------+ | | |   |
                  | +---|-------------+  | |  | +---------------+ | |   |
                  |     |                | +--|-------------------+ |   |
                  |     +------------a--------+                     |   |
                  |                      +--------------------------+   |
                  |                                                     |
                  +-----------------------------------------------------+


This is used for testing the type E topology in the trans_ method of the Hsm
class.
  * test_trans_topology_g1_1 - start in graph_g1_s211 (diagram -> a)
  * test_trans_topology_g1_2 - start in graph_g1_s211 (diagram -> b)
  * test_trans_topology_g1_3 - start in graph_g1_s01  (diagram -> a)
  * test_trans_topology_g1_4 - start in graph_g1_s321 (diagram -> d)
'''
def dispatch_graph_g1_s0(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status
def dispatch_graph_g1_s01(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.C):
    status = chart.trans(dispatch_graph_g1_s22)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_g1_s0
  return status

def dispatch_graph_g1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

def dispatch_graph_g1_s21(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.B):
    status = chart.trans(dispatch_graph_g1_s321)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_g1_s1
  return status

def dispatch_graph_g1_s211(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_g1_s21
  return status

def dispatch_graph_g1_s2111(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.A):
    status = chart.trans(dispatch_graph_g1_s321)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_g1_s211
  return status

def dispatch_graph_g1_s22(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  elif(e.signal == signals.D):
    status = chart.trans(dispatch_graph_g1_s1)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_g1_s1
  return status

def dispatch_graph_g1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_g1_s22
  return status

def dispatch_graph_g1_s32(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_g1_s3
  return status

def dispatch_graph_g1_s321(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
  elif(e.signal == signals.REFLECTION_SIGNAL):
    # We are no longer going to return a ReturnStatus object
    # instead we write the function name as a string
    status = reflect(chart,e)
  else:
    chart.spy_log.append("{}:{}".format(e.signal_name, reflect(chart,e)))
    status, chart.temp.fun = return_status.SUPER, dispatch_graph_g1_s32
  return status

@pytest.fixture
def spy_chart(request):
  chart = HsmEventProcessor()
  spy   = []
  chart.augment(other=spy, name="spy_log")
  Signal().append("A")
  Signal().append("B")
  Signal().append("C")
  Signal().append("D")
  Signal().append("E")
  Signal().append("F")
  yield chart
  del spy
  del chart

# grep test name to view diagram
@pytest.mark.dispatch
@pytest.mark.topology_a
def test1_trans_topology_a(spy_chart):
  chart = spy_chart
  expected_behavior = \
 ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_a1_s1',
  'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  'INIT_SIGNAL:dispatch_graph_a1_s1',
  'EXIT_SIGNAL:dispatch_graph_a1_s1',
  'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  'INIT_SIGNAL:dispatch_graph_a1_s1']

  chart.start_at(dispatch_graph_a1_s1)
  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  assert(chart.spy_log == expected_behavior)

# grep test name to view diagram
@pytest.mark.dispatch
@pytest.mark.topology_a
def test_trans_topology_a_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
 ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_a1_s1',
  'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  'INIT_SIGNAL:dispatch_graph_a1_s1',
  'EXIT_SIGNAL:dispatch_graph_a1_s1',
  'ENTRY_SIGNAL:dispatch_graph_a1_s1',
  'INIT_SIGNAL:dispatch_graph_a1_s1']

  chart.start_at(dispatch_graph_a1_s1)
  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_b
def test_trans_topology_b1_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s1',
     'ENTRY_SIGNAL:dispatch_graph_b1_s1',
     'ENTRY_SIGNAL:dispatch_graph_b1_s2',
     'INIT_SIGNAL:dispatch_graph_b1_s2',
     'A:dispatch_graph_b1_s2',
     'EXIT_SIGNAL:dispatch_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s2',
     'ENTRY_SIGNAL:dispatch_graph_b1_s2',
     'INIT_SIGNAL:dispatch_graph_b1_s2']
  chart.start_at(dispatch_graph_b1_s2)
  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_b
def test_trans_topology_b1_2(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s1',
     'ENTRY_SIGNAL:dispatch_graph_b1_s1',
     'ENTRY_SIGNAL:dispatch_graph_b1_s2',
     'ENTRY_SIGNAL:dispatch_graph_b1_s3',
     'INIT_SIGNAL:dispatch_graph_b1_s3',
     'B:dispatch_graph_b1_s3',
     'EXIT_SIGNAL:dispatch_graph_b1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_b1_s3',
     'ENTRY_SIGNAL:dispatch_graph_b1_s3',
     'INIT_SIGNAL:dispatch_graph_b1_s3']
  chart.start_at(dispatch_graph_b1_s3)
  event  = Event(signal=signals.B)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_c
def test_trans_topology_c1_1(spy_chart):
  chart   = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c1_s1',
     'ENTRY_SIGNAL:dispatch_graph_c1_s1',
     'INIT_SIGNAL:dispatch_graph_c1_s1',
     'A:dispatch_graph_c1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c1_s1',
     'EXIT_SIGNAL:dispatch_graph_c1_s1',
     'ENTRY_SIGNAL:dispatch_graph_c1_s2',
     'INIT_SIGNAL:dispatch_graph_c1_s2']
  event = Event(signal = signals.A)
  chart.start_at(dispatch_graph_c1_s1)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_c
def test_trans_topology_c1_2(spy_chart):
  chart   = spy_chart
  event = Event(signal = signals.A)
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c1_s2',
     'ENTRY_SIGNAL:dispatch_graph_c1_s2',
     'INIT_SIGNAL:dispatch_graph_c1_s2',
     'A:dispatch_graph_c1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c1_s2',
     'EXIT_SIGNAL:dispatch_graph_c1_s2',
     'ENTRY_SIGNAL:dispatch_graph_c1_s1',
     'INIT_SIGNAL:dispatch_graph_c1_s1']
  chart.start_at(dispatch_graph_c1_s2)
  chart.dispatch(e = event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_c
def test_trans_topology_c2_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c2_s1',
     'ENTRY_SIGNAL:dispatch_graph_c2_s1',
     'ENTRY_SIGNAL:dispatch_graph_c2_s2',
     'INIT_SIGNAL:dispatch_graph_c2_s2',
     'A:dispatch_graph_c2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c2_s2',
     'EXIT_SIGNAL:dispatch_graph_c2_s2',
     'ENTRY_SIGNAL:dispatch_graph_c2_s3',
     'INIT_SIGNAL:dispatch_graph_c2_s3']

  event = Event(signal = signals.A)
  chart.start_at(dispatch_graph_c2_s2)
  chart.dispatch(e = event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_c
def test_trans_topology_c2_2(spy_chart):
  chart   = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c2_s1',
     'ENTRY_SIGNAL:dispatch_graph_c2_s1',
     'ENTRY_SIGNAL:dispatch_graph_c2_s3',
     'INIT_SIGNAL:dispatch_graph_c2_s3',
     'A:dispatch_graph_c2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_c2_s3',
     'EXIT_SIGNAL:dispatch_graph_c2_s3',
     'ENTRY_SIGNAL:dispatch_graph_c2_s2',
     'INIT_SIGNAL:dispatch_graph_c2_s2']
  chart.start_at(dispatch_graph_c2_s3)
  event = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_d
def test_trans_topology_d1_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_d1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_d1_s1',
     'ENTRY_SIGNAL:dispatch_graph_d1_s1',
     'ENTRY_SIGNAL:dispatch_graph_d1_s2',
     'INIT_SIGNAL:dispatch_graph_d1_s2',
     'A:dispatch_graph_d1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_d1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_d1_s2',
     'EXIT_SIGNAL:dispatch_graph_d1_s2',
     'INIT_SIGNAL:dispatch_graph_d1_s1']
  chart.start_at(dispatch_graph_d1_s2)
  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_d
def test_trans_topology_d1_2(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_d1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_d1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_d1_s1',
     'ENTRY_SIGNAL:dispatch_graph_d1_s1',
     'ENTRY_SIGNAL:dispatch_graph_d1_s2',
     'ENTRY_SIGNAL:dispatch_graph_d1_s3',
     'INIT_SIGNAL:dispatch_graph_d1_s3',
     'B:dispatch_graph_d1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_d1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_d1_s3',
     'EXIT_SIGNAL:dispatch_graph_d1_s3',
     'INIT_SIGNAL:dispatch_graph_d1_s2']
  chart.start_at(dispatch_graph_d1_s3)
  event = Event(signal=signals.B)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_e
def test_trans_topology_e1_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s1',
     'ENTRY_SIGNAL:dispatch_graph_e1_s1',
     'ENTRY_SIGNAL:dispatch_graph_e1_s2',
     'ENTRY_SIGNAL:dispatch_graph_e1_s3',
     'ENTRY_SIGNAL:dispatch_graph_e1_s4',
     'ENTRY_SIGNAL:dispatch_graph_e1_s5',
     'INIT_SIGNAL:dispatch_graph_e1_s5',
     'A:dispatch_graph_e1_s5',
     'A:dispatch_graph_e1_s4',
     'A:dispatch_graph_e1_s3',
     'A:dispatch_graph_e1_s2',
     'A:dispatch_graph_e1_s1',
     'EXIT_SIGNAL:dispatch_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s5',
     'EXIT_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'EXIT_SIGNAL:dispatch_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s3',
     'EXIT_SIGNAL:dispatch_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s2',
     'ENTRY_SIGNAL:dispatch_graph_e1_s2',
     'ENTRY_SIGNAL:dispatch_graph_e1_s3',
     'ENTRY_SIGNAL:dispatch_graph_e1_s4',
     'ENTRY_SIGNAL:dispatch_graph_e1_s5',
     'INIT_SIGNAL:dispatch_graph_e1_s5']
  chart.start_at(dispatch_graph_e1_s5)
  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_e
def test_trans_topology_e1_2(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s1',
     'ENTRY_SIGNAL:dispatch_graph_e1_s1',
     'ENTRY_SIGNAL:dispatch_graph_e1_s2',
     'ENTRY_SIGNAL:dispatch_graph_e1_s3',
     'ENTRY_SIGNAL:dispatch_graph_e1_s4',
     'ENTRY_SIGNAL:dispatch_graph_e1_s5',
     'INIT_SIGNAL:dispatch_graph_e1_s5',
     'B:dispatch_graph_e1_s5',
     'B:dispatch_graph_e1_s4',
     'B:dispatch_graph_e1_s3',
     'B:dispatch_graph_e1_s2',
     'EXIT_SIGNAL:dispatch_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s5',
     'EXIT_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'EXIT_SIGNAL:dispatch_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s3',
     'ENTRY_SIGNAL:dispatch_graph_e1_s3',
     'ENTRY_SIGNAL:dispatch_graph_e1_s4',
     'INIT_SIGNAL:dispatch_graph_e1_s4']
  chart.start_at(dispatch_graph_e1_s5)
  event  = Event(signal=signals.B)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_e
def test_trans_topology_e1_3(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s1',
     'ENTRY_SIGNAL:dispatch_graph_e1_s1',
     'ENTRY_SIGNAL:dispatch_graph_e1_s2',
     'ENTRY_SIGNAL:dispatch_graph_e1_s3',
     'ENTRY_SIGNAL:dispatch_graph_e1_s4',
     'ENTRY_SIGNAL:dispatch_graph_e1_s5',
     'INIT_SIGNAL:dispatch_graph_e1_s5',
     'C:dispatch_graph_e1_s5',
     'C:dispatch_graph_e1_s4',
     'C:dispatch_graph_e1_s3',
     'EXIT_SIGNAL:dispatch_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s5',
     'EXIT_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'ENTRY_SIGNAL:dispatch_graph_e1_s4',
     'INIT_SIGNAL:dispatch_graph_e1_s4']
  chart.start_at(dispatch_graph_e1_s5)
  event  = Event(signal=signals.C)
  chart.dispatch(e=event)
  assert(chart.spy_log == expected_behavior)


@pytest.mark.dispatch
@pytest.mark.topology_e
def test_trans_topology_e1_4(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s1',
     'ENTRY_SIGNAL:dispatch_graph_e1_s1',
     'ENTRY_SIGNAL:dispatch_graph_e1_s2',
     'ENTRY_SIGNAL:dispatch_graph_e1_s3',
     'ENTRY_SIGNAL:dispatch_graph_e1_s4',
     'ENTRY_SIGNAL:dispatch_graph_e1_s5',
     'INIT_SIGNAL:dispatch_graph_e1_s5',
     'D:dispatch_graph_e1_s5',
     'D:dispatch_graph_e1_s4',
     'D:dispatch_graph_e1_s3',
     'D:dispatch_graph_e1_s2',
     'D:dispatch_graph_e1_s1',
     'EXIT_SIGNAL:dispatch_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s5',
     'EXIT_SIGNAL:dispatch_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s4',
     'EXIT_SIGNAL:dispatch_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s3',
     'EXIT_SIGNAL:dispatch_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_e1_s2',
     'ENTRY_SIGNAL:dispatch_graph_e1_s2',
     'INIT_SIGNAL:dispatch_graph_e1_s2']
  chart.start_at(dispatch_graph_e1_s5)
  event  = Event(signal=signals.D)
  chart.dispatch(e=event)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_e
def test_trans_topology_e1_5(spy_chart):
  chart = spy_chart
  expected_behavior = \
    []
  chart.start_at(dispatch_graph_e1_s5)
  event  = Event(signal=signals.E)
  chart.dispatch(e=event)
  pp(chart.spy_log)

@pytest.mark.dispatch
@pytest.mark.topology_f
def test_trans_topology_f1_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s31',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s1',
     'ENTRY_SIGNAL:dispatch_graph_f1_s1',
     'ENTRY_SIGNAL:dispatch_graph_f1_s22',
     'ENTRY_SIGNAL:dispatch_graph_f1_s3',
     'ENTRY_SIGNAL:dispatch_graph_f1_s31',
     'INIT_SIGNAL:dispatch_graph_f1_s31',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s31',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s1',
     'EXIT_SIGNAL:dispatch_graph_f1_s31',
     'ENTRY_SIGNAL:dispatch_graph_f1_s32',
     'ENTRY_SIGNAL:dispatch_graph_f1_s321',
     'INIT_SIGNAL:dispatch_graph_f1_s321']
  chart.start_at(dispatch_graph_f1_s31)

  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_f
def test_trans_topology_f1_2(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s1',
     'ENTRY_SIGNAL:dispatch_graph_f1_s1',
     'ENTRY_SIGNAL:dispatch_graph_f1_s21',
     'INIT_SIGNAL:dispatch_graph_f1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s1',
     'EXIT_SIGNAL:dispatch_graph_f1_s21',
     'ENTRY_SIGNAL:dispatch_graph_f1_s22',
     'ENTRY_SIGNAL:dispatch_graph_f1_s3',
     'ENTRY_SIGNAL:dispatch_graph_f1_s32',
     'INIT_SIGNAL:dispatch_graph_f1_s32']
  chart.start_at(dispatch_graph_f1_s21)
  event  = Event(signal=signals.B)
  chart.dispatch(e=event)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_f
def test_trans_topology_f1_3(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s0',
     'ENTRY_SIGNAL:dispatch_graph_f1_s0',
     'INIT_SIGNAL:dispatch_graph_f1_s0',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s0',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_f1_s1',
     'EXIT_SIGNAL:dispatch_graph_f1_s0',
     'ENTRY_SIGNAL:dispatch_graph_f1_s1',
     'ENTRY_SIGNAL:dispatch_graph_f1_s22',
     'INIT_SIGNAL:dispatch_graph_f1_s22']
  chart.start_at(dispatch_graph_f1_s0)
  event = Event(signal=signals.C)
  chart.dispatch(e=event)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_g
def test_trans_topology_g1_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s1',
     'ENTRY_SIGNAL:dispatch_graph_g1_s1',
     'ENTRY_SIGNAL:dispatch_graph_g1_s21',
     'ENTRY_SIGNAL:dispatch_graph_g1_s211',
     'ENTRY_SIGNAL:dispatch_graph_g1_s2111',
     'INIT_SIGNAL:dispatch_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s1',
     'EXIT_SIGNAL:dispatch_graph_g1_s2111',
     'EXIT_SIGNAL:dispatch_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s211',
     'EXIT_SIGNAL:dispatch_graph_g1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s21',
     'ENTRY_SIGNAL:dispatch_graph_g1_s22',
     'ENTRY_SIGNAL:dispatch_graph_g1_s3',
     'ENTRY_SIGNAL:dispatch_graph_g1_s32',
     'ENTRY_SIGNAL:dispatch_graph_g1_s321',
     'INIT_SIGNAL:dispatch_graph_g1_s321']
  chart.start_at(dispatch_graph_g1_s2111)
  event = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_g
def test_trans_topology_g1_2(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s1',
     'ENTRY_SIGNAL:dispatch_graph_g1_s1',
     'ENTRY_SIGNAL:dispatch_graph_g1_s21',
     'ENTRY_SIGNAL:dispatch_graph_g1_s211',
     'ENTRY_SIGNAL:dispatch_graph_g1_s2111',
     'INIT_SIGNAL:dispatch_graph_g1_s2111',
     'B:dispatch_graph_g1_s2111',
     'B:dispatch_graph_g1_s211',
     'EXIT_SIGNAL:dispatch_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s2111',
     'EXIT_SIGNAL:dispatch_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s1',
     'EXIT_SIGNAL:dispatch_graph_g1_s21',
     'ENTRY_SIGNAL:dispatch_graph_g1_s22',
     'ENTRY_SIGNAL:dispatch_graph_g1_s3',
     'ENTRY_SIGNAL:dispatch_graph_g1_s32',
     'ENTRY_SIGNAL:dispatch_graph_g1_s321',
     'INIT_SIGNAL:dispatch_graph_g1_s321']
  chart.start_at(dispatch_graph_g1_s2111)
  event = Event(signal=signals.B)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_g
def test_trans_topology_g1_3(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s01',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s0',
     'ENTRY_SIGNAL:dispatch_graph_g1_s0',
     'ENTRY_SIGNAL:dispatch_graph_g1_s01',
     'INIT_SIGNAL:dispatch_graph_g1_s01',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s01',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s1',
     'EXIT_SIGNAL:dispatch_graph_g1_s01',
     'EXIT_SIGNAL:dispatch_graph_g1_s0',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s0',
     'ENTRY_SIGNAL:dispatch_graph_g1_s1',
     'ENTRY_SIGNAL:dispatch_graph_g1_s22',
     'INIT_SIGNAL:dispatch_graph_g1_s22']
  chart.start_at(dispatch_graph_g1_s01)
  event = Event(signal=signals.C)
  chart.dispatch(e=event)
  assert(chart.spy_log == expected_behavior)

@pytest.mark.dispatch
@pytest.mark.topology_h
def test_trans_topology_g1_4(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s1',
     'ENTRY_SIGNAL:dispatch_graph_g1_s1',
     'ENTRY_SIGNAL:dispatch_graph_g1_s22',
     'ENTRY_SIGNAL:dispatch_graph_g1_s3',
     'ENTRY_SIGNAL:dispatch_graph_g1_s32',
     'ENTRY_SIGNAL:dispatch_graph_g1_s321',
     'INIT_SIGNAL:dispatch_graph_g1_s321',
     'D:dispatch_graph_g1_s321',
     'D:dispatch_graph_g1_s32',
     'D:dispatch_graph_g1_s3',
     'EXIT_SIGNAL:dispatch_graph_g1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s321',
     'EXIT_SIGNAL:dispatch_graph_g1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s32',
     'EXIT_SIGNAL:dispatch_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:dispatch_graph_g1_s22',
     'EXIT_SIGNAL:dispatch_graph_g1_s22',
     'INIT_SIGNAL:dispatch_graph_g1_s1']
  chart.start_at(dispatch_graph_g1_s321)
  event = Event(signal=signals.D)
  chart.dispatch(e=event)
  #pp(chart.spy_log)
  assert(chart.spy_log == expected_behavior)
