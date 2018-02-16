import random
from miros.activeobject import Factory
from miros.event import signals, Event, return_status

class HorseArcher(Factory):

  MAXIMUM_ARROW_CAPACITY = 60

  def __init__(self, name='Gandbold'):
    super().__init__(name)
    self.arrows = 0
    self.ticks  = 0
    self.others = {}

  def yell(self, event):
    pass

# Deceit-In-Detail-Tactic state callbacks
def didt_entry(archer, e):
  '''Load up on arrows and start tracking time within this tactic'''
  archer.arrows = HorseArcher.MAXIMUM_ARROW_CAPACITY
  archer.ticks  = 0
  return return_status.HANDLED

def didt_second(archer, e):
  '''A second within the tactic has passed'''
  archer.tick += 1
  return return_status.HANDLED

def didt_senior_war_cry(archer, e):
  '''A Horse archer heard a command from a senior officer.  They give this
     senior officer's war cry to themselves as if they thought of it'''
  archer.post_fifo(e)
  return return_status.HANDLED

def didt_advance_war_cry(archer, e):
  '''Yell out "advance war cry" to others and introspect on the state of the
     unit'''
  archer.yell(e)
  for ip, other in archer.others.items():
    other.dispatch(e)
  return return_status.HANDLED

def didt_other_advance_war_cry(archer, e):
  '''A horse archer heard another's Advance_War_Cry, so so they
     give the command to and introspect on the state of their unit'''
  archer.post_fifo(Event(signal=signals.Advance_War_Cry))
  ip = e.payload['ip']
  archer.other[ip].dispatch(e)
  return archer.trans(advance)

def didt_skirmish_war_cry(archer, e):
  '''Yell out "skirmish war cry" to others'''
  archer.yell(e)
  return archer.trans(skirmish)

def didt_other_skirmish_war_cry(archer, e):
  '''A horse archer heard another's Skirmish_War_Cry, so so they
     give the command to and introspect on the state of their unit'''
  archer.post_fifo(Event(signal=signals.Skirmish_War_Cry))
  ip = e.payload['ip']
  archer.other[ip].dispatch(e)
  return archer.trans(skirmish)

def didt_retreat_war_cry(archer, e):
  '''Yell out the "retreat war cry" and introspect on the state of the unit'''
  archer.yell(e)
  for ip, other in archer.others.items():
    other.dispatch(e)
  return archer.trans(feigned_retreat)

# Advance callbacks
def advance_entry(archer, e):
  '''Upon entering the advanced state wait 3 seconds then issue
     Close_Enough_For_Circle war cry'''
  archer.post_fifo(
    Event(signal=signals.Close_Enough_For_Circle),
    times=1,
    period=3.0,
    deferred=True)
  return return_status.HANDLED

def advance_senior_advanced_war_cry(archer, e):
  '''Stop Senior_Advance_War_Cry events from being handled outside of this
     state, the horse archer is already in the process of performing the
     order.'''
  return return_status.HANDLED

def advance_other_advanced_war_cry(archer, e):
  '''Stop Other_Advance_War_Cry events from being handled outside of this
     state, the horse archer is already in the process of performing the
     order.'''
  return return_status.HANDLED

def advance_close_enough_for_circle(archer, e):
  '''The Horse Archer is close enough to begin a Circle and Fire maneuver'''
  return archer.trans(circle_and_fire)

# Circle-And-Fire callbacks
def caf_second(archer, e):
  '''A horse archer can fire 1 to 3 arrows at a time in this maneuver,
     how they behave is up to them and how they respond
     to their local conditions'''
  if(archer.tick % 8 == 0):
    archer.arrow -= random.randint(1, 3)
  if archer.arrows < 20:
    archer.post_fifo(
      Event(signal=
        signals.Skirmish_War_Cry))
  archer.tick += 1
  return return_status.HANDLED

# Skirmish state callbacks
def skirmish_entry(archer, e):
  '''The Horse Archer will trigger an Ammunition_Low event if he
     has less than 10 arrows when he begins skirmishing'''
  if archer.arrow < 10:
    archer.post_fifo(Event(signal=signals.Ammunition_Low))
  return return_status.HANDLED

def skirmish_second(archer, e):
  '''Every 3 seconds the horse archer fires an arrow, if he has
     less than 10 arrows he will trigger an Ammunition_Low event'''
  if archer.tick % 3 == 0:
    if random.randint(1, 10) <= 4:
      archer.arrows -= 1
  if archer.arrows < 10:
    archer.post_fifo(Event(signal=signals.Ammunition_Low))
  archer.ticks += 1

def skirmish_officer_lured(archer, e):
  '''If Horse Archer lures an enemy officer they issue a
     Retreat_War_Cry event.'''
  archer.post_fifo(
    Event(signal=signals.Retreat_War_Cry))
  return return_status.HANDLED

def skirmish_ammunition_low(archer, e):
  '''If Horse Archer is low on low on ammunition they will give
     a Retreat_War_Cry'''
  archer.post_fifo(Event(signal=signals.Retreat_War_Cry))
  return return_status.HANDLED

def skirmish_senior_officer_squirmish_war_cry(archer, e):
  '''Ignore skirmish war cries from other while skirmishing'''
  return return_status.HANDLED

def skirmish_other_squirmish_war_cry(archer, e):
  '''Ignore skirmish war cries from other while skirmishing'''
  return return_status.HANDLED

def skirmish_retreat_ready_war_cry(archer, e):
  '''If all other horse archers are ready for a return, issue a
     Retreat_War_Cry, if not or either way transition into the
     waiting_to_lure state'''
  ready = True
  for ip, other in archer.other.items():
    if other.state_name != 'dead':
      ready &= other.state_name == 'waiting'
  if ready:
    archer.post_fifo(Event(signal=signals.Retreat_War_Cry))
  return archer.trans(waiting_to_lure)



def advance(archer, e):
  pass

def circle_and_fire(archer, e):
  pass

def skirmish(archer, e):
  pass

def feigned_retreat(archer, e):
  pass

def waiting_to_lure(archer, e):
  pass

def marshal(archer, e):
  pass

def waiting_to_advance(archer, e):
  pass


if __name__ == '__main__':
  horse_archer = HorseArcher()
