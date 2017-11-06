import pytest
from miros.hsm import stripped


@pytest.mark.strip
def test_trace_testing_single_line():
  '''Remove the timestamp off of a signal line'''

  with stripped('[2017-11-05 15:17:39.424492] [75c8c] e->BATTERY_CHARGE() armed->armed') as swt:
    assert(swt == '[75c8c] e->BATTERY_CHARGE() armed->armed')


@pytest.mark.strip
def test_trace_testing_single_block():
  '''Remove the timestamp off of a group of lines'''

  target = \
    '''[2017-11-05 21:31:56.098526] [75c8c] e->start_at() top->arming
       [2017-11-05 21:31:56.200047] [75c8c] e->BATTERY_CHARGE() arming->armed
       [2017-11-05 21:31:56.300974] [75c8c] e->BATTERY_CHARGE() armed->armed
       [2017-11-05 21:31:56.401682] [75c8c] e->BATTERY_CHARGE() armed->armed
    '''

  result = \
    '''[2018-11-05 01:31:56.098526] [75c8c] e->start_at() top->arming
       [2018-11-05 01:31:56.200047] [75c8c] e->BATTERY_CHARGE() arming->armed
       [2018-11-05 01:31:56.300974] [75c8c] e->BATTERY_CHARGE() armed->armed
       [2018-11-05 01:31:56.401682] [75c8c] e->BATTERY_CHARGE() armed->armed
     '''

  with stripped(target) as twt, \
       stripped(result) as owt:
    for target_item, other_item in zip(twt, owt):
      assert(target_item == other_item)


@pytest.mark.strip
def test_strip_with_nothing_to_do():
  '''Ignore blocks that don't have a timestamp'''

  target = \
    '''[75c8c] e->start_at() top->arming
       [75c8c] e->BATTERY_CHARGE() arming->armed
       [75c8c] e->BATTERY_CHARGE() armed->armed
       [75c8c] e->BATTERY_CHARGE() armed->armed
    '''

  result = \
    '''[75c8c] e->start_at() top->arming
       [75c8c] e->BATTERY_CHARGE() arming->armed
       [75c8c] e->BATTERY_CHARGE() armed->armed
       [75c8c] e->BATTERY_CHARGE() armed->armed
     '''
  with stripped(target) as twt, \
       stripped(result) as owt:
    for target_item, other_item in zip(twt, owt):
      assert(target_item == other_item)
