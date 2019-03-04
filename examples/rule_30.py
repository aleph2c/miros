import subprocess
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from miros import Event
from miros import signals
from miros import HsmWithQueues
from miros import return_status

from collections import deque
import math

Black   = 0.9
Default = 0.5
White   = 0.1

class Wall(HsmWithQueues):

  def __init__(self, name='wall'):
    super().__init__(name)
    self.color = None

  def color_number(self):
    return Black if self.color == 'black' else White

def fake_white(wall, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    wall.color = 'white'
    status = return_status.HANDLED
  elif(e.signal == signals.Next):
    status = return_status.HANDLED
  else:
    wall.temp.fun = wall.top
    status = return_status.SUPER
  return status

def fake_black(wall, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    wall.color = 'black'
    status = return_status.HANDLED
  elif(e.signal == signals.Next):
    status = return_status.HANDLED
  else:
    wall.temp.fun = wall.top
    status = return_status.SUPER
  return status

class WallLeftWhiteRightWhite(Wall):
  left_wall = fake_white
  right_wall = fake_white

class WallLeftWhiteRightBlack(Wall):
  left_wall = fake_white
  right_wall = fake_black

class WallLeftBlackRightWhite(Wall):
  left_wall = fake_black
  right_wall = fake_white

class WallLeftBlackRightBlack(Wall):
  left_wall = fake_black
  right_wall = fake_black

class Rule30(Wall):

  def __init__(self, name='cell'):
    super().__init__(name)
    self.left = None
    self.right = None
    self.color = None

def white(cell, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    cell.color = 'white'
    status = return_status.HANDLED
  elif(e.signal == signals.Next):
    if((cell.right.color == 'black' and
        cell.left.color == 'white') or 
       (cell.right.color == 'white' and
        cell.left.color == 'black')):
      status = cell.trans(black)
    else:
      status = return_status.HANDLED
  else:
    cell.temp.fun = cell.top
    status = return_status.SUPER
  return status

class Rule30WithQueueDepth(Rule30):

  def __init__(self, name='cell'):
    super().__init__(name)

  @staticmethod
  def queue_depth(cells_per_generation): 

    # From visual inspection with a protractor:
    # 15 cell_per_generation -> 50 degrees
    # 20 cell_per_generation -> 50, then 60
    # 25 cell_per_generation -> 50, then 60, then 65
    # 30 cell_per_generation -> 50, then 60, then 70
    # 40 cell_per_generation -> around 70
    # 50 cell_per_generation -> around 70
    if cells_per_generation <= 15:
      degrees = 50
    elif cells_per_generation <= 20:
      degrees = 60
    elif cells_per_generation <= 25:
      degrees = 65
    else:
      degrees = 70
    qd = 1 + math.tan(math.radians(degrees))
    qd *= 0.5*cells_per_generation
    qd = math.floor(qd)
    return qd

def black(cell, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    cell.color = 'black'
    status = return_status.HANDLED
  elif(e.signal == signals.Next):
    if cell.left.color == 'black':
      status = cell.trans(white)
    else:
      status = return_status.HANDLED
  else:
    cell.temp.fun = cell.top
    status = return_status.SUPER
  return status

class TwoDCellularAutomata():
  def __init__(self, 
      generations, 
      cells_per_generation=None, 
      starting_machine=None,
      machine_cls=None,
      boundary_cls=None,
      ):

    # python automatically places the classes passed into this object as tuples,
    # this is surprising behavior but it is how it works, so we go with it
    self.machine_cls_tuple = machine_cls,
    self.boundary_cls_tuple = boundary_cls,

    if machine_cls is None:
      self.machine_cls_tuple = (Rule30,)

    if boundary_cls is None:
      self.boundary_cls_tuple = (WallLeftWhiteRightWhite,)

    self.generations = generations
    self.cells_per_generation = cells_per_generation

    # if they haven't specified cells_per_generation set it
    # so that the cells appear square on most terminals
    if cells_per_generation is None:
      # this number was discovered through trial and error
      # matplotlib seems to be ignoring the aspect ratio
      self.cells_per_generation = round(generations*17/12)

    self.starting_machine = round(self.cells_per_generation/2.0) \
      if starting_machine is None else starting_machine

    self.generation = None

    self.left_wall=self.boundary_cls_tuple[0].left_wall
    self.right_wall=self.boundary_cls_tuple[0].right_wall

  def make_and_start_left_boundary_machine(self):
    boundary = self.boundary_cls_tuple[0]()
    boundary.start_at(self.boundary_cls_tuple[0].left_wall)
    return boundary

  def make_and_start_right_boundary_machine(self):
    boundary = self.boundary_cls_tuple[0]()
    boundary.start_at(self.boundary_cls_tuple[0].right_wall)
    return boundary

  def initial_state(self):
    Z = np.full([self.generations, self.cells_per_generation], Black, dtype=np.float32)

    # create a collections of unstarted machines
    self.machines = []
    for i in range(self.cells_per_generation-2):
      self.machines.append(self.machine_cls_tuple[0]())

    left_wall = self.make_and_start_left_boundary_machine()
    right_wall = self.make_and_start_right_boundary_machine()

    # unstarted machines sandwiched between unstarted boundaries
    self.machines = [left_wall] + self.machines + [right_wall]

    # start the boundaries in their holding color
    self.machines[0].start_at(fake_white)
    self.machines[-1].start_at(fake_white)

    # start most of the machines in white except for the one in the center
    for i in range(1, len(self.machines)-1):
      if i != self.starting_machine:
        self.machines[i].start_at(white)
      else:
        self.machines[i].start_at(black)

    # we have created a generation, so count down by one
    self.generation = self.generations-1

    ## draw our boundaries once, since they aren't going to change
    Z[:, 0] = self.machines[0].color_number()
    Z[:, Z.shape[-1]-1] = self.machines[-1].color_number()

    self.Z = Z

  def next_generation(self):
    Z = self.Z
    if self.generation == self.generations-1:
      # draw the first row
      for i, machine in enumerate(self.machines):
        Z[self.generations-1, i] = machine.color_number()
    else:
      Z = self.Z
      new_machines = []
      for i in range(1, (len(self.machines)-1)):
        old_left_machine = self.machines[i-1]
        old_machine = self.machines[i]
        old_right_machine = self.machines[i+1]
        
        new_machine = self.machine_cls_tuple[0]()
        new_machine.start_at(old_machine.state_fn)
        new_machine.left = old_left_machine
        new_machine.right = old_right_machine
        new_machines.append(new_machine)

      left_wall = self.make_and_start_left_boundary_machine()
      right_wall = self.make_and_start_right_boundary_machine()
      new_machines = [left_wall] + new_machines + [right_wall]

      for i, machine in enumerate(new_machines):
        machine.dispatch(Event(signal=signals.Next))
        Z[self.generation, i] = machine.color_number()
      self.machines = new_machines[:]

    self.Z = Z
    self.generation -= 1

  def _Generation(self):
    self.initial_state()
    yield self.Z
    while True:
      self.next_generation()
      yield self.Z

class TwoDCellularAutonomataWallRecursion(TwoDCellularAutomata):

  def __init__(self, 
      generations, 
      cells_per_generation=None, 
      starting_machine=None,
      machine_cls=None,
      boundary_cls=None,
      order_scalar=None,
      ):

    super().__init__(
      generations,
      cells_per_generation,
      starting_machine,
      machine_cls,
      boundary_cls)

    half_point = round(self.cells_per_generation/2.0)
    self.core_machine_index = half_point
    self.order_scalar = order_scalar
    if order_scalar is None:
      self.order_scalar = 1

    if hasattr(machine_cls, 'queue_depth'):
      queue_depth = machine_cls.queue_depth(self.cells_per_generation)
      queue_depth *= self.order_scalar
    else:
      queue_depth = self.cells_per_generation*self.order_scalar/2.0
    queue_depth = math.floor(queue_depth)

    self.core_colors = deque(maxlen=queue_depth)
    self.core_code = []

    for i in range(4):
      self.core_colors.append('white')
      self.core_code.append(0)

    self.boundary_cls = WallLeftWhiteRightWhite

  def initial_state(self):
    super().initial_state()
    self.update_core_code()
    self.set_boundary_class()

  def next_generation(self):
    super().next_generation()
    self.update_core_code()
    self.set_boundary_class()

  def update_core_code(self):
    self.core_colors.append(self.machines[self.core_machine_index].color)
    self.core_code = [1 if i == 'black' else 0 for i in self.core_colors]

  def set_boundary_class(self):

    number = 0
    for index, value in enumerate(self.core_code[0:4]):
      number += value * 2**index

    if number == 1:
      cls = WallLeftWhiteRightBlack
    elif number == 2:
      cls = WallLeftBlackRightWhite
    elif number == 3:
      cls = WallLeftBlackRightBlack
    else:
      cls = WallLeftWhiteRightWhite

    self.boundary_cls = cls

  def make_and_start_left_boundary_machine(self):
    cls = self.boundary_cls
    boundary = cls()
    boundary.start_at(cls.left_wall)
    return boundary

  def make_and_start_right_boundary_machine(self):
    cls = self.boundary_cls
    boundary = cls()
    boundary.start_at(cls.right_wall)
    return boundary

class Canvas():
  def __init__(self, evolution, title=None):
    self.fig, self.ax = plt.subplots()
    if title:
      self.ax.set_title(title)
    self.evolution = evolution
    self.generation = evolution._Generation()
    self.ax.set_yticklabels([])
    self.ax.set_xticklabels([])
    self.ax.set_aspect(1.0)
    self.ax.xaxis.set_ticks_position('none')
    self.ax.yaxis.set_ticks_position('none')
    self.fig.tight_layout()
    self.cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
      'oranges', ['#ffffff', '#ffa501', '#b27300', '#191000'])
    self.grid = self.ax.pcolormesh(next(self.generation), cmap=self.cmap)

  def init(self):
    return (self.grid,)

  def animate(self, i):
    self.Z = next(self.generation)
    # set_array only accepts a 1D argument
    # so flatten Z before feeding it into the grid arg
    self.grid.set_array(self.Z.ravel())
    return (self.grid,)
  
  def run_animation(self, generations, interval):
    self.anim = animation.FuncAnimation(
      self.fig, self.animate, init_func=self.init,
      frames=generations, interval=interval,
      blit=False)
    return self.anim

  def save(self, generations, filename=None):
    plt.savefig(filename)

    if self.evolution.generation > 0:
      for i in range(self.evolution.generations):
        next(self.generation)
      self.ax.pcolormesh(self.evolution.Z, cmap=self.cmap)
      #self.Z = next(self.generation)
      #self.grid.set_array(self.Z.ravel())
      #self.ax.pcolormesh(self.evolution.Z, cmap=self.cmap)
    plt.savefig(filename) 

  def save_animation(self, filename):
    self.anim.save(filename) 

generations = 1200

## Eye scans
## 12, 2 * pump -- no repeat after 1200
## 11, 2 * pump -- no repeat after 1200
## 10, 1 * pump -- peudo-repeat seen within 1200
## 10, 2 * pump -- repeat seen within 1200
## 10, 3 * pump -- repeat seen within 1200
autonoma = TwoDCellularAutonomataWallRecursion(
  generations=generations,
  machine_cls=Rule30WithQueueDepth,
  cells_per_generation=15,
  order_scalar=1,
  )

#autonoma = TwoDCellularAutomata(
#  generations=generations,
#  machine_cls=Rule30,
#  cells_per_generation=50
#  )

eco = Canvas(autonoma)
# 43 seconds with generations = 200
eco.run_animation(generations, interval=10)
eco.save_animation('rule_30.mp4')

# 43 seconds with generations = 200
eco.save(0, 'rule_30.pdf')
#eco.save(0, 'rule_30.svg')

cmd = 'cmd.exe /C {} &'.format('rule_30.mp4')
subprocess.Popen(cmd, shell=True)

cmd = 'cmd.exe /C {} &'.format('rule_30.pdf')
subprocess.Popen(cmd, shell=True)
#
#cell = Rule30('bob')
