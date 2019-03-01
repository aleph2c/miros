import time
import random
import subprocess
import matplotlib
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Grid():
  def __init__(self, generations, cells_per_generation):
    self.generations = generations
    self.cells_per_generation = cells_per_generation

    FFMpegWriter = animation.writers['ffmpeg']
    metadata = {'title': 'Rule 30', 'artist': 'Scott Volk'}
    self.writer = FFMpegWriter(fps=1, metadata=metadata)

    Z = np.full([generations, cells_per_generation], 0.2, dtype=np.float32)
    Z[:, 0] = 0.1
    Z[:, Z.shape[-1]-1] = 0.1
    Z = np.flipud(Z)
    self.Z = Z
    self.fig = plt.figure()

  def next_generation(self):
    x_size = self.Z.shape[0]-1
    y_size = self.Z.shape[-1]-1
    x_index = random.randint(0, x_size)
    y_index = random.randint(0, y_size)
    self.Z[x_index, y_index] = random.random()

  def graph(self, title=None):
    if title is None:
      title = 'rule 30'
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
      'rule30', ['#ffffff', '#ffa500', '#b27300', '#191000'])
    plt.pcolormesh(self.Z, cmap=cmap)

    ax = plt.gca()
    ax.set_title(title)
    self.fig.tight_layout()

  def animate(self, generations, title=None, filename=None):
    if title is None:
      title = 'rule 30'
    if filename is None:
      filename = 'rule_30.mp4'

    with self.writer.saving(self.fig, filename, 100):
      for generation in range(generations):
        self.next_generation()
        self.graph(title + " " + str(generation))
        self.writer.grab_frame()

  def save_pdf(self, title=None, filename=None):
    if filename is None:
      filename = 'rule_30.pdf'
    self.filename = filename
    plt.savefig(self.filename)

eco = Grid(generations=6, cells_per_generation=8)
eco.graph()
eco.save_pdf()
time.sleep(0.1)
cmd = 'cmd.exe /C {} &'.format(eco.filename)
subprocess.Popen(cmd, shell=True)

video_file = 'rule_30.mp4'
eco.animate(5, title='rule 30', filename=video_file)
cmd = 'cmd.exe /C {} &'.format(video_file)
subprocess.Popen(cmd, shell=True)

