from miros.activeobject import Factory
from miros.event import signals, Event, return_status

class HorseArcher(Factory):

  MAXIMUM_ARROW_CAPACITY = 60

  def __init__(self):
    name = ''
    super().__init__(name)
    self.arrows = 0
    self.ticks  = 0
    self.others = []

  def yell(self, event):
    pass

def didt_entry(archer, e):
  '''load up on arrows and start time'''
  archer.arrows = HorseArcher.MAXIMUM_ARROW_CAPACITY
  archer.ticks  = 0

def didt_second(archer, e):
  '''A second within the tactic has pasted'''
  archer.tick += 1

def didt_senior_war_cry(archer, e):
  '''horse archer gives the senior officer's war cry to itself'''
  archer.post_fifo(e)

def didt_advance_war_cry(archer, e):
  '''yell out "advance war cry" to others and introspect on the state of the unit'''
  archer.yell(e)
  for ip, other in archer.others.items():
    other.dispatch(e)

if __name__ == '__main__':
  horse_archer = HorseArcher()
