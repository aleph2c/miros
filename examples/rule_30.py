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
import pathlib

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


class TwoDCellularAutomata():
  def __init__(self,
      generations,
      cells_per_generation=None,
      initial_condition_index=None,
      machine_cls=None, 
      wall_cls=None,
      ):
    '''Build a two dimensional cellular automata object which can be advanced with a coroutine.  

    **Args**:
       | ``generations`` (int): how many generations to run (vertical cells)
       | ``cells_per_generation=None`` (int): how many cells across
       | ``initial_condition_index=None`` (int): the starting index cell (make black)
       | ``machine_cls=None`` (Rule): which automata rule to follow
       | ``wall_cls=None`` (Wall): which wall rules to follow

    **Returns**:
       (TwoDCellularAutonomata): an automata object

    **Example(s)**:
      
    .. code-block:: python
     
      # build an automata using rule 30 with white walls
      # it should be 50 cells across
      # and it should run for 1000 generations
      autonoma = TwoDCellularAutomata(
        machine_cls=Rule30,
        generations=1000,
        wall_cls=WallLeftWhiteRightWhite,
        cells_per_generation=50
      )

      # to get the generator for this automata
      generation = automata.make_generation_coroutine()

      # to advance a generation (first one will initialize it)
      next(generation)

      # to get the color codes from it's two dimension array
      automata.Z

      # to advance a generation
      next(generation)

    '''
    # python automatically places the classes passed into this object as tuples,
    # this is surprising behavior but it is how it works, so we go with it
    self.machine_cls = machine_cls
    self.wall_cls = wall_cls

    if machine_cls is None:
      self.machine_cls = Rule30

    if wall_cls is None:
      self.wall_cls = WallLeftWhiteRightWhite

    self.generations = generations
    self.cells_per_generation = cells_per_generation

    # if they haven't specified cells_per_generation set it
    # so that the cells appear square on most terminals
    if cells_per_generation is None:
      # this number was discovered through trial and error
      # matplotlib seems to be ignoring the aspect ratio
      self.cells_per_generation = round(generations*17/12)

    self.initial_condition_index = round(self.cells_per_generation/2.0) \
      if initial_condition_index is None else initial_condition_index

    self.generation = None

    self.left_wall=self.wall_cls.left_wall
    self.right_wall=self.wall_cls.right_wall

  def make_and_start_left_wall_machine(self):
    '''make and start the left wall based on the wall_cls'''
    wall = self.wall_cls()
    wall.start_at(self.wall_cls.left_wall)
    return wall

  def make_and_start_right_wall_machine(self):
    '''make and start the right wall based on the wall_cls'''
    wall = self.wall_cls()
    wall.start_at(self.wall_cls.right_wall)
    return wall

  def initial_state(self):
    '''initialize the 2d cellular automata'''
    Z = np.full([self.generations, self.cells_per_generation], Black, dtype=np.float32)

    # create a collections of unstarted machines
    self.machines = []
    for i in range(self.cells_per_generation-2):
      self.machines.append(self.machine_cls())

    left_wall = self.make_and_start_left_wall_machine()
    right_wall = self.make_and_start_right_wall_machine()

    # unstarted machines sandwiched between unstarted boundaries
    self.machines = [left_wall] + self.machines + [right_wall]

    # start the boundaries in their holding color
    self.machines[0].start_at(fake_white)
    self.machines[-1].start_at(fake_white)

    # start most of the machines in white except for the one at the
    # intial_condition_index
    for i in range(1, len(self.machines)-1):
      if i != self.initial_condition_index:
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
    '''create the next row of the 2d cellular automata, update the color map Z'''
    Z = self.Z
    if self.generation == self.generations-1:
      # draw the first row
      for i, machine in enumerate(self.machines):
        Z[self.generations-1, i] = machine.color_number()
    else:
      # draw every other row
      Z = self.Z
      new_machines = []
      for i in range(1, (len(self.machines)-1)):
        old_left_machine = self.machines[i-1]
        old_machine = self.machines[i]
        old_right_machine = self.machines[i+1]
        
        new_machine = self.machine_cls()
        new_machine.start_at(old_machine.state_fn)
        new_machine.left = old_left_machine
        new_machine.right = old_right_machine
        new_machines.append(new_machine)

      left_wall = self.make_and_start_left_wall_machine()
      right_wall = self.make_and_start_right_wall_machine()
      new_machines = [left_wall] + new_machines + [right_wall]

      for i, machine in enumerate(new_machines):
        machine.dispatch(Event(signal=signals.Next))
        Z[self.generation, i] = machine.color_number()
      self.machines = new_machines[:]

    self.Z = Z
    self.generation -= 1

  def make_generation_coroutine(self):
    '''create a coroutine, which can be used as many times needed'''
    self.initial_state()
    yield self.Z
    while True:
      self.next_generation()
      yield self.Z

class TwoDCellularAutonomataWallRecursion(TwoDCellularAutomata):

  def __init__(self, 
      generations, 
      cells_per_generation=None, 
      initial_condition_index=None,
      machine_cls=None,
      wall_cls=None,
      order_scalar=None):
    '''short description

    longer description

    **Note**:
       Do this not that recommendation

    **Args**:
       | ``generations`` (type1): 
       | ``cell_per_generation`` (type1): 
       | ``initial_condition_index`` (type1): 
       | ``machine_cls`` (type1): 
       | ``wall_cls`` (type1): 
       | ``order_scalar`` (type1): 

    **Returns**:
       (type): 

    **Example(s)**:
      
    .. code-block:: python
       
       >>> [factorial(n) for n in range(6)]
       [1, 1, 2, 6, 24, 120]


    '''
    super().__init__(
      generations,
      cells_per_generation,
      initial_condition_index,
      machine_cls,
      wall_cls)

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

    self.wall_cls = WallLeftWhiteRightWhite

  def initial_state(self):
    super().initial_state()
    self.update_core_code()
    self.set_wall_class()

  def next_generation(self):
    super().next_generation()
    self.update_core_code()
    self.set_wall_class()

  def update_core_code(self):
    self.core_colors.append(self.machines[self.core_machine_index].color)
    self.core_code = [1 if i == 'black' else 0 for i in self.core_colors]

  def set_wall_class(self):

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

    self.wall_cls = cls

  def make_and_start_left_wall_machine(self):
    cls = self.wall_cls
    wall = cls()
    wall.start_at(cls.left_wall)
    return wall

  def make_and_start_right_wall_machine(self):
    cls = self.wall_cls
    wall = cls()
    wall.start_at(cls.right_wall)
    return wall

class Canvas():
  def __init__(self, automata, title=None):
    '''Animate 2D graphing paper, or static file describing a automata

    Given an autonoma, which has a ``make_generation_coroutine`` coroutine generator, an
    animation can be build by calling this coroutine for as many generations are
    required.

    **Note**:
       This ``automata`` object needs to provide a ``make_generation_coroutine`` method which
       returns a coroutine which can be called with ``next``.

    **Args**:
       | ``automata`` (TwoDCellularAutomata): 
       | ``title=None`` (string): An optional title

    **Returns**:
       (Canvas): this object

    **Example(s)**:
      
    .. code-block:: python
       
       eco1 = Canvas(autonoma)
       eco1.run_animation(1200, interval=10)  # 10 ms
       eco1.save('eco1.mp4')

       eco2 = Canvas(automata)
       eco2 = save('eco2.pdf, generations=100)

    '''
    self.fig, self.ax = plt.subplots()
    if title:
      self.ax.set_title(title)
    self.automata = automata
    self.generation = automata.make_generation_coroutine()
    self.ax.set_yticklabels([])
    self.ax.set_xticklabels([])
    self.ax.set_aspect(1.0)
    self.ax.xaxis.set_ticks_position('none')
    self.ax.yaxis.set_ticks_position('none')
    self.fig.tight_layout()
    # seventies orange/browns looking color map
    self.cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
      'oranges', ['#ffffff', '#ffa501', '#b27300', '#191000'])
    self.grid = self.ax.pcolormesh(next(self.generation), cmap=self.cmap)

  def init(self):
    '''animation initialization callback

    **Note**:
       This not needed by our animation, but it is needed by the library we are
       calling, so we just stub it out

    **Returns**:
       (tuple): (self.grid,)

    '''
    return (self.grid,)

  def animate(self, i):
    '''animation callback.

    This method will be called for each i frame of the animation.  It creates
    the next generation of the automata then it updates the pcolormesh using the
    set_array method.

    **Args**:
       | ``i`` (int): animation frame number

    **Returns**:
       (tuple): (self.grid,)

    '''
    self.Z = next(self.generation)
    # set_array only accepts a 1D argument
    # so flatten Z before feeding it into the grid arg
    self.grid.set_array(self.Z.ravel())
    return (self.grid,)
  
  def run_animation(self, generations, interval):
    '''Run an animation of the automata.

    **Args**:
       | ``generations`` (int): number of automata generations
       | ``interval`` (int): movie frame interval in ms

    **Example(s)**:
      
    .. code-block:: python
       
      eco = Canvas(automata)
      eco.run_animation(1200, interval=20)  # 20 ms

    '''
    self.anim = animation.FuncAnimation(
      self.fig, self.animate, init_func=self.init,
      frames=generations, interval=interval,
      blit=False)

  def save(self, filename=None, generations=0):
    '''save an animation or run for a given number of generations and save as a
       static file (pdf, svg, .. etc)

    **Note**:
       This function will save as many different static file formats as are
       supported by matplot lib, since it uses matplotlib.

    **Args**:
       | ``filename=None`` (string): name of the file
       | ``generations=0`` (int): generations to run if the files doesn't have a
       |                          'mp4' extension and hasn't been animated before


    **Example(s)**:

       eco1 = Canvas(autonoma)
       eco1.run_animation(50, 10)
       eco1.save('rule_30.mp4)
       eco1.save('rule_30.pdf)

       eco2 = Canvas(autonoma)
       eco1.save('rule_30.pdf', generations=40)

    '''
  def save(self, filename=None, generations=0):

    if pathlib.Path(filename).suffix == '.mp4':
      self.anim.save(filename) 
    else:
      if self.automata.generation > 0:
        for i in range(self.automata.generations):
          next(self.generation)
        self.ax.pcolormesh(self.automata.Z, cmap=self.cmap)
      plt.savefig(filename) 

generations = 200

## Eye scans
## 12, 2 * pump -- no repeat after 1200
## 11, 2 * pump -- no repeat after 1200
## 10, 1 * pump -- peudo-repeat seen within 1200
## 10, 2 * pump -- repeat seen within 1200
## 10, 3 * pump -- repeat seen within 1200
#autonoma = TwoDCellularAutonomataWallRecursion(
#  generations=generations,
#  machine_cls=Rule30WithQueueDepth,
#  cells_per_generation=15,
#  order_scalar=1,
#  )

autonoma = TwoDCellularAutomata(
  generations=generations,
  machine_cls=Rule30,
  wall_cls=WallLeftWhiteRightWhite
  )

eco = Canvas(autonoma)
# 43 seconds with generations = 200
eco.run_animation(generations, interval=10)
eco.save('rule_30.mp4')

# 43 seconds with generations = 200
eco.save('rule_30.pdf')
eco.save('rule_30.svg')

cmd = 'cmd.exe /C {} &'.format('rule_30.mp4')
subprocess.Popen(cmd, shell=True)

cmd = 'cmd.exe /C {} &'.format('rule_30.pdf')
subprocess.Popen(cmd, shell=True)
#
#cell = Rule30('bob')
