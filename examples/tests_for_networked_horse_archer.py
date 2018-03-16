
if __name__ == '__main__':
  pp('')
  archer.cancel_events(Event(signal=signals.Second))
  time.sleep(0.2)

  # build the horse archer's empathy chart, send it all the events required to
  # test it
  oha = OtherHorseArcher()
  oha.start_at(empathy)
  oha.post_fifo(Event(signal=signals.Other_Retreat_Ready_War_Cry))
  oha.post_fifo(Event(signal=signals.Retreat_War_Cry))
  oha.post_fifo(Event(signal=signals.Advance_War_Cry))
  oha.post_fifo(Event(signal=signals.Advance_War_Cry))
  oha.post_fifo(Event(signal=signals.Other_Advance_War_Cry))
  oha.post_fifo(Event(signal=signals.Other_Retreat_Ready_War_Cry))
  oha.post_fifo(Event(signal=signals.Advance_War_Cry))
  oha.post_fifo(Event(signal=signals.Advance_War_Cry))
  oha.complete_circuit()
  expected_empathy_trace = \
  '''
  [10:59:17.592835] [other] e->start_at() top->not_waiting
  [10:59:17.593095] [other] e->Other_Retreat_Ready_War_Cry() not_waiting->waiting
  [10:59:17.593384] [other] e->Retreat_War_Cry() waiting->not_waiting
  [10:59:17.593570] [other] e->Advance_War_Cry() not_waiting->dead
  [10:59:17.593886] [other] e->Other_Advance_War_Cry() dead->not_waiting
  [10:59:17.594120] [other] e->Other_Retreat_Ready_War_Cry() not_waiting->waiting
  [10:59:17.594381] [other] e->Advance_War_Cry() waiting->not_waiting
  [10:59:17.594557] [other] e->Advance_War_Cry() not_waiting->dead
  '''
  time.sleep(1.0)
  with stripped(expected_empathy_trace) as stripped_target, \
       stripped(oha.trace()) as stripped_trace_result:

    for target, result in zip(stripped_target, stripped_trace_result):
      assert(target == result)

  # Test that our horse archer can actually use his empathy HSM
  # stop time for the horse archer so that we can test his empathy reactions
  archer.cancel_events(Event(signal=signals.Second))
  time.sleep(1.0)
  archer.live_trace = False  # stop looking at his reactions

  # get the name of his first and last brother in arms
  others = list(archer.others.keys())
  others.sort()
  first_brothers_name = others[0]
  empathy_for_first_brother = \
    archer.others[first_brothers_name]

  last_brothers_name = others[-1]
  print(archer.others[last_brothers_name].trace())
  print(archer.others[first_brothers_name].trace())

  # confirm paths in empathy chart
  # confirm not_waiting paths
  archer.post_fifo(
    Event(
      signal=signals.Other_Advance_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Skirmish_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Retreat_War_Cry,
      payload=first_brothers_name))

  # confirm path to dead
  archer.post_fifo(
    Event(
      signal=signals.Advance_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Advance_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Retreat_War_Cry,
      payload=first_brothers_name))

  # confirm path to waiting
  archer.post_fifo(
    Event(
      signal=signals.Other_Retreat_Ready_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Ready_War_Cry,
      payload=first_brothers_name))

  # confirm paths from waiting to not waiting
  archer.post_fifo(
    Event(
      signal=signals.Other_Retreat_Ready_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Advance_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Retreat_Ready_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Retreat_War_Cry,
      payload=first_brothers_name))

  time.sleep(1.1)
  print(empathy_for_first_brother.trace())

  # start time
  archer.post_fifo(
    Event(signal=signals.ResetTactic))
  # wait a bit
  archer.live_trace = True
  time.sleep(3)
  # stop time
  archer.cancel_events(
    Event(signal=signals.Second))

  # get first brother
  others = list(archer.others.keys())
  others.sort()
  first_brothers_name = others[0]
  empathy_for_first_brother = \
    archer.others[first_brothers_name]

  # prime the pump and clear the trace of the first brother
  archer.post_fifo(
    Event(
      signal=signals.Other_Advance_War_Cry,
      payload=first_brothers_name))
  time.sleep(1.0)
  empathy_for_first_brother.clear_trace()

  # confirm paths in empathy chart
  # confirm not_waiting paths
  archer.post_fifo(
    Event(
      signal=signals.Other_Advance_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Skirmish_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Retreat_War_Cry,
      payload=first_brothers_name))

  # confirm path to dead
  archer.post_fifo(
    Event(
      signal=signals.Advance_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Advance_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Retreat_War_Cry,
      payload=first_brothers_name))

  # confirm path to waiting
  archer.post_fifo(
    Event(
      signal=signals.Other_Retreat_Ready_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Ready_War_Cry,
      payload=first_brothers_name))

  # confirm paths from waiting to not waiting
  archer.post_fifo(
    Event(
      signal=signals.Other_Retreat_Ready_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Advance_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Other_Retreat_Ready_War_Cry,
      payload=first_brothers_name))
  archer.post_fifo(
    Event(
      signal=signals.Retreat_War_Cry,
      payload=first_brothers_name))

  # wait a bit
  time.sleep(1.1)

  # compare trace output with expected output (remove name)
  expected_empathy_target_trace = \
'''
[2018-03-01 07:06:53.426020] [Altan_192.168.0.10] e->Other_Advance_War_Cry() not_waiting->not_waiting
[2018-03-01 07:06:53.427078] [Altan_192.168.0.10] e->Other_Skirmish_War_Cry() not_waiting->not_waiting
[2018-03-01 07:06:53.431441] [Altan_192.168.0.10] e->Other_Retreat_War_Cry() not_waiting->not_waiting
[2018-03-01 07:06:53.446427] [Altan_192.168.0.10] e->Advance_War_Cry() not_waiting->dead
[2018-03-01 07:06:53.450818] [Altan_192.168.0.10] e->Other_Advance_War_Cry() dead->not_waiting
[2018-03-01 07:06:53.451772] [Altan_192.168.0.10] e->Retreat_War_Cry() not_waiting->dead
[2018-03-01 07:06:53.452617] [Altan_192.168.0.10] e->Other_Retreat_Ready_War_Cry() dead->waiting
[2018-03-01 07:06:53.453089] [Altan_192.168.0.10] e->Other_Ready_War_Cry() waiting->waiting
[2018-03-01 07:06:53.453579] [Altan_192.168.0.10] e->Other_Retreat_Ready_War_Cry() waiting->waiting
[2018-03-01 07:06:53.454506] [Altan_192.168.0.10] e->Advance_War_Cry() waiting->not_waiting
[2018-03-01 07:06:53.457566] [Altan_192.168.0.10] e->Other_Retreat_Ready_War_Cry() not_waiting->waiting
[2018-03-01 07:06:53.458497] [Altan_192.168.0.10] e->Retreat_War_Cry() waiting->not_waiting
'''
  with stripped(expected_empathy_target_trace) as stripped_target, \
       stripped(empathy_for_first_brother.trace()) as stripped_trace_result:
    for target, result in zip(stripped_target, stripped_trace_result):
      assert(target == result)
