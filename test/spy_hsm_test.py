import pytest
from miros.event import ReturnStatus, signals, Event, return_status
from miros.hsm   import reflect, Hsm, HsmTopologyException, spy_on
import pprint
def pp(item):
  print("")
  pprint.pprint(item)

signals.append("A")
signals.append("B")
signals.append("C")
signals.append("D")
signals.append("E")
signals.append("F")
signals.append("G")
################################################################################
#                                 Spy Graph A1                                 #
################################################################################
'''    The following state chart is used to test the spy on topology A

                            +- graph_a1_s1 -+
                            |               +-----+
                            |               |     a
                            |               <-----+
                            +---------------+

This is used for testing the type A topology in the trans_ method of the Hsm
class.
  * test_spy_topology_a_1 (diagram)
  * test_spy_topology_a_2 (diagram)
'''
@spy_on
def spy_graph_a1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_a1_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

################################################################################
#                             Spy Graph B1                                #
################################################################################
'''      The following state chart is used to test spy_on with topology B

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
  * test_spy_topology_b1_1 - start in graph_b1_s2 (diagram)
  * test_spy_topology_b1_2 - start in graph_b1_s3 (diagram)
'''
@spy_on
def spy_graph_b1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_b1_s2)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def spy_graph_b1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(spy_graph_b1_s3)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_b1_s1
  return status

@spy_on
def spy_graph_b1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_b1_s2
  return status
################################################################################
#                             Spy Graph C1                                #
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
  * test_spy_topology_c1_1 (diagram - start in graph_c1_s1 )
  * test_spy_topology_c1_2 (diagram - start in graph_c1_s1 )
'''
@spy_on
def spy_graph_c1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_c1_s2)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def spy_graph_c1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_c1_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status
################################################################################
#                             Spy Graph C2                                #
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
  * test_spy_topology_c2_1 (diagram - start in graph_c2_s2)
  * test_spy_topology_c2_2 (diagram - start in graph_c2_s3)
'''
@spy_on
def spy_graph_c2_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    chart.trans(spy_graph_c2_s2)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def spy_graph_c2_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_c2_s3)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_c2_s1
  return status

@spy_on
def spy_graph_c2_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_c2_s2)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_c2_s1
  return status
################################################################################
#                             Spy Graph D1                                #
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
  * test_spy_topology_d1_1 - start in graph_d1_s2 (diagram)
  * test_spy_topology_d1_2 - start in graph_d1_s3 (diagram)
'''
@spy_on
def spy_graph_d1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def spy_graph_d1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_d1_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_d1_s1
  return status

@spy_on
def spy_graph_d1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(spy_graph_d1_s2)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_d1_s2
  return status
################################################################################
#                             Spy Graph E1                                #
################################################################################
'''           The following state chart is used to test topology E

                     +---------- graph_e1_s1 -----------+
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
  * test_spy_topology_e1_1 - start in graph_e1_s5 (diagram - a)
  * test_spy_topology_e1_2 - start in graph_e1_s5 (diagram - b)
  * test_spy_topology_e1_3 - start in graph_e1_s5 (diagram - c)
  * test_spy_topology_e1_3 - start in graph_e1_s5 (diagram - d)
  * test_spy_topology_e1_4 - start in graph_e1_s5 (diagram - d)
'''
@spy_on
def spy_graph_e1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_e1_s5)
  elif(e.signal == signals.D):
    status = chart.trans(spy_graph_e1_s2)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def spy_graph_e1_s2(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(spy_graph_e1_s4)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_e1_s1
  return status

@spy_on
def spy_graph_e1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    status = chart.trans(spy_graph_e1_s4)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_e1_s2
  return status

@spy_on
def spy_graph_e1_s4(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_e1_s3
  return status

@spy_on
def spy_graph_e1_s5(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_e1_s4
  return status

################################################################################
#                             Spy Graph F1                                #
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
  * test_spy_topology_f1_1 - start in graph_f1_s31 (diagram -> a)
  * test_spy_topology_f1_2 - start in graph_f1_s21 (diagram -> b)
  * test_spy_topology_f1_3 - start in graph_f1_s0  (diagram -> c)
'''
@spy_on
def spy_graph_f1_s0(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    status = chart.trans(spy_graph_f1_s22)
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def spy_graph_f1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def spy_graph_f1_s21(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(spy_graph_f1_s32)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_f1_s1
  return status

@spy_on
def spy_graph_f1_s22(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_f1_s1
  return status

@spy_on
def spy_graph_f1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_f1_s22
  return status

@spy_on
def spy_graph_f1_s31(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_f1_s321)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_f1_s3
  return status

@spy_on
def spy_graph_f1_s32(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_f1_s3
  return status

@spy_on
def spy_graph_f1_s321(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_f1_s32
  return status

################################################################################
#                             Spy Graph G1                                #
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
  * test_spy_topology_g1_1 - start in graph_g1_s211 (diagram -> a)
  * test_spy_topology_g1_2 - start in graph_g1_s211 (diagram -> b)
  * test_spy_topology_g1_3 - start in graph_g1_s01  (diagram -> a)
  * test_spy_topology_g1_4 - start in graph_g1_s321 (diagram -> d)
'''
@spy_on
def spy_graph_g1_s0(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def spy_graph_g1_s01(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.C):
    status = chart.trans(spy_graph_g1_s22)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_g1_s0
  return status

def spy_graph_g1_s1(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, chart.top
  return status

@spy_on
def spy_graph_g1_s21(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.B):
    status = chart.trans(spy_graph_g1_s321)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_g1_s1
  return status

@spy_on
def spy_graph_g1_s211(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_g1_s21
  return status

@spy_on
def spy_graph_g1_s2111(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.A):
    status = chart.trans(spy_graph_g1_s321)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_g1_s211
  return status

@spy_on
def spy_graph_g1_s22(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.D):
    status = chart.trans(spy_graph_g1_s1)
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_g1_s1
  return status

@spy_on
def spy_graph_g1_s3(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_g1_s22
  return status

@spy_on
def spy_graph_g1_s32(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_g1_s3
  return status

@spy_on
def spy_graph_g1_s321(chart, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    status, chart.temp.fun = return_status.SUPER, spy_graph_g1_s32
  return status

@pytest.fixture
def spy_chart(request):
  chart = Hsm()
  spy   = []
  chart.augment(other=spy, name="spy")
  signals.append("A")
  signals.append("B")
  signals.append("C")
  signals.append("D")
  signals.append("E")
  signals.append("F")
  yield chart
  del spy
  del chart

# grep test name to view diagram
@pytest.mark.spy
@pytest.mark.topology_a
def test_spy_topology_a_1():
  chart = Hsm()
  expected_behavior = \
  ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_a1_s1',
   'ENTRY_SIGNAL:spy_graph_a1_s1',
   'INIT_SIGNAL:spy_graph_a1_s1',
   'A:spy_graph_a1_s1',
   'EXIT_SIGNAL:spy_graph_a1_s1',
   'ENTRY_SIGNAL:spy_graph_a1_s1',
   'INIT_SIGNAL:spy_graph_a1_s1']

  chart.start_at(spy_graph_a1_s1)
  event = Event(signal=signals.A)
  chart.dispatch(e=event)
  assert(chart.spy == expected_behavior)

# grep test name to view diagram
@pytest.mark.spy
@pytest.mark.topology_a
def test_spy_topology_a_2():
  chart = Hsm()
  chart.spy = []
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_a1_s1',
    'ENTRY_SIGNAL:spy_graph_a1_s1',
    'INIT_SIGNAL:spy_graph_a1_s1',
    'A:spy_graph_a1_s1',
    'EXIT_SIGNAL:spy_graph_a1_s1',
    'ENTRY_SIGNAL:spy_graph_a1_s1',
    'INIT_SIGNAL:spy_graph_a1_s1']

  chart.start_at(spy_graph_a1_s1)
  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_b
def test_spy_topology_b1_1(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_b1_s1',
     'ENTRY_SIGNAL:spy_graph_b1_s1',
     'ENTRY_SIGNAL:spy_graph_b1_s2',
     'INIT_SIGNAL:spy_graph_b1_s2',
     'A:spy_graph_b1_s2',
     'A:spy_graph_b1_s1',
     'EXIT_SIGNAL:spy_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_b1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_b1_s2',
     'ENTRY_SIGNAL:spy_graph_b1_s2',
     'INIT_SIGNAL:spy_graph_b1_s2']
  chart.start_at(spy_graph_b1_s2)
  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.dispatch
def test_spy_topology_b1_2(spy_chart):
  chart = Hsm()
  expected_behavior = \
   ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_b1_s3',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_b1_s2',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_b1_s1',
   'ENTRY_SIGNAL:spy_graph_b1_s1',
   'ENTRY_SIGNAL:spy_graph_b1_s2',
   'ENTRY_SIGNAL:spy_graph_b1_s3',
   'INIT_SIGNAL:spy_graph_b1_s3',
   'B:spy_graph_b1_s3',
   'B:spy_graph_b1_s2',
   'EXIT_SIGNAL:spy_graph_b1_s3',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_b1_s3',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_b1_s3',
   'ENTRY_SIGNAL:spy_graph_b1_s3',
   'INIT_SIGNAL:spy_graph_b1_s3']
  chart.start_at(spy_graph_b1_s3)
  event  = Event(signal=signals.B)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_c
def test_spy_topology_c1_1(spy_chart):
  chart   = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s1',
     'ENTRY_SIGNAL:spy_graph_c1_s1',
     'INIT_SIGNAL:spy_graph_c1_s1',
     'A:spy_graph_c1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s1',
     'EXIT_SIGNAL:spy_graph_c1_s1',
     'ENTRY_SIGNAL:spy_graph_c1_s2',
     'INIT_SIGNAL:spy_graph_c1_s2']
  event = Event(signal = signals.A)
  chart.start_at(spy_graph_c1_s1)
  chart.dispatch(e=event)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_c
def test_spy_topology_c1_3(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s2',
     'ENTRY_SIGNAL:spy_graph_c1_s2',
     'INIT_SIGNAL:spy_graph_c1_s2',
     'A:spy_graph_c1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s2',
     'EXIT_SIGNAL:spy_graph_c1_s2',
     'ENTRY_SIGNAL:spy_graph_c1_s1',
     'INIT_SIGNAL:spy_graph_c1_s1']
  chart.start_at(spy_graph_c1_s2)
  event = Event(signal = signals.A)
  chart.dispatch(e = event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_c
def test_spy_topology_c2_1():
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_c2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c2_s1',
     'ENTRY_SIGNAL:spy_graph_c2_s1',
     'ENTRY_SIGNAL:spy_graph_c2_s2',
     'INIT_SIGNAL:spy_graph_c2_s2',
     'A:spy_graph_c2_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c2_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c2_s2',
     'EXIT_SIGNAL:spy_graph_c2_s2',
     'ENTRY_SIGNAL:spy_graph_c2_s3',
     'INIT_SIGNAL:spy_graph_c2_s3']

  event = Event(signal = signals.A)
  chart.start_at(spy_graph_c2_s2)
  chart.dispatch(e = event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_c
def test_spy_topology_c2_2(spy_chart):
  chart   = Hsm()
  expected_behavior = \
  ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_c2_s3',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c2_s1',
   'ENTRY_SIGNAL:spy_graph_c2_s1',
   'ENTRY_SIGNAL:spy_graph_c2_s3',
   'INIT_SIGNAL:spy_graph_c2_s3',
   'A:spy_graph_c2_s3',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c2_s2',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c2_s3',
   'EXIT_SIGNAL:spy_graph_c2_s3',
   'ENTRY_SIGNAL:spy_graph_c2_s2',
   'INIT_SIGNAL:spy_graph_c2_s2']
  chart.start_at(spy_graph_c2_s3)
  event = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_d
def test_spy_topology_d1_1(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_d1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_d1_s1',
     'ENTRY_SIGNAL:spy_graph_d1_s1',
     'ENTRY_SIGNAL:spy_graph_d1_s2',
     'INIT_SIGNAL:spy_graph_d1_s2',
     'A:spy_graph_d1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_d1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_d1_s2',
     'EXIT_SIGNAL:spy_graph_d1_s2',
     'INIT_SIGNAL:spy_graph_d1_s1']
  chart.start_at(spy_graph_d1_s2)
  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_d
def test_spy_topology_d1_2(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_d1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_d1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_d1_s1',
     'ENTRY_SIGNAL:spy_graph_d1_s1',
     'ENTRY_SIGNAL:spy_graph_d1_s2',
     'ENTRY_SIGNAL:spy_graph_d1_s3',
     'INIT_SIGNAL:spy_graph_d1_s3',
     'B:spy_graph_d1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_d1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_d1_s3',
     'EXIT_SIGNAL:spy_graph_d1_s3',
     'INIT_SIGNAL:spy_graph_d1_s2']
  chart.start_at(spy_graph_d1_s3)
  event = Event(signal=signals.B)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_e
def test_spy_topology_e1_1(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5',
     'A:spy_graph_e1_s5',
     'A:spy_graph_e1_s4',
     'A:spy_graph_e1_s3',
     'A:spy_graph_e1_s2',
     'A:spy_graph_e1_s1',
     'EXIT_SIGNAL:spy_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s5',
     'EXIT_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'EXIT_SIGNAL:spy_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s3',
     'EXIT_SIGNAL:spy_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5']
  chart.start_at(spy_graph_e1_s5)
  event = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_e
def test_spy_topology_e1_2(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5',
     'B:spy_graph_e1_s5',
     'B:spy_graph_e1_s4',
     'B:spy_graph_e1_s3',
     'B:spy_graph_e1_s2',
     'EXIT_SIGNAL:spy_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s5',
     'EXIT_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'EXIT_SIGNAL:spy_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'INIT_SIGNAL:spy_graph_e1_s4']
  chart.start_at(spy_graph_e1_s5)
  event = Event(signal=signals.B)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_e
def test_spy_topology_e1_3(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5',
     'C:spy_graph_e1_s5',
     'C:spy_graph_e1_s4',
     'C:spy_graph_e1_s3',
     'EXIT_SIGNAL:spy_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s5',
     'EXIT_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'INIT_SIGNAL:spy_graph_e1_s4']
  chart.start_at(spy_graph_e1_s5)
  event  = Event(signal=signals.C)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_e
def test_spy_topology_e1_4(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5',
     'D:spy_graph_e1_s5',
     'D:spy_graph_e1_s4',
     'D:spy_graph_e1_s3',
     'D:spy_graph_e1_s2',
     'D:spy_graph_e1_s1',
     'EXIT_SIGNAL:spy_graph_e1_s5',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s5',
     'EXIT_SIGNAL:spy_graph_e1_s4',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s4',
     'EXIT_SIGNAL:spy_graph_e1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s3',
     'EXIT_SIGNAL:spy_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'INIT_SIGNAL:spy_graph_e1_s2']
  chart.start_at(spy_graph_e1_s5)
  event  = Event(signal=signals.D)
  chart.dispatch(e=event)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_f
def test_spy_topology_f1_1(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s31',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s1',
     'ENTRY_SIGNAL:spy_graph_f1_s1',
     'ENTRY_SIGNAL:spy_graph_f1_s22',
     'ENTRY_SIGNAL:spy_graph_f1_s3',
     'ENTRY_SIGNAL:spy_graph_f1_s31',
     'INIT_SIGNAL:spy_graph_f1_s31',
     'A:spy_graph_f1_s31',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s31',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s1',
     'EXIT_SIGNAL:spy_graph_f1_s31',
     'ENTRY_SIGNAL:spy_graph_f1_s32',
     'ENTRY_SIGNAL:spy_graph_f1_s321',
     'INIT_SIGNAL:spy_graph_f1_s321']
  chart.start_at(spy_graph_f1_s31)
  event  = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_f
def test_spy_topology_f1_2(spy_chart):
  chart = Hsm()
  expected_behavior = \
   ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s21',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s1',
   'ENTRY_SIGNAL:spy_graph_f1_s1',
   'ENTRY_SIGNAL:spy_graph_f1_s21',
   'INIT_SIGNAL:spy_graph_f1_s21',
   'B:spy_graph_f1_s21',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s32',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s21',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s3',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s22',
   'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s1',
   'EXIT_SIGNAL:spy_graph_f1_s21',
   'ENTRY_SIGNAL:spy_graph_f1_s22',
   'ENTRY_SIGNAL:spy_graph_f1_s3',
   'ENTRY_SIGNAL:spy_graph_f1_s32',
   'INIT_SIGNAL:spy_graph_f1_s32']
  chart.start_at(spy_graph_f1_s21)
  event  = Event(signal=signals.B)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_f
def test_spy_topology_f1_3(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s0',
     'ENTRY_SIGNAL:spy_graph_f1_s0',
     'INIT_SIGNAL:spy_graph_f1_s0',
     'C:spy_graph_f1_s0',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s0',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_f1_s1',
     'EXIT_SIGNAL:spy_graph_f1_s0',
     'ENTRY_SIGNAL:spy_graph_f1_s1',
     'ENTRY_SIGNAL:spy_graph_f1_s22',
     'INIT_SIGNAL:spy_graph_f1_s22']
  chart.start_at(spy_graph_f1_s0)
  event = Event(signal=signals.C)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_g
def test_spy_topology_g1_1(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s211',
     'ENTRY_SIGNAL:spy_graph_g1_s2111',
     'INIT_SIGNAL:spy_graph_g1_s2111',
     'A:spy_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s22',
     'EXIT_SIGNAL:spy_graph_g1_s2111',
     'EXIT_SIGNAL:spy_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s211',
     'EXIT_SIGNAL:spy_graph_g1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s22',
     'ENTRY_SIGNAL:spy_graph_g1_s3',
     'ENTRY_SIGNAL:spy_graph_g1_s32',
     'ENTRY_SIGNAL:spy_graph_g1_s321',
     'INIT_SIGNAL:spy_graph_g1_s321']
  chart.start_at(spy_graph_g1_s2111)
  event = Event(signal=signals.A)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_g
def test_spy_topology_g1_2():
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s211',
     'ENTRY_SIGNAL:spy_graph_g1_s2111',
     'INIT_SIGNAL:spy_graph_g1_s2111',
     'B:spy_graph_g1_s2111',
     'B:spy_graph_g1_s211',
     'B:spy_graph_g1_s21',
     'EXIT_SIGNAL:spy_graph_g1_s2111',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s2111',
     'EXIT_SIGNAL:spy_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s211',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s21',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s22',
     'EXIT_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s22',
     'ENTRY_SIGNAL:spy_graph_g1_s3',
     'ENTRY_SIGNAL:spy_graph_g1_s32',
     'ENTRY_SIGNAL:spy_graph_g1_s321',
     'INIT_SIGNAL:spy_graph_g1_s321']
  chart.start_at(spy_graph_g1_s2111)
  event = Event(signal=signals.B)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_g
def test_spy_topology_g1_3(spy_chart):
  chart = Hsm()
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s01',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s0',
     'ENTRY_SIGNAL:spy_graph_g1_s0',
     'ENTRY_SIGNAL:spy_graph_g1_s01',
     'INIT_SIGNAL:spy_graph_g1_s01',
     'C:spy_graph_g1_s01',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s22',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s01',
     'EXIT_SIGNAL:spy_graph_g1_s01',
     'EXIT_SIGNAL:spy_graph_g1_s0',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s0',
     'ENTRY_SIGNAL:spy_graph_g1_s22',
     'INIT_SIGNAL:spy_graph_g1_s22']
  chart.start_at(spy_graph_g1_s01)
  event = Event(signal=signals.C)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)

@pytest.mark.spy
@pytest.mark.topology_h
def test_spy_topology_g1_4(spy_chart):
  chart = spy_chart
  expected_behavior = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s22',
     'ENTRY_SIGNAL:spy_graph_g1_s22',
     'ENTRY_SIGNAL:spy_graph_g1_s3',
     'ENTRY_SIGNAL:spy_graph_g1_s32',
     'ENTRY_SIGNAL:spy_graph_g1_s321',
     'INIT_SIGNAL:spy_graph_g1_s321',
     'D:spy_graph_g1_s321',
     'D:spy_graph_g1_s32',
     'D:spy_graph_g1_s3',
     'D:spy_graph_g1_s22',
     'EXIT_SIGNAL:spy_graph_g1_s321',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s321',
     'EXIT_SIGNAL:spy_graph_g1_s32',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s32',
     'EXIT_SIGNAL:spy_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s3',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_g1_s22',
     'EXIT_SIGNAL:spy_graph_g1_s22']
  chart.start_at(spy_graph_g1_s321)
  event = Event(signal=signals.D)
  chart.dispatch(e=event)
  #pp(chart.spy)
  assert(chart.spy == expected_behavior)
