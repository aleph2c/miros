import uuid
import time
import random
from miros.hsm import pp
from miros.hsm import HsmWithQueues, spy_on, stripped
from miros.activeobject import Factory
from miros.event import signals, Event, return_status
import mesh_network


'''
[ Chart: empathy (ip) ] (10 per horse archer)
  top     not_waiting                        waiting                       dead
   +-start_at->|                                |                            |
   |     (?)   |                                |                            |
   |           +-Other_Retreat_Ready_War_Cry()->|                            |
   |           |              (?)               |                            |
   |           |                                +<----Retreat_War_Cry()------|
   |           |                                |            (?)             |
   |           +-------Advance_War_Cry()--------+--------------------------->|
   |           |              (?)               |                            |
   |           +<-------------------------------+--Other_Advance_War_Cry()---|
   |           |                                |            (?)             |
   |           +-Other_Retreat_Ready_War_Cry()->|                            |
   |           |              (?)               |                            |
   |           |                                +<----Advance_War_Cry()------|
   |           |                                |            (?)             |
   |           +-------Advance_War_Cry()--------+--------------------------->|
   |           |              (?)               |                            |
   |           +<-------------------------------+--Other_Advance_War_Cry()---|
   |           |                                |            (?)             |
'''
@spy_on
def empathy(other, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.INIT_SIGNAL):
    status = other.trans(not_waiting)
  elif(e.signal == signals.Other_Advance_War_Cry or
       e.signal == signals.Other_Skirmish_War_Cry or
       e.signal == signals.Other_Retreat_War_Cry):
    status = other.trans(not_waiting)
  elif(e.signal == signals.Other_Retreat_Ready_War_Cry or
       e.signal == signals.Other_Ready_War_Cry):
    status = other.trans(waiting)
  else:
    status, other.temp.fun = return_status.SUPER, other.top
  return status

@spy_on
def not_waiting(other, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.Retreat_War_Cry):
    status = other.trans(dead)
  elif(e.signal == signals.Advance_War_Cry):
    status = other.trans(dead)
  else:
    status, other.temp.fun = return_status.SUPER, empathy
  return status

@spy_on
def dead(other, e):
  status = return_status.UNHANDLED
  status, other.temp.fun = return_status.SUPER, empathy
  return status

@spy_on
def waiting(other, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.Advance_War_Cry):
    status = other.trans(not_waiting)
  elif(e.signal == signals.Retreat_War_Cry):
    status = other.trans(not_waiting)
  else:
    status, other.temp.fun = return_status.SUPER, not_waiting
  return status

class OtherHorseArcher(HsmWithQueues):

  def __init__(self, name='other', ip=None, time_compression=1.0):
    super().__init__(name)
    self.name = name
    self.ip   = ip

  def dead(self):
    result = self.state_name == 'dead'
    return result

  def waiting(self):
    result = self.state_name == 'waiting'
    return result

  def not_waiting(self):
    result = self.state_name == 'not_waiting'
    return result

class HorseArcher(Factory):

  MAXIMUM_ARROW_CAPACITY = 60

  def __init__(self, name=None, time_compression=1.0, rabbit_user=None, rabbit_password=None, rabbit_port=None):

    if rabbit_user is None or rabbit_password is None:
      raise("need to provide RabbitMq server credentials")

    if rabbit_port is None:
      rabbit_port = 5672

    self.name = name
    self.routing_key = 'archer.{}'.format(name)

    super().__init__(name)
    self.arrows = 0
    self.ticks  = 0
    self.time_compression = time_compression
    self.others = {}

    self.mesh_tx = mesh_network.MeshTransmitter(
      user=rabbit_user,
      password=rabbit_password,
      port=rabbit_port)

    def mesh_rx_callback(ch, method, properties, body):
      if isinstance(body, Event):
        name_of_other = body.payload
        self.add_member_if_needed(name_of_other)
        if name_of_other != self.name:
          #  print(" [+] {}:{}".format(method.routing_key, body))
          self.post_fifo(body)

    self.mesh_rx = mesh_network.MeshReceiver(
      user=rabbit_user,
      password=rabbit_password,
      port=rabbit_port,
      routing_key='archer.#'
    )

    self.mesh_rx.register_live_callback(mesh_rx_callback)
    self.mesh_rx.start_consuming()

  def enable_snoop(self, live_trace=True, live_spy=False):
    '''
    Attach this node to the snoop mesh network.  Connect it's spy and trace
    output to the spy and trace 'fanout' exchanges

    Start consuming other spy and trace messaging
    '''
    self.snoop_tx = mesh_network.SnoopTransmitter(
      user='bob',
      password='dobbs',
      port=5672,
      encryption_key=
      b'lV5vGz-Hekb3K3396c9ZKRkc3eDIazheC4kow9DlKY0=')

    self.snoop_rx = mesh_network.SnoopReceiver(
      user='bob',
      password='dobbs',
      port=5672,
      encryption_key=
      b'lV5vGz-Hekb3K3396c9ZKRkc3eDIazheC4kow9DlKY0=')

    #  You can also tie a live_spy and live_trace callback method:
    def custom_spy_callback(ch, method, properties, body):
      print(" [+s] {}".format(body))

    def custom_trace_callback(ch, method, properties, body):
      body = body.replace('\n', '')
      print(" [+t] {}".format(body))

    self.snoop_rx.register_live_spy_callback(custom_spy_callback)
    self.snoop_rx.register_live_trace_callback(custom_trace_callback)

    self.live_trace = live_trace
    self.live_spy = live_spy
    self.register_live_spy_callback(archer.snoop_tx.broadcast_spy)
    self.register_live_trace_callback(archer.snoop_tx.broadcast_trace)

    self.snoop_rx.start_consuming()

  def disable_snoop(self):

    self.snoop_rx.stop_consuming()

    self.register_live_spy_callback(
      HsmWithQueues.live_spy_callback_default)

    self.register_live_trace_callback(
      HsmWithQueues.live_spy_callback_default)

  def yell(self, event):
    self.mesh_tx.message_to_other_channels(event, routing_key=self.routing_key)

  def compress(self, time_in_seconds):
    return 1.0 * time_in_seconds / self.time_compression

  def to_time(self, time_in_seconds):
    return self.compress(time_in_seconds)

  def add_member_if_needed(self, other_archer_name):
    if self.name != other_archer_name:
      if other_archer_name not in self.others:
        oha = OtherHorseArcher(other_archer_name)
        oha.start_at(empathy)
        self.others[other_archer_name] = oha

  @staticmethod
  def get_a_name():
    archer_root = random.choice([
      'Hulagu', 'Hadan', 'Gantulga', 'Ganbaatar',
      'Narankhuu', 'Ihbarhasvad', 'Nergui',
      'Narantuyaa', 'Altan', 'Gandbold'])
    archer_name = "{}.{}".format(
      archer_root,
      str(uuid.uuid5(uuid.NAMESPACE_DNS, archer_root))[0:5])
    return archer_name

def battle_entry(archer, e):
  archer.yell(Event(signal=signals.Annouce_Arrival_To_Unit, payload=archer.name))
  return return_status.HANDLED

def battle_field_announcement(archer, e):
  other_archer_name = e.payload
  archer.add_member_if_needed(other_archer_name)
  return return_status.HANDLED

def battle_init(archer, e):
  return archer.trans(deceit_in_detail)

# Deceit-In-Detail-Tactic state callbacks
def didt_entry(archer, e):
  '''Load up on arrows and start tracking time within this tactic'''
  archer.arrows = HorseArcher.MAXIMUM_ARROW_CAPACITY
  archer.ticks  = 0
  archer.post_fifo(
    Event(signal=signals.Second),
    times=0,
    period=archer.to_time(1.0),
    deferred=True)
  return return_status.HANDLED

def didt_exit(archer, e):
  '''Load up on arrows and start tracking time within this tactic'''
  archer.cancel_events(Event(signal=signals.Second))
  return return_status.HANDLED

def didt_init(archer, e):
  '''Immediately advance'''
  return archer.trans(advance)

def didt_second(archer, e):
  '''A second within the tactic has passed'''
  archer.ticks += 1
  return return_status.HANDLED

def didt_senior_advance_war_cry(archer, e):
  '''A Horse archer heard a command from a senior officer.  They give this
     senior officer's war cry to themselves as if they thought of it'''
  archer.post_fifo(Event(signal=signals.Advance_War_Cry))
  return return_status.HANDLED

def didt_advance_war_cry(archer, e):
  '''Yell out "advance war cry" to others and introspect on the state of the
     unit'''
  archer.yell(Event(signal=signals.Other_Advance_War_Cry, payload=archer.name))
  for name, other in archer.others.items():
    other.dispatch(e)
  return archer.trans(advance)

def didt_other_advance_war_cry(archer, e):
  '''A horse archer heard another's Advance_War_Cry, so so they
     give the command to and introspect on the state of their unit'''
  archer.post_fifo(Event(signal=signals.Advance_War_Cry))
  name = e.payload
  archer.others[name].dispatch(e)
  return archer.trans(advance)

def didt_other_retreat_war_cry(archer, e):
  name = e.payload
  archer.others[name].dispatch(e)
  return archer.trans(feigned_retreat)

def didt_skirmish_war_cry(archer, e):
  '''Yell out "skirmish war cry" to others'''
  archer.yell(Event(signal=signals.Other_Skirmish_War_Cry, payload=archer.name))
  return archer.trans(skirmish)

def didt_other_skirmish_war_cry(archer, e):
  '''A horse archer heard another's Skirmish_War_Cry, so they
     give the command to and introspect on the state of their unit'''
  archer.post_fifo(Event(signal=signals.Skirmish_War_Cry))
  name = e.payload
  archer.others[name].dispatch(e)
  return archer.trans(skirmish)

def didt_retreat_war_cry(archer, e):
  '''Yell out the "retreat war cry" and introspect on the state of the unit'''
  archer.yell(Event(signal=signals.Other_Retreat_War_Cry, payload=archer.name))
  for name, other in archer.others.items():
    other.dispatch(e)
  return archer.trans(feigned_retreat)

def didt_other_retreat_ready_war_cry(archer, e):
  name = e.payload
  archer.others[name].dispatch(e)
  return return_status.HANDLED

def didt_other_ready_war_cry(archer, e):
  name = e.payload
  archer.others[name].dispatch(e)
  return return_status.HANDLED

def didt_other_reset_tactic(archer, e):
  return archer.trans(deceit_in_detail)

# Advance callbacks
def advance_entry(archer, e):
  '''Upon entering the advanced state wait 3 seconds then issue
     Close_Enough_For_Circle war cry'''
  archer.post_fifo(
    Event(signal=signals.Close_Enough_For_Circle),
    times=1,
    period=archer.to_time(3.0),
    deferred=True)
  return return_status.HANDLED

def advance_exit(archer, e):
  '''Upon entering the advanced state wait 3 seconds then issue
     Close_Enough_For_Circle war cry'''
  archer.cancel_events(Event(signal=signals.Close_Enough_For_Circle))
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
  name = e.payload
  archer.others[name].dispatch(e)
  return return_status.HANDLED

def advance_close_enough_for_circle(archer, e):
  '''The Horse Archer is close enough to begin a Circle and Fire maneuver'''
  return archer.trans(circle_and_fire)

# Circle-And-Fire callbacks
def caf_second(archer, e):
  '''A horse archer can fire 1 to 3 arrows at a time in this maneuver,
     how they behave is up to them and how they respond
     to their local conditions'''
  if(archer.ticks % 6 == 0):  # second attack already!
    archer.arrows -= random.randint(1, 3)
    archer.scribble('arrows left {}'.format(archer.arrows))
  if archer.arrows < 20:
    archer.post_fifo(
      Event(signal=
        signals.Skirmish_War_Cry))
  archer.ticks += 1
  return return_status.HANDLED

# Skirmish state callbacks
def skirmish_entry(archer, e):
  '''The Horse Archer will trigger an Ammunition_Low event if he
     has less than 10 arrows when he begins skirmishing'''
  # a Knight could charge at him sometime between 40-120 sec
  # once he enters the skirmish state
  archer.post_fifo(
    Event(signal=signals.Officer_Lured),
    times=1,
    period=archer.to_time(random.randint(40, 200)),
    deferred=True)

  if archer.arrows < 10:
    archer.post_fifo(Event(signal=signals.Ammunition_Low))
  return return_status.HANDLED

def skirmish_exit(archer, e):
  archer.cancel_events(Event(signal=signals.Retreat_War_Cry))
  archer.cancel_events(Event(signal=signals.Officer_Lured))
  return return_status.HANDLED

def skirmish_second(archer, e):
  '''Every 3 seconds the horse archer fires an arrow, if he has
     less than 10 arrows he will trigger an Ammunition_Low event'''
  # While skirmishing, he makes directed attacks on his enemy
  # 40 percent chance of making a shot every 3 seconds
  if archer.ticks % 3 == 0:
    if random.randint(1, 10) <= 4:
      archer.arrows -= 1
      archer.scribble('arrows left {}'.format(archer.arrows))
  if archer.arrows < 10:
    archer.post_fifo(Event(signal=signals.Ammunition_Low))
  archer.ticks += 1
  return return_status.HANDLED

def skirmish_officer_lured(archer, e):
  '''If Horse Archer lures an enemy officer they issue a
     Retreat_War_Cry event.'''
  print("Knight Charging")
  archer.scribble("Knight Charging")
  archer.post_fifo(
    Event(signal=signals.Retreat_War_Cry))
  return return_status.HANDLED

def skirmish_ammunition_low(archer, e):
  '''If Horse Archer is low ammunition they will give
     a Retreat_War_Cry'''
  archer.post_fifo(Event(signal=signals.Retreat_Ready_War_Cry))
  return return_status.HANDLED

def skirmish_senior_squirmish_war_cry(archer, e):
  '''Ignore skirmish war cries from other while skirmishing'''
  return return_status.HANDLED

def skirmish_other_squirmish_war_cry(archer, e):
  '''Ignore skirmish war cries from other while skirmishing'''
  name = e.payload
  archer.others[name].dispatch(e)
  return return_status.HANDLED

def skirmish_retreat_ready_war_cry(archer, e):
  '''If all other horse archers are ready for a return, issue a
     Retreat_War_Cry, if not or either way transition into the
     waiting_to_lure state'''
  ready = True
  archer.yell(Event(signal=signals.Other_Retreat_Ready_War_Cry,
    payload=archer.name))
  for name, other in archer.others.items():
    if other.dead() is not True:
      ready &= other.waiting()
  if ready:
    # let's make sure Gandbold isn't a chicken
    delay_time = random.randint(10, 30)
    archer.post_fifo(
      Event(signal=signals.Retreat_War_Cry),
      times=1,
      period=archer.to_time(delay_time),
      deferred=True)
  return archer.trans(waiting_to_lure)


# Waiting-to-Lure callbacks
def wtl_entry(archer, e):
  archer.scribble('put away bow')
  archer.scribble('pull scimitar')
  archer.scribble('act scared')
  return return_status.HANDLED

def wtl_second(archer, e):
  archer.ticks += 1
  return return_status.HANDLED

def wtl_exit(archer, e):
  archer.scribble('stash scimitar')
  archer.scribble('pull bow')
  archer.scribble('stop acting')
  return return_status.HANDLED

# Feigned-Retreat callbacks
def fr_entry(archer, e):
  archer.scribble('fire on knights')
  archer.scribble('fire on footman')
  if archer.arrows == 0:
    archer.post_fifo(
      Event(signal=signals.Out_Of_Arrows))
  return return_status.HANDLED

def fr_exit(archer, e):
  archer.cancel_events(Event(signal=signals.Out_Of_Arrows))
  archer.scribble("full gallop")
  return return_status.HANDLED

def fr_second(archer, e):
  if archer.ticks % 3 == 0:
    if random.randint(1, 10) <= 8:
      archer.arrows -= 1
      archer.scribble('arrows left {}'.format(archer.arrows))
    if archer.arrows == 0:
      archer.post_fifo(
        Event(signal=signals.Out_Of_Arrows))
  archer.ticks += 1
  return return_status.HANDLED

def fr_retreat_war_cry(archer, e):
  name = e.payload
  archer.others[name].dispatch(e)
  return return_status.HANDLED

def fr_other_retreat_war_cry(archer, e):
  name = e.payload
  archer.others[name].dispatch(e)
  return return_status.HANDLED

def fr_out_of_arrows(archer, e):
  return archer.trans(marshal)

# Marshal callbacks
def marshal_entry(archer, e):
  archer.scribble("halt horse")
  archer.scribble("identify next marshal point")
  archer.scribble("field wrap wounds on self and horse")
  archer.scribble("drink water")
  archer.post_fifo(
    Event(signal=signals.Ready),
    times=1,
    period=archer.to_time(3),
    deferred=True)
  return return_status.HANDLED

def marshal_ready(archer, e):
  ready = True
  archer.yell(
    Event(signal=signals.Other_Ready_War_Cry,
    payload=archer.name))
  for name, other in archer.others.items():
    if other.dead() is not True:
      ready &= other.waiting()
  if ready:
    archer.post_fifo(
      Event(signal=signals.Advance_War_Cry))
  return archer.trans(waiting_to_advance)

# Waiting-to-Advance callbacks
def wta_entry(archer, e):
  archer.arrows = HorseArcher.MAXIMUM_ARROW_CAPACITY

  archer.post_fifo(Event(signal=signals.Advance_War_Cry),
    times=1,
    period=archer.to_time(random.randint(30, 120)),
    deferred=True)
  return return_status.HANDLED

def wta_exit(archer, e):
  archer.cancel_events(Event(signal=signals.Advance_War_Cry))
  return return_status.HANDLED

# Create the archer
archer = HorseArcher(
  name = HorseArcher.get_a_name(),
  rabbit_user='bob',
  rabbit_password='dobbs',
  rabbit_port=5672
)

# Create the archer states
battle = archer.create(state='battle'). \
  catch(
    signal=signals.ENTRY_SIGNAL,
    handler=battle_entry). \
  catch(
    signal=signals.INIT_SIGNAL,
    handler=battle_init). \
  catch(
    signal=signals.Annouce_Arrival_To_Unit,
    handler=battle_field_announcement). \
  to_method()

deceit_in_detail = archer.create(state='deceit_in_detail'). \
  catch(
    signal=signals.ENTRY_SIGNAL,
    handler=didt_entry). \
  catch(
    signal=signals.INIT_SIGNAL,
    handler=didt_init). \
  catch(
    signal=signals.Second,
    handler=didt_second). \
  catch(
    signal=signals.Senior_Advance_War_Cry,
    handler=didt_senior_advance_war_cry). \
  catch(
    signal=signals.Advance_War_Cry,
    handler=didt_advance_war_cry). \
  catch(
    signal=signals.Other_Advance_War_Cry,
    handler=didt_other_advance_war_cry). \
  catch(
    signal=signals.Skirmish_War_Cry,
    handler=didt_skirmish_war_cry). \
  catch(
    signal=signals.Other_Skirmish_War_Cry,
    handler=didt_other_skirmish_war_cry). \
  catch(
    signal=signals.Retreat_War_Cry,
    handler=didt_retreat_war_cry). \
  catch(
    signal=signals.Other_Retreat_War_Cry,
    handler=didt_other_retreat_war_cry). \
  catch(
    signal=signals.Other_Retreat_Ready_War_Cry,
    handler=didt_other_retreat_ready_war_cry). \
  catch(
    signal=signals.Other_Ready_War_Cry,
    handler=didt_other_ready_war_cry). \
  catch(
    signal=signals.ResetTactic,
    handler=didt_other_reset_tactic). \
  to_method()

advance = archer.create(state='advance'). \
  catch(
    signal=signals.ENTRY_SIGNAL,
    handler=advance_entry).  \
  catch(
    signal=signals.EXIT_SIGNAL,
    handler=advance_exit).  \
  catch(
    signal=signals.Senior_Advance_War_Cry,
    handler=advance_senior_advanced_war_cry).  \
  catch(
    signal=signals.Other_Advance_War_Cry,
    handler=advance_other_advanced_war_cry).  \
  catch(
    signal=signals.Close_Enough_For_Circle,
    handler=advance_close_enough_for_circle). \
  to_method()

circle_and_fire = archer.create(state='circle_and_fire'). \
  catch(
    signal=signals.Second,
    handler=caf_second). \
  to_method()

skirmish = archer.create(state='skirmish'). \
  catch(
    signal=signals.ENTRY_SIGNAL,
    handler=skirmish_entry). \
  catch(
    signal=signals.EXIT_SIGNAL,
    handler=skirmish_exit). \
  catch(
    signal=signals.Second,
    handler=skirmish_second). \
  catch(
    signal=signals.Officer_Lured,
    handler=skirmish_officer_lured). \
  catch(
    signal=signals.Ammunition_Low,
    handler=skirmish_ammunition_low). \
  catch(
    signal=signals.Senior_Skirmish_War_Cry,
    handler=skirmish_senior_squirmish_war_cry). \
  catch(
    signal=signals.Other_Skirmish_War_Cry,
    handler=skirmish_other_squirmish_war_cry). \
  catch(
    signal=signals.Retreat_Ready_War_Cry,
    handler=skirmish_retreat_ready_war_cry). \
  to_method()

waiting_to_lure = archer.create(state='waiting_to_lure'). \
  catch(
    signal=signals.ENTRY_SIGNAL,
    handler=wtl_entry). \
  catch(
    signal=signals.EXIT_SIGNAL,
    handler=wtl_exit). \
  catch(
    signal=signals.Second,
    handler=wtl_second). \
  to_method()

feigned_retreat = archer.create(state='feigned_retreat'). \
  catch(
    signal=signals.ENTRY_SIGNAL,
    handler=fr_entry). \
  catch(
    signal=signals.EXIT_SIGNAL,
    handler=fr_exit). \
  catch(
    signal=signals.Second,
    handler=fr_second). \
  catch(
    signal=signals.Out_Of_Arrows,
    handler=fr_out_of_arrows). \
  catch(
    signal=signals.Retreat_War_Cry,
    handler=fr_retreat_war_cry). \
  catch(
    signal=signals.Other_Retreat_War_Cry,
    handler=fr_other_retreat_war_cry). \
  to_method()

marshal = archer.create(state='marshal'). \
  catch(
    signal=signals.ENTRY_SIGNAL,
    handler=marshal_entry). \
  catch(
    signal=signals.Ready,
    handler=marshal_ready). \
  to_method()

waiting_to_advance = archer.create(state='waiting_to_advance'). \
  catch(
    signal=signals.ENTRY_SIGNAL,
    handler=wta_entry). \
  catch(
    signal=signals.EXIT_SIGNAL,
    handler=wta_exit). \
  to_method()

archer.nest(battle, parent=None). \
  nest(deceit_in_detail, parent=battle). \
  nest(advance, parent=deceit_in_detail). \
  nest(circle_and_fire, parent=advance). \
  nest(skirmish, parent=deceit_in_detail). \
  nest(waiting_to_lure, parent=skirmish). \
  nest(feigned_retreat, parent=deceit_in_detail). \
  nest(marshal, parent=deceit_in_detail). \
  nest(waiting_to_advance, parent=marshal)

if __name__ == '__main__':
  # build a horse archer and rev his time by 100
  print(archer.name)
  archer.time_compression = 100
  archer.start_at(battle)
  archer.enable_snoop(live_trace=True)
  archer.post_fifo(Event(signal=signals.Senior_Advance_War_Cry))
  time.sleep(15.0)

# empathy_for_first_brother

  # time.sleep(1.0)
  # with stripped(expected_empathy_target_trace) as stripped_target, \
  #      stripped(oha.trace()) as stripped_trace_result:

  #   for target, result in zip(stripped_target, stripped_trace_result):
  #     assert(target == result)
  # time.sleep(200)

  # ips =  ['192.168.0.2', '192.168.0.3',
  #         '192.168.0.4', '192.168.0.5',
  #         '192.168.0.6', '192.168.0.7',
  #         '192.168.0.8', '192.168.0.9',
  #         '192.168.0.10']

  # names = ['Hulagu', 'Hadan',
  #          'Gantulga', 'Ganbaatar',
  #          'Narankhuu', 'Ihbarhasvad',
  #          'Nergui', 'Narantuyaa',
  #          'Altan']

  # empathy_names = list(map(str.__add__, [name + '_' for name in names], ips))

  # ohas = [OtherHorseArcher(empathy_name) for empathy_name in empathy_names]
  # for oha in ohas:
  #   oha.start_at(empathy)

