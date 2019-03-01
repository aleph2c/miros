import time
import random
import subprocess
import matplotlib
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Evolution():
  def __init__(self, generations, cells_per_generation):
    self.generations = generations
    self.cells_per_generation = cells_per_generation

  def _Generation(self):
    Z = np.full([self.generations, self.cells_per_generation], 0.2, dtype=np.float32)
    Z[:, 0] = 0.1
    Z[:, Z.shape[-1]-1] = 0.1
    Z = np.flipud(Z)
    self.Z = Z

    yield self.Z

    while True:
      x_size = self.Z.shape[0]-1
      y_size = self.Z.shape[-1]-1
      x_index = random.randint(0, x_size)
      y_index = random.randint(0, y_size)
      self.Z[x_index, y_index] = random.random()
      yield self.Z

class Grid():
  def __init__(self, evolution, title=None):
    self.fig, self.ax = plt.subplots()
    if title:
      self.ax.set_title(title)

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

  def save_pdf(self, generations, filename=None):
    for i in range(generations-1):
      next(self.generation)
    self.ax.pcolormesh(next(self.generation), cmap=self.cmap)
    plt.savefig(filename)

  def save_animation(self, filename):
    self.anim.save(filename) 

generator = Evolution(generations=12, cells_per_generation=16)
eco = Grid(generator)
eco.run_animation(generations=2000, interval=10)
eco.save_animation('rule_30.mp4')
eco.save_pdf(6, 'rule_30.pdf')

cmd = 'cmd.exe /C {} &'.format('rule_30.mp4')
subprocess.Popen(cmd, shell=True)

cmd = 'cmd.exe /C {} &'.format('rule_30.pdf')
subprocess.Popen(cmd, shell=True)

