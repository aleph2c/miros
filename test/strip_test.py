import pytest
from miros.hsm import stripped


@pytest.mark.tazor
@pytest.mark.strip
def test_trace_testing(fabric_fixture):

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
    print()
    for target_item, other_item in zip(twt, owt):
      print(target_item)
      assert(target_item == other_item)

  with stripped('[2017-11-05 15:17:39.424492] [75c8c] e->BATTERY_CHARGE() armed->armed') as swt:
    assert(swt == '[75c8c] e->BATTERY_CHARGE() armed->armed')
