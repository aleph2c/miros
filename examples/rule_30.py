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

White   = 0.1
Default = 0.5
Black   = 0.9

class NCache:

  Bottom_Width = 4
  Spec = namedtuple('Spec', ['width', 'angle_degrees'])

  def __init__(self):
    '''Used to store and describe the characteristics of rule30 within walls

    **Returns**:
       (Ncache): This object

    **Example(s)**:

      nc = NCache()
      csv_filename, movie_filename = nc.build_cache_csv(WallLeftBlackRightBlack,
          start_at=4, upto=200)
      nc.plot_csv(csv_filename)

    '''
    def by_angle(spec):
      return spec.angle_degrees

    def by_width(spec):
      return spec.width

    self.by_angle = by_angle
    self.by_width = by_width
    self._lookup = {}
    self._lookup[4] = 73.7
    self._lookup[5] = 55.3
    self._lookup[6] = 65.3
    self._lookup[7] = 28.2
    self._lookup[8] = 35.2
    self._lookup[9] = 35.5
    self._lookup[10] = 35.7
    self._lookup[11] = 44.4
    self._lookup[12] = 36.0
    self._lookup[13] = 27.7
    self._lookup[14] = 30.2
    self._lookup[15] = 39.2
    self._lookup[16] = 34.0
    self._lookup[17] = 35.3
    self._lookup[18] = 27.7
    self._lookup[19] = 27.5
    self._lookup[20] = 21.9
    self._lookup[21] = 23.1
    self._lookup[22] = 24.0
    self._lookup[23] = 27.7
    self._lookup[24] = 27.5
    self._lookup[25] = 26.9
    self._lookup[26] = 24.7
    self._lookup[27] = 27.0
    self._lookup[28] = 28.7
    self._lookup[29] = 26.4
    self._lookup[30] = 21.9
    self._lookup[31] = 28.5
    self._lookup[32] = 37.7
    self._lookup[33] = 37.7
    self._lookup[34] = 26.9
    self._lookup[35] = 21.9
    self._lookup[36] = 23.6
    self._lookup[37] = 25.7
    self._lookup[38] = 25.4
    self._lookup[39] = 25.3
    self._lookup[40] = 26.6
    self._lookup[41] = 23.6
    self._lookup[42] = 28.5
    self._lookup[43] = 25.1
    self._lookup[44] = 21.0
    self._lookup[45] = 22.8
    self._lookup[46] = 23.6
    self._lookup[47] = 24.4
    self._lookup[48] = 23.6
    self._lookup[49] = 27.2
    self._lookup[50] = 19.6
    self._lookup[51] = 26.4
    self._lookup[52] = 27.4
    self._lookup[53] = 26.2
    self._lookup[54] = 29.9
    self._lookup[55] = 23.7
    self._lookup[56] = 23.6
    self._lookup[57] = 24.4
    self._lookup[58] = 26.6
    self._lookup[59] = 25.8
    self._lookup[60] = 25.2
    self._lookup[61] = 24.2
    self._lookup[62] = 26.9
    self._lookup[63] = 25.8
    self._lookup[64] = 25.1
    self._lookup[65] = 26.0
    self._lookup[66] = 20.6
    self._lookup[67] = 25.3
    self._lookup[68] = 23.3
    self._lookup[69] = 24.7
    self._lookup[70] = 24.4
    self._lookup[71] = 24.5
    self._lookup[72] = 26.7
    self._lookup[73] = 25.0
    self._lookup[74] = 20.2
    self._lookup[75] = 22.2
    self._lookup[76] = 23.9
    self._lookup[77] = 22.4
    self._lookup[78] = 27.7
    self._lookup[79] = 24.2
    self._lookup[80] = 22.9
    self._lookup[81] = 23.6
    self._lookup[82] = 23.0
    self._lookup[83] = 19.1
    self._lookup[84] = 19.9
    self._lookup[85] = 21.0
    self._lookup[86] = 20.0
    self._lookup[87] = 26.2
    self._lookup[88] = 27.7
    self._lookup[89] = 23.8
    self._lookup[90] = 23.1
    self._lookup[91] = 25.2
    self._lookup[92] = 22.5
    self._lookup[93] = 22.8
    self._lookup[94] = 26.4
    self._lookup[95] = 20.7
    self._lookup[96] = 20.8
    self._lookup[97] = 20.1
    self._lookup[98] = 22.6
    self._lookup[99] = 21.3
    self._lookup[100] = 23.4
    self._lookup[100] = 23.4
    self._lookup[101] = 21.5
    self._lookup[102] = 21.7
    self._lookup[103] = 23.1
    self._lookup[104] = 23.0
    self._lookup[105] = 22.4
    self._lookup[106] = 24.7
    self._lookup[107] = 21.4
    self._lookup[108] = 22.1
    self._lookup[109] = 21.7
    self._lookup[109] = 21.7
    self._lookup[110] = 25.3
    self._lookup[111] = 24.0
    self._lookup[112] = 25.6
    self._lookup[113] = 23.6
    self._lookup[114] = 24.8
    self._lookup[115] = 23.3
    self._lookup[116] = 23.6
    self._lookup[117] = 24.9
    self._lookup[118] = 22.6
    self._lookup[119] = 21.4
    self._lookup[120] = 21.1
    self._lookup[121] = 21.5
    self._lookup[122] = 25.2
    self._lookup[123] = 24.7
    self._lookup[124] = 23.0
    self._lookup[125] = 23.1
    self._lookup[126] = 24.2
    self._lookup[127] = 20.4
    self._lookup[128] = 21.3
    self._lookup[129] = 22.1
    self._lookup[130] = 21.6
    self._lookup[131] = 22.8
    self._lookup[132] = 23.0
    self._lookup[133] = 25.0
    self._lookup[134] = 23.9
    self._lookup[135] = 22.6
    self._lookup[136] = 23.4
    self._lookup[137] = 20.7
    self._lookup[138] = 21.7
    self._lookup[139] = 22.2
    self._lookup[140] = 22.0
    self._lookup[141] = 23.1
    self._lookup[142] = 23.0
    self._lookup[143] = 21.8
    self._lookup[144] = 22.2
    self._lookup[145] = 22.1
    self._lookup[146] = 24.4
    self._lookup[147] = 22.5

    
  def get_angle(self, cells_per_generation):
    '''Get the angle of the n-phenomenon for a rule 30 automata held between
    white walls.


    **Note**:
       The angle only applies to rule 30 between white walls

    **Args**:
       | ``cells_per_generation`` (int): how wide is your graphing paper

    **Returns**:
       (float): The observed angle of n-phenomenon for this width of graphing
       paper

    **Example(s)**:


    '''
    
    result = None


    if cells_per_generation in self._lookup:
      result = self._lookup[cells_per_generation]
    elif cells_per_generation < NCache.Bottom_Width:
      result = None
    else:
      def do_sum(x1, x2):
        return x1+x2
      result = reduce(do_sum, self.widest()[15])/15
    return result

  def slowest_n_phenom(self):
    fastest = sorted(
      [NCache.Spec(k,v) for (k,v) in self._lookup.items()],
      key=self.by_angle
    )
    return fastest

  def slowest_n_phenom(self):
    slowest = sorted(
      [NCache.Spec(k,v) for (k,v) in self._lookup.items()],
      key=self.by_angle,
      reverse=True
    )
    return slowest

  def widest(self):
    w = sorted(
      [NCache.Spec(k,v) for (k,v) in self._lookup.items()],
      key=self.by_width,
      reverse=True
    )
    return w

  def thinnest(self):
    w = sorted(
      [NCache.Spec(k,v) for (k,v) in self._lookup.items()],
      key=self.by_width,
    )
    return w

  def build_cache_csv(self, wall_cls, start_at, upto):

    m = re.search(r"(Wall.+)'", str(wall_cls))
    if m: 
      file_start = "rule{}".format(
        re.sub(r'([A-Z]+)', r'_\1', m.group(1)).lower())
    basename = '{}_{}_to_{}'.format(file_start, start_at, upto)
    csv_filename = '{}.csv'.format(basename)
    png_filename = '{}_'.format(basename)

    with open(csv_filename, 'w') as fh:
      writer = csv.writer(fh)
      writer.writerows([['width', 'angle_in_degrees']])

    generations = 50
    width = start_at
    while width < upto:
      filename = "{}{}".format(png_filename, width)
      automata = OneDCellularAutomataWithAngleDiscovery(
        generations=generations,
        machine_cls=Rule30,
        wall_cls=wall_cls,
        cells_per_generation=width
        )
      eco = Canvas(automata)
      eco.save('{}.png'.format(filename), dpi=300)
      angle_degrees = automata.n_angle
      #cmd = 'cmd.exe /C {} &'.format('{}.png'.format(filename))
      #subprocess.Popen(cmd, shell=True)

      if wall_cls == WallLeftWhiteRightWhite or wall_cls == WallLeftBlackRightWhite \
          and (automata.cells_per_generation - len(automata.n_mask) >= 2):
        generations += 50
      elif wall_cls == WallLeftWhiteRightBlack or wall_cls == WallLeftBlackRightBlack \
          and (automata.cells_per_generation - len(automata.n_mask) >= 4):
        generations += 50
      else:
        with open(csv_filename, 'a') as fh:
          writer = csv.writer(fh)
          writer.writerows([[str(width), "{0:0.1f}".format(angle_degrees)]])
        width += 1
        eco.close()
    movie_filename = "{}.mp4".format(png_filename)
    os.system("ffmpeg -f image2 -r 1 -i ./{}\%01d.png -vcodec mpeg4 -y ./{}".format(png_filename, movie_filename))
    return csv_filename, movie_filename

  def plot_csv(self, csv_filename):
    x = []
    y = []
    with open(csv_filename, 'r') as csvfile:
      plots = csv.reader(csvfile, delimiter=',')
      for row in plots:
        try:
          x.append(int(row[0]))
          y.append(float(row[1]))
        except:
          pass
    plt.plot(x, y, label='cells versus angle')
    plt.xlabel('cells per generation')
    plt.ylabel('angle of n phenomenon [degrees]')
    plt.savefig('cells_per_generation_vrs_angle_of_n_phenomenon.svg')
    plt.savefig('cells_per_generation_vrs_angle_of_n_phenomenon.pdf')
    plt.close()

    
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

class OneDCellularAutomataWithAngleDiscovery(OneDCellularAutomata):

    def __init__(self, 
        generations, 
        cells_per_generation=None, 
        initial_condition_index=None,
        machine_cls=None,
        wall_cls=None):

      super().__init__(
        generations,
        cells_per_generation,
        initial_condition_index,
        machine_cls,
        wall_cls)

      self.black_mask = np.array([Black], dtype=np.float32)
      self.white_mask = np.array([White], dtype=np.float32)

      if self.wall_cls == WallLeftWhiteRightBlack or \
        self.wall_cls == WallLeftWhiteRightWhite:
        self.n_mask = np.concatenate(
           (self.white_mask, self.black_mask), axis=0)
      else:
        self.n_mask = np.concatenate(
           (self.black_mask, self.white_mask), axis=0)
      self.n_angle = 90

    def build_next_mask(self):

      if self.wall_cls == WallLeftBlackRightBlack or \
        self.wall_cls == WallLeftBlackRightWhite:

        if abs(self.n_mask[-1] - White) < 0.001:
          self.n_mask = np.concatenate(
            (self.n_mask, self.black_mask), axis=0)
        else:
          self.n_mask = np.concatenate(
            (self.n_mask, self.white_mask), axis=0)
      else:
        if abs(self.n_mask[-1] - White) < 0.001:
          self.n_mask = np.concatenate(
            (self.n_mask, self.black_mask), axis=0)
        else:
          self.n_mask = np.concatenate(
            (self.n_mask, self.white_mask), axis=0)

    def update_angle(self):

      previous_generation = self.generation+1
      row_to_check = self.Z[previous_generation]
      sub_row_to_check = row_to_check[0:len(self.n_mask)]

      if np.array_equal(self.n_mask, sub_row_to_check):

        self.nothing_at_row = self.generations-previous_generation + 1
        adjacent = self.nothing_at_row
        adjacent -= (self.cells_per_generation / math.sqrt(2.0))
        opposite = self.cells_per_generation
        self.n_angle = math.degrees(math.atan(opposite/adjacent))

        self.build_next_mask()

    def next_generation(self):
      super().next_generation()
      self.update_angle()

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
      middle_color = self.Z[row_number, col_number]
      self.for_pattern_search[col_number].append(1.0 if abs(middle_color-Black)<0.01 else 0.0)
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


class OneDCellularAutonomataWallRecursionUsingAngle(OneDCellularAutomata):

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
    print(queue_depth)

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
      middle_color = self.Z[row_number, col_number]
      self.for_pattern_search[col_number].append(1.0 if abs(middle_color-Black)<0.01 else 0.0)
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
      plt.savefig(filename, dpi=dpi) 

  def close(self):
    plt.close(self.fig)

## Eye scans
## 12, 2 * pump -- no repeat after 1200
## 11, 2 * pump -- no repeat after 1200
## 10, 1 * pump -- peudo-repeat seen within 1200
## 10, 2 * pump -- repeat seen within 1200
## 10, 3 * pump -- repeat seen within 1200
width = 17
generations = 5000
# 10, queue_depth = 2, 37
# 10, queue_depth = 3, 51
# 10, queue_depth = 4, 14
# 10, queue_depth = 5, 16
# 10, queue_depth = 6, 35
# 10, queue_depth = 7, 30  # lots of veritical lines
# 10, queue_depth = 8, 65  #
# 10, queue_depth = 9, 24  #
# 10, queue_depth = 10, 52 (degrees 35.7)
# 10, queue_depth = 11, 110
# 10, queue_depth = 12, 30
# 10, queue_depth = 13, 32
# 11, queue_depth = 2, 53
# 11, queue_depth = 3, 5
# 11, queue_depth = 4, 24
# 11, queue_depth = 5, 57
# 11, queue_depth = 6, 28
# 11, queue_depth = 7, 30
# 11, queue_depth = 8, 32
# 11, queue_depth = 9, 27
# 11, queue_depth = 10, 36
# 11, queue_depth = 11, 42
# 11, queue_depth = 12, 80
# 11, queue_depth = 13, 42 (degrees 44.4)
# 11, queue_depth = 14, 84
# 11, queue_depth = 15, 46
# 11, queue_depth = 16, 48
# 11, queue_depth = 17, 50
# 11, queue_depth = 18, 52
# 12, queue_depth = 2, 16
# 12, queue_depth = 3, 35
# 12, queue_depth = 4, 24
# 12, queue_depth = 5, 26
# 12, queue_depth = 6, 39
# 12, queue_depth = 7, 58
# 12, queue_depth = 8, 19
# 12, queue_depth = 9, 14
# 12, queue_depth = 10, 46
# 12, queue_depth = 11, 36
# 12, queue_depth = 12, 53 (degrees 36.0)
# 12, queue_depth = 13, 32
# 12, queue_depth = 14, 42  # need 600 to find it
# 12, queue_depth = 15, 276
# 12, queue_depth = 16, 46
# 12, queue_depth = 17, 13
# 12, queue_depth = 18, 25
# 13, queue_depth = 2, 16
# 13, queue_depth = 3, 5 
# 13, queue_depth = 4, 9 
# 13, queue_depth = 5, 12
# 13, queue_depth = 6, 46
# 13, queue_depth = 7, 34
# 13, queue_depth = 8, 15
# 13, queue_depth = 9, 65
# 13, queue_depth = 10, 139
# 13, queue_depth = 11, 24
# 13, queue_depth = 12, 44 (degrees 27.7)
# 13, queue_depth = 13, 121
# 13, queue_depth = 14, 35
# 13, queue_depth = 15, 157
# 13, queue_depth = 16, 318
# 13, queue_depth = 17, 465
# 13, queue_depth = 18, 278
# 13, queue_depth = 19, 76
# 13, queue_depth = 20, 225
# 13, queue_depth = 21, 197
# 13, queue_depth = 22, 384
# 13, queue_depth = 23, 30
# 13, queue_depth = 24, 162
# 14, queue_depth = 2, 42
# 14, queue_depth = 3, 43
# 14, queue_depth = 4, 13
# 14, queue_depth = 5, 20
# 14, queue_depth = 6, 26
# 14, queue_depth = 7, 9
# 14, queue_depth = 8, 32
# 14, queue_depth = 9, 176
# 14, queue_depth = 10, 271
# 14, queue_depth = 11, 279
# 14, queue_depth = 12, 20
# 14, queue_depth = 13, 236 (degrees 30.2)
# 14, queue_depth = 14, 395
# 14, queue_depth = 15, 66
# 14, queue_depth = 16, 208
# 14, queue_depth = 17, 13
# 14, queue_depth = 18, 338
# 14, queue_depth = 19, 195
# 14, queue_depth = 20, 228
# 14, queue_depth = 21, 98
# 14, queue_depth = 22, 210
# 14, queue_depth = 23, 255
# 14, queue_depth = 24, 1450
# 14, queue_depth = 25, 32
# 14, queue_depth = 26, 1223
# 14, queue_depth = 27, 287
# 14, queue_depth = 28, 1012
# 14, queue_depth = 29, 610
# 15, queue_depth = 4, 44
# 15, queue_depth = 5, 160
# 15, queue_depth = 6, 134
# 15, queue_depth = 7, 60
# 15, queue_depth = 8, 58
# 15, queue_depth = 9, 48
# 15, queue_depth = 10, 52
# 15, queue_depth = 11, 200
# 15, queue_depth = 12, 160
# 15, queue_depth = 13, 74
# 15, queue_depth = 14, 429
# 15, queue_depth = 15, 541
# 15, queue_depth = 16, 1022 (39.2)
# 15, queue_depth = 17, 73
# 15, queue_depth = 18, 17
# 15, queue_depth = 19, 271
# 15, queue_depth = 20, 232
# 15, queue_depth = 21, 534
# 15, queue_depth = 22, 564
# 15, queue_depth = 23, 1210
# 15, queue_depth = 24, 258
# 15, queue_depth = 25, 630
# 16, queue_depth = 2, 111
# 16, queue_depth = 3, 18
# 16, queue_depth = 4, 42
# 16, queue_depth = 5, 123
# 16, queue_depth = 6, 74
# 16, queue_depth = 7, 35
# 16, queue_depth = 8, 288
# 16, queue_depth = 9, 310
# 16, queue_depth = 10, 42
# 16, queue_depth = 11, 582
# 16, queue_depth = 12, 46
# 16, queue_depth = 13, 40
# 16, queue_depth = 14, 86
# 16, queue_depth = 15, 252
# 16, queue_depth = 16, 378 (34.0 degrees)
# 16, queue_depth = 17, 180
# 16, queue_depth = 18, 900
# 16, queue_depth = 19, 288
# 16, queue_depth = 20, 541
# 16, queue_depth = 21, 1746
# 16, queue_depth = 22, 1017
# 16, queue_depth = 23, 117
# 16, queue_depth = 24, 1162
# 16, queue_depth = 25, 551
# 16, queue_depth = 26, 1182
# 17, queue_depth = 5, 36
# 17, queue_depth = 6, 47
# 17, queue_depth = 7, 270
# 17, queue_depth = 8, 164
# 17, queue_depth = 9, 92
# 17, queue_depth = 10, 42
# 17, queue_depth = 11, 179
# 17, queue_depth = 12, 433
# 17, queue_depth = 13, 448
# 17, queue_depth = 14, 238
# 17, queue_depth = 15, 120
# 17, queue_depth = 16, 60
# 17, queue_depth = 17, 1054
# 17, queue_depth = 18, 441
# 17, queue_depth = 19, 1149
# 17, queue_depth = 20, 390
# 17, queue_depth = 21, 1582
# 17, queue_depth = 22, 600
# 17, queue_depth = 23, 600

ma = OneDCellularAutonomataWallRecursion(
  generations=generations,
  machine_cls=Rule30WithQueueDepth,
  cells_per_generation=width,
  queue_depth=23,
  )
#ma = OneDCellularAutonomataWallRecursionUsingAngle(
#  generations=generations,
#  machine_cls=Rule30WithQueueDepth,
#  cells_per_generation=width,
#  )
# no pattern found for 12/2
# 15: 32768, 1022

#nc = NCache()
#csv_filename, movie_filename = nc.build_cache_csv(WallLeftBlackRightBlack,
#    start_at=4, upto=200)
#nc.plot_csv(csv_filename)
filename = "rule_30_white_walls_{}_generations_width_{}".format(generations, width)
#ma = OneDCellularAutomataWithAngleDiscovery(
#  generations=generations,
#  machine_cls=Rule30,
#  wall_cls=WallLeftWhiteRightWhite,
#  cells_per_generation=width
#  )
eco = Canvas(ma)
# 43 seconds with generations = 200
eco.run_animation(generations, interval=100)
movie_filename = '{}.mp4'.format(filename)
eco.save(movie_filename)

eco.save('{}.pdf'.format(filename))
eco.close()
cmd = 'cmd.exe /C {} &'.format('{}.pdf'.format(filename))
subprocess.Popen(cmd, shell=True)

#plt.acorr(ma.middle_numbers, usevlines=True, normed=True, maxlags=None, lw=2)
def autocorrelate(x):
  result = np.correlate(x, x, mode='full')
  # don't include the corriletion with itself
  result[result.size//2] = 0
  return result[result.size//2:]

# a specific column can repeat, while the other columns change
# for this reason we need to multiply the spectrums together so
# as to find where the real pattern repetitions take place
max_c_indexs = []
column_correlations = []
for i in range(width):
  column_correlations.append(autocorrelate(ma.for_pattern_search[i]))
  max_index = np.argmax(column_correlations[-1])
  max_c_indexs.append(max_index)

collective_correlations = column_correlations[0]
for correlation in column_correlations[1:]:
  collective_correlations = np.multiply(collective_correlations, correlation)


#max_index = np.argmax(collective_correlations)
#max_value = collective_correlations[max_index]
#collective_correlations = np.clip(collective_correlations, 1, max_value)
#collective_correlations = np.log(collective_correlations)

# the answer is the max_index (it holds the highest energy)

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
#print(width)
#print(ma.n_angle)
#
#cell = Rule30('bob')
