import subprocess
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from miros import Event
from miros import signals
from miros import HsmWithQueues
from miros import return_status

import math
import pathlib
from collections import deque
from collections import namedtuple

import csv
from functools import reduce
import os
import re

from scipy import fft
from functools import reduce

White   = 0
Black   = 1

def build_rule_function(number):
  if number > 2**8:
    print('not supported')
  number_as_binary_string = "{0:b}".format(number)
  number_as_binary_string = number_as_binary_string.rjust(8, '0')
  masks = {}
  masks[0] = number_as_binary_string[7] == '1'
  masks[1] = number_as_binary_string[6] == '1'
  masks[2] = number_as_binary_string[5] == '1'
  masks[3] = number_as_binary_string[4] == '1'
  masks[4] = number_as_binary_string[3] == '1'
  masks[5] = number_as_binary_string[2] == '1'
  masks[6] = number_as_binary_string[1] == '1'
  masks[7] = number_as_binary_string[0] == '1'
  def fn(left, middle, right):
    left_bit = 1 if left else 0
    middle_bit = 1 if middle else 0
    right_bit = 1 if right else 0
    number = left_bit << 2
    number += middle_bit << 1
    number += right_bit
    return masks[number]
  return fn


rule_30_fn = build_rule_function(30)
assert rule_30_fn(False, False, False) == False
assert rule_30_fn(False, False, True) == True
assert rule_30_fn(False, True, False) == True
assert rule_30_fn(False, True, True) == True
assert rule_30_fn(True, False, False) == True
assert rule_30_fn(True, False, True) == False
assert rule_30_fn(True, True, False) == False
assert rule_30_fn(True, True, True) == False

# credit agf from stackoverlow
# https://stackoverflow.com/questions/6800193/what-is-the-most-efficient-way-of-finding-all-the-factors-of-a-number-in-python 
def factors(n):
  return set(reduce(list.__add__,
    ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0 )))

period_lookup = {}
period_lookup[(10, 3)] = 51
period_lookup[(10, 4)] = 14
period_lookup[(10, 5)] = 16
period_lookup[(10, 6)] = 35
period_lookup[(10, 7)] = 30
period_lookup[(10, 8)] = 65
period_lookup[(10, 9)] = 24
period_lookup[(10, 10)] = 52
period_lookup[(10, 11)] = 110
period_lookup[(10, 12)] = 30
period_lookup[(10, 13)] = 32
period_lookup[(11, 4)] = 24
period_lookup[(11, 5)] = 57
period_lookup[(11, 6)] = 28
period_lookup[(11, 7)] = 30
period_lookup[(11, 8)] = 32
period_lookup[(11, 9)] = 27
period_lookup[(11, 10)] = 36
period_lookup[(11, 11)] = 42
period_lookup[(11, 12)] = 80
period_lookup[(11, 13)] = 42
period_lookup[(11, 14)] = 84
period_lookup[(11, 15)] = 46
period_lookup[(11, 16)] = 48
period_lookup[(11, 17)] = 50
period_lookup[(11, 18)] = 52
period_lookup[(12, 4)] = 24
period_lookup[(12, 5)] = 26
period_lookup[(12, 6)] = 39
period_lookup[(12, 7)] = 58
period_lookup[(12, 8)] = 19
period_lookup[(12, 9)] = 14
period_lookup[(12, 10)] = 46
period_lookup[(12, 11)] = 36
period_lookup[(12, 12)] = 53
period_lookup[(12, 13)] = 32
period_lookup[(12, 14)] = 42
period_lookup[(13, 10)] = 139
period_lookup[(13, 15)] = 157
period_lookup[(13, 21)] = 197
period_lookup[(14, 3)] = 43
period_lookup[(14, 4)] = 13
period_lookup[(14, 9)] = 176
period_lookup[(14, 10)] = 271

def automata_period(num1, num2):
  num1 = int(num1)
  num2 = int(num2)
  product = num1 * num2
  divisor = max(factors(num1).intersection(factors(num2)))
  if divisor == 0:
    raise("0 illegal in period_lookup")
  return int(product/divisor)

def periodicity(*args):
  list_of_variables = args
  unique_pattern_durations = [period_lookup[(pattern.width, pattern.depth)] for pattern in list_of_variables]
  return reduce(automata_period, unique_pattern_durations)

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

class Rule(Wall):
  def __init__(self, name='cell'):
    super().__init__(name)
    self.left = None
    self.right = None
    self.color = None

  def result(self, left, middle, right):
    inputs_as_bool = [True if cell.color == 'black' else False for cell in [left, middle, right]]
    output_as_bool = self.rule_fn(*inputs_as_bool)
    output_as_color = 'black' if output_as_bool else 'white'
    return output_as_color

class Rule30(Rule):

  def __init__(self, name='cell'):
    super().__init__(name)
    self.left = None
    self.right = None
    self.color = None
    self.rule_fn = build_rule_function(30)

def white(cell, e):
  status = return_status.UNHANDLED

  if(e.signal == signals.ENTRY_SIGNAL):
    cell.color = 'white'
    status = return_status.HANDLED
  elif(e.signal == signals.Next):
    next_color = cell.result(cell.left, cell, cell.right)
    if next_color == 'black':
      status = cell.trans(black)
    else:
      status = return_status.HANDLED

    #if((cell.right.color == 'black' and
    #    cell.left.color == 'white') or 
    #   (cell.right.color == 'white' and
    #    cell.left.color == 'black')):
    #  status = cell.trans(black)
    #else:
    #  status = return_status.HANDLED
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
    next_color = cell.result(cell.left, cell, cell.right)
    if next_color == 'white':
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

    n_cache = NCache()
    degrees = n_cache.get_angle(cells_per_generation)
    print("degrees {}".format(degrees))

    qd = 1 + math.tan(math.radians(degrees))
    qd *= 0.5*cells_per_generation
    qd = math.floor(qd)

    qd =  0.5 * math.tan(math.radians(degrees))
    qd += 1.0 / math.sqrt(2)
    qd *= cells_per_generation
    qd = math.floor(qd)
    #print(qd)
    #qd = 1
    return qd

class OneDCellularAutomata():
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
       (OneDCellularAutonomata): an automata object

    **Example(s)**:
      
    .. code-block:: python
     
      # build an automata using rule 30 with white walls
      # it should be 50 cells across
      # and it should run for 1000 generations
      ma = OneDCellularAutomata(
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
    Z = np.full([self.generations, self.cells_per_generation], Black, dtype=np.bool)

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

class OneDCellularAutonomataWallRecursion(OneDCellularAutomata):

  def __init__(self, 
      generations, 
      cells_per_generation=None, 
      initial_condition_index=None,
      machine_cls=None,
      wall_cls=None,
      queue_depth=None):
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

    **Returns**:
       (type): 

    **Example(s)**:

    '''
    super().__init__(
      generations,
      cells_per_generation,
      initial_condition_index,
      machine_cls,
      wall_cls)

    half_point = round(self.cells_per_generation/2.0)
    self.core_machine_index = half_point

    if queue_depth is None:
      queue_depth = 1
    else:
      queue_depth = queue_depth

    self.core_colors = deque(maxlen=queue_depth)
    self.core_code = []
    self.middle_numbers = []
    self.for_pattern_search = [[] for i in range(self.cells_per_generation)]

    for i in range(4):
      self.core_colors.append('white')
      self.core_code.append(0)
    self.wall_cls = WallLeftWhiteRightWhite

  def initial_state(self):
    super().initial_state()
    self.update_core_code()
    self.core_code = [1 if i == 'black' else 0 for i in self.core_colors]
    self.set_wall_class()

  def next_generation(self):
    super().next_generation()
    self.update_core_code()
    row_number = self.generation+1
    for col_number in range(self.Z.shape[1]):
      cell_color = self.Z[row_number, col_number]
      self.for_pattern_search[col_number].append(1.0 if abs(cell_color-Black)<0.01 else 0.0)
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

    Given an ma, which has a ``make_generation_coroutine`` coroutine generator, an
    animation can be build by calling this coroutine for as many generations are
    required.

    **Note**:
       This ``automata`` object needs to provide a ``make_generation_coroutine`` method which
       returns a coroutine which can be called with ``next``.

    **Args**:
       | ``automata`` (OneDCellularAutomata): 
       | ``title=None`` (string): An optional title

    **Returns**:
       (Canvas): this object

    **Example(s)**:
      
    .. code-block:: python
       
       eco1 = Canvas(ma)
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

       eco1 = Canvas(ma)
       eco1.run_animation(50, 10)
       eco1.save('rule_30.mp4)
       eco1.save('rule_30.pdf)

       eco2 = Canvas(ma)
       eco1.save('rule_30.pdf', generations=40)

    '''
  def save(self, filename=None, generations=0, dpi=100):

    if pathlib.Path(filename).suffix == '.mp4':
      self.anim.save(filename) 
    else:
      if self.automata.generation > 0:
        for i in range(self.automata.generations):
          next(self.generation)
        self.ax.pcolormesh(self.automata.Z, cmap=self.cmap)
      #for item in [self.fig, self.ax]:
      #  item.patch.set_visible(False)
      self.ax.axis('off')
      plt.savefig(filename, dpi=dpi) 

  def close(self):
    plt.close(self.fig)

class ODCAVariable(OneDCellularAutonomataWallRecursion):
  def __init__(self, width, depth, generations):
    self.width = width
    self.depth = depth
    super().__init__(
      generations=generations,
      machine_cls=Rule30WithQueueDepth,
      cells_per_generation=width,
      queue_depth=depth,
      )

class ODCAXEquation:
  def __init__(self, odcavar, generations, width_alg='max'):
    self.automata = [odcavar]
    self.width_alg = width_alg
    self.width = odcavar.width
    self.max_width = odcavar.width
    self.min_width = odcavar.width
    self.generations = generations

  def load(self, odcarvar):
    self.automata.append(odcarvar)
    # the max_width is the maximum max_width
    self.max_width = max([automata.cells_per_generation for automata in self.automata])
    self.min_width = min([automata.cells_per_generation for automata in self.automata])
    self.width = self.max_width if self.width_alg == 'max' else self.min_width

  def __xor__(self, vector):
    self.load(vector)
    return self

  def pad_width_to_max(self, vector):
    '''Wrap pad a row in the provided vector

    **Note**:
       Do this not that recommendation

    **Args**:
       | ``vector`` (1d ndarray): The vector row you want to pad

    **Returns**:
       (1d ndarray): The vector padded so that its width is self.width.  The
       begging part of the vector is placed on the end until the row width of
       the vector is equal to the self.width of this obj
    '''
    padding_needed = self.max_width - vector.size
    if padding_needed > 0:
      # keep all the rows and get rid of the first columns added by the pad command
      result = np.lib.pad(vector, (0, padding_needed), mode='wrap')
    else:
      result = vector
    return result


  def trim_width_to_min(self, vector):
    size_needed = vector.size - (vector.size - self.min_width)
    result = vector[0:size_needed]
    return result

  def initial_state(self):
    '''initialize the 2d cellular automata'''

    if self.width_alg == 'max':
      self.for_pattern_search = [[] for i in range(self.max_width)]
      self.Z = np.full([self.generations, self.max_width], Black, dtype=np.bool)
    else:
      self.for_pattern_search = [[] for i in range(self.min_width)]
      self.Z = np.full([self.generations, self.min_width], Black, dtype=np.bool)

  def make_generation_coroutine(self):

    def xor_row(row1, row2):
      if self.width_alg == 'max':
        padded_row1 = self.pad_width_to_max(row1)
        padded_row2 = self.pad_width_to_max(row2)
      else:
        padded_row1 = self.trim_width_to_min(row1)
        padded_row2 = self.trim_width_to_min(row2)
      return np.bitwise_xor(padded_row1, padded_row2)

    # to multiply on variable's current generation by another 
    # self.for_pattern_search = [[] for i in range(self.automata[0].cells_per_generation)]
    self.initial_state()
    [obj.initial_state() for obj in self.automata]
    # pull the last row vector out of each automata and make a list of vectors
    # multiply each of these vectors together for the row_result
    g = self.automata[0].generation
    self.row_result = reduce(xor_row, [obj.Z[g, :] for obj in self.automata])
    self.Z[0, :] = self.row_result
    self.generation = self.automata[0].generation
    yield self.Z
    while True:
      [obj.next_generation() for obj in self.automata]
      # pull the last row vector out of each automata and make a list of vectors
      # multiply each of these vectors together for the row_result
      g = self.automata[0].generation
      self.row_result = reduce(xor_row, [obj.Z[g+1, :] for obj in self.automata])
      self.Z[g+1, :] = self.row_result
      self.generation = self.automata[0].generation
      row_number = self.generation + 1
      for col_number in range(self.Z.shape[1]):
        cell_color = self.Z[row_number, col_number]
        self.for_pattern_search[col_number].append(1.0 if abs(cell_color - Black)<0.01 else 0.0)
      yield self.Z

# Goal, for a given width, find the optimal queue depth:
# 
# Need a new class that can detect it's own periodicity using two masks.  We
# have done both before, so you will have to dig into your old code and find:
# * mask1 for finding the n-phenomenon across the bulk
# * mask2 (new) for finding the n-phenomenon at the middle point
# * size of the queue length

# Goal, for a given width and queue depth, find the recursive wall object's
# periodicity
#
# Create another class that can make itself based on either provided parameters
# or by building the previous object to find it's queue length.  The resulting
# object will be used to build recursive wall objects.
# 
# Create another class that can find the periodicity of the previous object, or
# find if it has petered out by masking for the n-phenomenon
#

# Build a table, which will have a maximum size and will grow by one when it has
# run out of periodicity.  When it needs to drop a number, it will drop the
# number that is the smallest non-prime

# The table will be used to figure out which combinations of machines should be
# xor'd together.  Look at set hacking to get an idea about how this will be
# done, the new pioneered number will be combined with every other item in the
# list, with a number of picks == round(len(table)/2)

# question, does the n-phenomenon express itself exactly the same in reverse?
# rule 135

# Since the entropy generator will need access to computation, turn it into a
# daemon and have it send entropy back to the main process

width       = 11
queue_depth = 20
generations = 380

# 16 * 28 * 26 = 11648
# 16 * 39 = 624
# 35 * 39 = 1366
# 10, 4: 14
# 10, 5: 16
# 10, 6: 35
# 11, 4: 24
# 11, 5: 57
# 11, 6: 28
# 12, 5: 26
# 13, 4: 9
# 13, 5: 12
# 13, 6: 46
# (10, 5)^(10, 6) = 560
# (11, 5)^(11, 6) = 1596
# (10, 5)^(11, 5) = 912
# (10, 6)^(11, 6) = 980
# (10, 5)^(13, 5) = 192
# (10, 5)^(13, 5) = 48
# (10, 5)^(13, 5)^(11, 5) = 16*12*57 = 10944 (too big to see), but 912
# 10944/912 -> 12
# (10, 4)^(11, 4)^(13^4) = 14*24*9 = 3024
# 2*7 2*2*2*3 3*3
# changing the order didn't increase the periodicity
# 456
# (10, 5)^(13, 5)^(11, 5)^(12, 5) = 456
# 16, 12, 57, 26 ?-> 456

a = ODCAVariable(width=10, depth=3, generations=generations)
b = ODCAVariable(width=10, depth=5, generations=generations)
#c = ODCAVariable(width=10, depth=12, generations=generations)
#d = ODCAVariable(width=12, depth=5, generations=generations)

# commutative (order) indifferent
# associative (grouping) indifferent
equation = ODCAXEquation(a, generations=generations, width_alg='min')
equation ^= b
#equation ^= c

print(periodicity(a, b))
#print(periodicity(a, b, c, d))
#exit(0)

#equation ^= d

ma = OneDCellularAutonomataWallRecursion(
  generations=generations,
  machine_cls=Rule30WithQueueDepth,
  cells_per_generation=width,
  queue_depth=queue_depth,
  )

filename = "equation_rec_walls_{}_queue_{}_gen_{}".format(width, queue_depth, generations)
eco = Canvas(equation)
eco.run_animation(generations, interval=100)
movie_filename = '{}.mp4'.format(filename)
eco.save(movie_filename)
png = '{}.png'.format(filename)
eco.save(png)

eco.save('{}.pdf'.format(filename))
eco.close()
cmd = 'cmd.exe /C {} &'.format('{}.pdf'.format(filename))
subprocess.Popen(cmd, shell=True)

def autocorrelate(x):
  '''

  compute the autocorrelation of vector x

  **Args**:
     | ``x`` (list): a list containing where each element is a 1.0 or 0.0

  **Returns**:
     (list): the autocorrelation for the list
  '''
  result = np.correlate(x, x, mode='full')
  # don't include the correletion with itself
  result[result.size//2] = 0
  return result[result.size//2:]

# a specific column can repeat, while the other columns change
# for this reason we need to multiply the spectrums together so
# as to find where the real pattern repetitions take place
max_c_indexs = []
column_correlations = []
width = equation.width
for i in range(width):
  column_correlations.append(autocorrelate(equation.for_pattern_search[i]))
  max_index = np.argmax(column_correlations[-1])
  max_c_indexs.append(max_index)

collective_correlations = column_correlations[0]
for correlation in column_correlations[1:]:
  collective_correlations = np.multiply(collective_correlations, correlation)

fig = plt.figure()
autocorrelation_filename = "autocorrection.pdf"
#plt.plot(pattern_index, collective_autocorrelation_fft_product)
#plt.plot(pattern_index, cc)
plt.plot([i for i in range(len(collective_correlations))], collective_correlations)
plt.savefig(autocorrelation_filename, dpi=300)

of_interest = []
for i in range(10):
  max_index = np.argmax(collective_correlations)
  of_interest.append(max_index)
  collective_correlations[max_index] = 0

print(of_interest)

cmd = 'cmd.exe /C {} &'.format(movie_filename)
subprocess.Popen(cmd, shell=True)

cmd = 'cmd.exe /C {} &'.format(autocorrelation_filename)
subprocess.Popen(cmd, shell=True)
