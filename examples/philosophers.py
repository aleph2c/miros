import time
import random
from miros import Event
from miros import spy_on
from miros import signals
from functools import partial
from miros import ActiveObject
from miros import return_status

NUMBER_OF_PHILOSOPHERS = 5

class Fork():
  Free = 0
  Used = 1

def right(n, num):
  return ((n + (num - 1)) % num)

def left(n, num):
  return ((n + 1) % num)

class Philosopher(ActiveObject):
    def __init__(self, n):
        name = "philosopher_{}".format(n)
        super().__init__(name)

        self.n = n
        self.subscribe(Event(signal=signals.EAT))

@spy_on
def thinking(philosopher, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
        philosopher.post_fifo(
            Event(signal=signals.Tired),
            period=random.randint(1, 10),
            times=1,
            deferred=True)
        status = return_status.HANDLED
    elif(e.signal == signals.Tired):
        status = philosopher.trans(hungry)
    else:
        philosopher.temp.fun = philosopher.top
        status = return_status.SUPER
    return status

@spy_on
def hungry(philosopher, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
        philosopher.publish(
            Event(signal=signals.HUNGRY, payload=philosopher.n))
        status = return_status.HANDLED
    elif(e.signal == signals.EAT):
        if e.payload == philosopher.n:
            status = philosopher.trans(eating)
        else:
            status = return_status.HANDLED
    else:
        philosopher.temp.fun = philosopher.top
        status = return_status.SUPER
    return status

@spy_on
def eating(philosopher, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
        philosopher.post_fifo(
            Event(signal=signals.Full),
            period=random.randint(1, 10),
            times=1,
            deferred=True)
        status = return_status.HANDLED
    elif(e.signal == signals.Full):
        status = philosopher.trans(thinking)
    elif(e.signal == signals.EXIT_SIGNAL):
        philosopher.publish(
            Event(signal=signals.DONE, payload=philosopher.n))
        status = return_status.HANDLED
    else:
        philosopher.temp.fun = philosopher.top
        status = return_status.SUPER
    return status

class Table(ActiveObject):
    def __init__(self, name, number_of_philosophers):
        super().__init__(name)

        self.subscribe(Event(signal=signals.DONE))
        self.subscribe(Event(signal=signals.HUNGRY))

        self.forks  = [Fork.Free for i in range(number_of_philosophers)]
        self.is_hungry = [False for i in range(number_of_philosophers)]
        self.to_the_right_of = partial(right, num=number_of_philosophers)
        self.to_the_left_of = partial(left, num=number_of_philosophers)

@spy_on
def serving(table, e):
    status = return_status.UNHANDLED

    if (e.signal == signals.HUNGRY):
        n = e.payload
        m = table.to_the_left_of(n)
        if (table.forks[m] == Fork.Free) and (table.forks[n] == Fork.Free):
            table.forks[m] = Fork.Used
            table.forks[n] = Fork.Used
            table.is_hungry[n] = False
            table.publish(Event(signal=signals.EAT, payload=n))
        else:
            table.is_hungry[n] = True 
            status = return_status.HANDLED #TODO: Not sure why book example handles this in the else...

    elif (e.signal == signals.DONE):
        n = e.payload

        #set down the forks
        table.forks[n] = Fork.Free
        m = table.to_the_right_of(n)
        table.forks[m] = Fork.Free

        #check the person to the right is hungry and the fork to the OF THAT PERSON right is free...
        if table.is_hungry[m] and (table.forks[m] == Fork.Free) :
            table.forks[n] = Fork.Used
            table.forks[m] = Fork.Used
            table.is_hungry[m] = False
            table.publish(Event(signal=signals.EAT, payload=m))

        m = table.to_the_left_of(n)  # check the left neighbour
        n = table.to_the_left_of(m)  # left fork of the left neighbour

        #check the person to the left is hungry and the fork to the OF THAT PERSON right is free...
        if table.is_hungry[m] and (table.forks[n] == Fork.Free) :
            table.forks[m] = Fork.Used
            table.forks[n] = Fork.Used
            table.is_hungry[m] = False
            table.publish(Event(signal=signals.EAT, payload=m))
        
        status = return_status.HANDLED
    else:
        table.temp.fun = table.top  #or chart.top for the top most
        status = return_status.SUPER

    return status

if __name__ == "__main__":

    table = Table(name = 'table1',
        number_of_philosophers=NUMBER_OF_PHILOSOPHERS)
    table.start_at(serving)

    time.sleep(0.1)

    for n in range(NUMBER_OF_PHILOSOPHERS):
      philosopher = Philosopher(n)
      philosopher.start_at(thinking)
      philosopher.live_trace = True

    time.sleep(60) 
