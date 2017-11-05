import pytest
from miros.hsm          import HsmEventProcessor
from miros.activeobject import ActiveFabric


@pytest.fixture
def spy_chart(request):
  '''Creates a hsm event processor object and adds a spy_log attribute to it:

  The hsm event processor is named 'chart'
  The spy_log attribute is a list
  == THE TEST IS RUN ==
  The spy_log list is deleted
  The chart is deleted
  '''
  chart = HsmEventProcessor()
  spy   = []
  chart.augment(other=spy, name="spy_log")
  yield chart
  del spy
  del chart


@pytest.fixture
def fabric_fixture(request):
  '''Stops the ActiveFabric, then clears the ActiveFabric

  == THE TEST IS RUN ==
  ActiveFabric is stopped
  ActiveFabric is cleared
  '''
  yield
  # shut down the active fabric for the next test
  ActiveFabric().stop()
  ActiveFabric().clear()


def common_test_function():
  print("hello world")

