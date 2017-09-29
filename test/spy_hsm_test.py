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
from collections import OrderedDict
@pytest.mark.spy
@pytest.mark.topology_a
def test_spy_topology_a_1():
  chart = Hsm()
  chart.full.spy = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_a1_s1',
     'ENTRY_SIGNAL:spy_graph_a1_s1',
     'INIT_SIGNAL:spy_graph_a1_s1',
     'A:spy_graph_a1_s1',
     'EXIT_SIGNAL:spy_graph_a1_s1',
     'ENTRY_SIGNAL:spy_graph_a1_s1',
     'INIT_SIGNAL:spy_graph_a1_s1']

  assert(
    chart.spy() == \
      ['ENTRY_SIGNAL:spy_graph_a1_s1',
       'INIT_SIGNAL:spy_graph_a1_s1',
       'A:spy_graph_a1_s1',
       'EXIT_SIGNAL:spy_graph_a1_s1',
       'ENTRY_SIGNAL:spy_graph_a1_s1',
       'INIT_SIGNAL:spy_graph_a1_s1']
  )

@pytest.mark.spy
@pytest.mark.topology_a
def test_spy_topology_a_2():
  chart = Hsm()
  chart.full.spy = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_a1_s1',
    'ENTRY_SIGNAL:spy_graph_a1_s1',
    'INIT_SIGNAL:spy_graph_a1_s1',
    'A:spy_graph_a1_s1',
    'EXIT_SIGNAL:spy_graph_a1_s1',
    'ENTRY_SIGNAL:spy_graph_a1_s1',
    'INIT_SIGNAL:spy_graph_a1_s1']
  assert(
    chart.spy() == \
      ['ENTRY_SIGNAL:spy_graph_a1_s1',
       'INIT_SIGNAL:spy_graph_a1_s1',
       'A:spy_graph_a1_s1',
       'EXIT_SIGNAL:spy_graph_a1_s1',
       'ENTRY_SIGNAL:spy_graph_a1_s1',
       'INIT_SIGNAL:spy_graph_a1_s1']
  )

@pytest.mark.spy
@pytest.mark.topology_b
def test_spy_topology_b1_1():
  chart = Hsm()
  chart.full.spy = \
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
  #pp(chart.spy())
  assert(
    chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_b1_s1',
     'ENTRY_SIGNAL:spy_graph_b1_s2',
     'INIT_SIGNAL:spy_graph_b1_s2',
     'A:spy_graph_b1_s1',
     'EXIT_SIGNAL:spy_graph_b1_s2',
     'ENTRY_SIGNAL:spy_graph_b1_s2',
     'INIT_SIGNAL:spy_graph_b1_s2']
  )

@pytest.mark.spy
@pytest.mark.topology_b
def test_spy_topology_b1_2():
  chart = Hsm()
  chart.full.spy = \
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
  #pp(chart.spy())
  assert(
   chart.spy() == \
     [
     'ENTRY_SIGNAL:spy_graph_b1_s1',
     'ENTRY_SIGNAL:spy_graph_b1_s2',
     'ENTRY_SIGNAL:spy_graph_b1_s3',
     'INIT_SIGNAL:spy_graph_b1_s3',
     'B:spy_graph_b1_s2',
     'EXIT_SIGNAL:spy_graph_b1_s3',
     'ENTRY_SIGNAL:spy_graph_b1_s3',
     'INIT_SIGNAL:spy_graph_b1_s3']
  )


@pytest.mark.spy
@pytest.mark.topology_c
def test_spy_topology_c1_1():
  chart = Hsm()
  chart.full.spy = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s1',
     'ENTRY_SIGNAL:spy_graph_c1_s1',
     'INIT_SIGNAL:spy_graph_c1_s1',
     'A:spy_graph_c1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s1',
     'EXIT_SIGNAL:spy_graph_c1_s1',
     'ENTRY_SIGNAL:spy_graph_c1_s2',
     'INIT_SIGNAL:spy_graph_c1_s2']
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_c1_s1',
     'INIT_SIGNAL:spy_graph_c1_s1',
     'A:spy_graph_c1_s1',
     'EXIT_SIGNAL:spy_graph_c1_s1',
     'ENTRY_SIGNAL:spy_graph_c1_s2',
     'INIT_SIGNAL:spy_graph_c1_s2']
  )

@pytest.mark.spy
@pytest.mark.topology_c
def test_spy_topology_c1_3():
  chart = Hsm()
  chart.full.spy = \
    ['SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s2',
     'ENTRY_SIGNAL:spy_graph_c1_s2',
     'INIT_SIGNAL:spy_graph_c1_s2',
     'A:spy_graph_c1_s2',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s1',
     'SEARCH_FOR_SUPER_SIGNAL:spy_graph_c1_s2',
     'EXIT_SIGNAL:spy_graph_c1_s2',
     'ENTRY_SIGNAL:spy_graph_c1_s1',
     'INIT_SIGNAL:spy_graph_c1_s1']
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_c1_s2',
     'INIT_SIGNAL:spy_graph_c1_s2',
     'A:spy_graph_c1_s2',
     'EXIT_SIGNAL:spy_graph_c1_s2',
     'ENTRY_SIGNAL:spy_graph_c1_s1',
     'INIT_SIGNAL:spy_graph_c1_s1']
  )

@pytest.mark.spy
@pytest.mark.topology_c
def test_spy_topology_c2_1():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_c2_s1',
     'ENTRY_SIGNAL:spy_graph_c2_s2',
     'INIT_SIGNAL:spy_graph_c2_s2',
     'A:spy_graph_c2_s2',
     'EXIT_SIGNAL:spy_graph_c2_s2',
     'ENTRY_SIGNAL:spy_graph_c2_s3',
     'INIT_SIGNAL:spy_graph_c2_s3']
  )

@pytest.mark.spy
@pytest.mark.topology_c
def test_spy_topology_c2_2():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_c2_s1',
     'ENTRY_SIGNAL:spy_graph_c2_s3',
     'INIT_SIGNAL:spy_graph_c2_s3',
     'A:spy_graph_c2_s3',
     'EXIT_SIGNAL:spy_graph_c2_s3',
     'ENTRY_SIGNAL:spy_graph_c2_s2',
     'INIT_SIGNAL:spy_graph_c2_s2']
  )

@pytest.mark.spy
@pytest.mark.topology_d
def test_spy_topology_d1_1():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    ['ENTRY_SIGNAL:spy_graph_d1_s1',
     'ENTRY_SIGNAL:spy_graph_d1_s2',
     'INIT_SIGNAL:spy_graph_d1_s2',
     'A:spy_graph_d1_s2',
     'EXIT_SIGNAL:spy_graph_d1_s2',
     'INIT_SIGNAL:spy_graph_d1_s1']
  )

@pytest.mark.spy
@pytest.mark.topology_d
def test_spy_topology_d1_2():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_d1_s1',
     'ENTRY_SIGNAL:spy_graph_d1_s2',
     'ENTRY_SIGNAL:spy_graph_d1_s3',
     'INIT_SIGNAL:spy_graph_d1_s3',
     'B:spy_graph_d1_s3',
     'EXIT_SIGNAL:spy_graph_d1_s3',
     'INIT_SIGNAL:spy_graph_d1_s2']
  )

@pytest.mark.spy
@pytest.mark.topology_e
def test_spy_topology_e1_1():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5',
     'A:spy_graph_e1_s1',
     'EXIT_SIGNAL:spy_graph_e1_s5',
     'EXIT_SIGNAL:spy_graph_e1_s4',
     'EXIT_SIGNAL:spy_graph_e1_s3',
     'EXIT_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5']
  )

@pytest.mark.spy
@pytest.mark.topology_e
def test_spy_topology_e1_2():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5',
     'B:spy_graph_e1_s2',
     'EXIT_SIGNAL:spy_graph_e1_s5',
     'EXIT_SIGNAL:spy_graph_e1_s4',
     'EXIT_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'INIT_SIGNAL:spy_graph_e1_s4']
  )

@pytest.mark.spy
@pytest.mark.topology_e
def test_spy_topology_e1_3():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5',
     'C:spy_graph_e1_s3',
     'EXIT_SIGNAL:spy_graph_e1_s5',
     'EXIT_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'INIT_SIGNAL:spy_graph_e1_s4']
  )

@pytest.mark.spy
@pytest.mark.topology_e
def test_spy_topology_e1_4():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5',
     'C:spy_graph_e1_s3',
     'EXIT_SIGNAL:spy_graph_e1_s5',
     'EXIT_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'INIT_SIGNAL:spy_graph_e1_s4']
  )

@pytest.mark.spy
@pytest.mark.topology_e
def test_spy_topology_e1_5():
  chart = Hsm()
  chart.full.spy = \
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
     'E:spy_graph_e1_s5',
     'E:spy_graph_e1_s4',
     'E:spy_graph_e1_s3',
     'E:spy_graph_e1_s2',
     'E:spy_graph_e1_s1:HANDLED']
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_e1_s1',
     'ENTRY_SIGNAL:spy_graph_e1_s2',
     'ENTRY_SIGNAL:spy_graph_e1_s3',
     'ENTRY_SIGNAL:spy_graph_e1_s4',
     'ENTRY_SIGNAL:spy_graph_e1_s5',
     'INIT_SIGNAL:spy_graph_e1_s5',
     'E:spy_graph_e1_s1:HANDLED']
  )

@pytest.mark.spy
@pytest.mark.topology_f
def test_spy_topology_1_1():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_f1_s1',
     'ENTRY_SIGNAL:spy_graph_f1_s22',
     'ENTRY_SIGNAL:spy_graph_f1_s3',
     'ENTRY_SIGNAL:spy_graph_f1_s31',
     'INIT_SIGNAL:spy_graph_f1_s31',
     'A:spy_graph_f1_s31',
     'EXIT_SIGNAL:spy_graph_f1_s31',
     'ENTRY_SIGNAL:spy_graph_f1_s32',
     'ENTRY_SIGNAL:spy_graph_f1_s321',
     'INIT_SIGNAL:spy_graph_f1_s321']
  )

@pytest.mark.spy
@pytest.mark.topology_f
def test_spy_topology_1_2():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
   [
   'ENTRY_SIGNAL:spy_graph_f1_s1',
   'ENTRY_SIGNAL:spy_graph_f1_s21',
   'INIT_SIGNAL:spy_graph_f1_s21',
   'B:spy_graph_f1_s21',
   'EXIT_SIGNAL:spy_graph_f1_s21',
   'ENTRY_SIGNAL:spy_graph_f1_s22',
   'ENTRY_SIGNAL:spy_graph_f1_s3',
   'ENTRY_SIGNAL:spy_graph_f1_s32',
   'INIT_SIGNAL:spy_graph_f1_s32']
  )

@pytest.mark.spy
@pytest.mark.topology_f
def test_spy_topology_1_3():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_f1_s0',
     'INIT_SIGNAL:spy_graph_f1_s0',
     'C:spy_graph_f1_s0',
     'EXIT_SIGNAL:spy_graph_f1_s0',
     'ENTRY_SIGNAL:spy_graph_f1_s1',
     'ENTRY_SIGNAL:spy_graph_f1_s22',
     'INIT_SIGNAL:spy_graph_f1_s22']
  )
@pytest.mark.spy
@pytest.mark.topology_f
def test_spy_topology_1_2():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
   [
   'ENTRY_SIGNAL:spy_graph_f1_s1',
   'ENTRY_SIGNAL:spy_graph_f1_s21',
   'INIT_SIGNAL:spy_graph_f1_s21',
   'B:spy_graph_f1_s21',
   'EXIT_SIGNAL:spy_graph_f1_s21',
   'ENTRY_SIGNAL:spy_graph_f1_s22',
   'ENTRY_SIGNAL:spy_graph_f1_s3',
   'ENTRY_SIGNAL:spy_graph_f1_s32',
   'INIT_SIGNAL:spy_graph_f1_s32']
  )

@pytest.mark.spy
@pytest.mark.topology_g
def test_spy_topology_1_1():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s211',
     'ENTRY_SIGNAL:spy_graph_g1_s2111',
     'INIT_SIGNAL:spy_graph_g1_s2111',
     'A:spy_graph_g1_s2111',
     'EXIT_SIGNAL:spy_graph_g1_s2111',
     'EXIT_SIGNAL:spy_graph_g1_s211',
     'EXIT_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s22',
     'ENTRY_SIGNAL:spy_graph_g1_s3',
     'ENTRY_SIGNAL:spy_graph_g1_s32',
     'ENTRY_SIGNAL:spy_graph_g1_s321',
     'INIT_SIGNAL:spy_graph_g1_s321']
  )

@pytest.mark.spy
@pytest.mark.topology_g
def test_spy_topology_1_2():
  chart = Hsm()
  chart.full.spy = \
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
  assert(
   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s211',
     'ENTRY_SIGNAL:spy_graph_g1_s2111',
     'INIT_SIGNAL:spy_graph_g1_s2111',
     'B:spy_graph_g1_s21',
     'EXIT_SIGNAL:spy_graph_g1_s2111',
     'EXIT_SIGNAL:spy_graph_g1_s211',
     'EXIT_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s22',
     'ENTRY_SIGNAL:spy_graph_g1_s3',
     'ENTRY_SIGNAL:spy_graph_g1_s32',
     'ENTRY_SIGNAL:spy_graph_g1_s321',
     'INIT_SIGNAL:spy_graph_g1_s321']
  )

@pytest.mark.spy
@pytest.mark.topology_g
def test_spy_topology_1_3():
  chart = Hsm()
  chart.full.spy = \
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
  assert(

   chart.spy() == \
    ['ENTRY_SIGNAL:spy_graph_g1_s0',
     'ENTRY_SIGNAL:spy_graph_g1_s01',
     'INIT_SIGNAL:spy_graph_g1_s01',
     'C:spy_graph_g1_s01',
     'EXIT_SIGNAL:spy_graph_g1_s01',
     'EXIT_SIGNAL:spy_graph_g1_s0',
     'ENTRY_SIGNAL:spy_graph_g1_s22',
     'INIT_SIGNAL:spy_graph_g1_s22']
  )

@pytest.mark.spy
@pytest.mark.topology_g
def test_spy_topology_1_3():
  chart = Hsm()
  chart.full.spy = \
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
  assert(

   chart.spy() == \
    ['ENTRY_SIGNAL:spy_graph_g1_s0',
     'ENTRY_SIGNAL:spy_graph_g1_s01',
     'INIT_SIGNAL:spy_graph_g1_s01',
     'C:spy_graph_g1_s01',
     'EXIT_SIGNAL:spy_graph_g1_s01',
     'EXIT_SIGNAL:spy_graph_g1_s0',
     'ENTRY_SIGNAL:spy_graph_g1_s22',
     'INIT_SIGNAL:spy_graph_g1_s22']
  )

@pytest.mark.spy
@pytest.mark.topology_h
def test_spy_topology_g1_4():
  chart = Hsm()
  chart.full.spy = \
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
  assert(

   chart.spy() == \
    [
     'ENTRY_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s211',
     'ENTRY_SIGNAL:spy_graph_g1_s2111',
     'INIT_SIGNAL:spy_graph_g1_s2111',
     'B:spy_graph_g1_s21',
     'EXIT_SIGNAL:spy_graph_g1_s2111',
     'EXIT_SIGNAL:spy_graph_g1_s211',
     'EXIT_SIGNAL:spy_graph_g1_s21',
     'ENTRY_SIGNAL:spy_graph_g1_s22',
     'ENTRY_SIGNAL:spy_graph_g1_s3',
     'ENTRY_SIGNAL:spy_graph_g1_s32',
     'ENTRY_SIGNAL:spy_graph_g1_s321',
     'INIT_SIGNAL:spy_graph_g1_s321']
  )

