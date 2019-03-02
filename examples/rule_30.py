import time
import random
import subprocess
import matplotlib
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from miros import Event
from miros import signals
from miros import HsmWithQueues
from miros import return_status

Black = 0.9
Default = 0.5
White = 0.1

class Wall(HsmWithQueues):

  def __init__(self, name='wall'):
    super().__init__(name)
    self.color = None

  def color_number(self):
    return Black if self.color == 'black' else White

class Cell(Wall):

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

class Evolution():
  def __init__(self, generations, cells_per_generation, starting_cell=None):
    self.generations = generations
    self.cells_per_generation = cells_per_generation

    self.starting_cell = round(self.cells_per_generation/2.0) \
      if starting_cell is None else starting_cell
    self.generation = None

  def initial_state(self):
    Z = np.full([self.generations, self.cells_per_generation], Black, dtype=np.float32)
    self.machines = []
    for i in range(self.cells_per_generation-2):
      self.machines.append(Cell())
    left_wall = Wall()
    left_wall.start_at(fake_white)
    right_wall = Wall()
    right_wall.start_at(fake_white)
    self.machines = [left_wall] + self.machines + [right_wall]

    self.machines[0].start_at(fake_white)
    self.machines[-1].start_at(fake_white)
    for i in range(1, len(self.machines)-1):
      if i != self.starting_cell:
        self.machines[i].start_at(white)
      else:
        self.machines[i].start_at(black)

    self.generation = self.generations-1

    ## draw the walls
    Z[:, 0] = self.machines[0].color_number()
    Z[:, Z.shape[-1]-1] = self.machines[-1].color_number()

    self.Z = Z

  def next_generation(self):
    # flip our y coodinate system
    #Z = np.flipud(self.Z)
    Z = self.Z
    if self.generation == self.generations-1:
      # draw the walls
      #Z[:, 0] = self.machines[0].color_number()
      #Z[:, Z.shape[-1]-1] = self.machines[-1].color_number()

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
        
        new_machine = Cell()
        new_machine.start_at(old_machine.state_fn)
        new_machine.left = old_left_machine
        new_machine.right = old_right_machine
        new_machines.append(new_machine)

      left_wall = Wall()
      left_wall.start_at(fake_white)
      right_wall = Wall()
      right_wall.start_at(fake_white)
      new_machines = [left_wall] + new_machines + [right_wall]

      for i, machine in enumerate(new_machines):
        machine.dispatch(Event(signal=signals.Next))
        Z[self.generation, i] = machine.color_number()

      self.machines = new_machines[:]
      # flip our y coodinate system
      #Z = np.flipud(Z)
    self.Z = Z
    self.generation -= 1

  def _Generation(self):
    self.initial_state()
    yield self.Z
    while True:
      self.next_generation()
      yield self.Z

class Canvas():
  def __init__(self, evolution, title=None):
    self.fig, self.ax = plt.subplots()
    if title:
      self.ax.set_title(title)
    self.evolution = evolution
    self.generation = evolution._Generation()
    #self.ax.set_ylabel('G')
    self.ax.set_yticklabels([])
    self.ax.set_xticklabels([])
    self.ax.xaxis.set_ticks_position('none')
    self.ax.yaxis.set_ticks_position('none')
    self.fig.tight_layout()
    self.cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
      'oranges', ['#ffffff', '#ffa500', '#b27300', '#191000'])
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
    self.ax.pcolormesh(self.evolution.Z, cmap=self.cmap)
    plt.savefig(filename)

  def save_animation(self, filename):
    self.anim.save(filename) 

generations = 20
cells_per_generation = round(generations * 17/12)
generator = Evolution(generations=generations, cells_per_generation=cells_per_generation)
eco = Canvas(generator)
eco.run_animation(generations, interval=100)
eco.save_animation('rule_30.mp4')
eco.save(0, 'rule_30.pdf')
eco.save(0, 'rule_30.svg')

cmd = 'cmd.exe /C {} &'.format('rule_30.mp4')
subprocess.Popen(cmd, shell=True)

cmd = 'cmd.exe /C {} &'.format('rule_30.pdf')
subprocess.Popen(cmd, shell=True)

cell = Cell('bob')
