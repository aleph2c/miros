from miros import (Event, signals, return_status, spy_on, ActiveObject)
import threading
import time
import sys

class DemoChart(ActiveObject):
  def __init__(self, name):
    super().__init__(name)
    self.foo = None

class HSMTesterThread(threading.Thread):
    def __init__(self, chart):
        threading.Thread.__init__(self)
        self.chart = chart
        self.boolKeepOnGoing = True
        self.dictsigcall = {'A' : self.callA,
                            'B' : self.callB,
                            'C' : self.callC,
                            'D' : self.callD,
                            'E' : self.callE,
                            'F' : self.callF,
                            'G' : self.callG,
                            'H' : self.callH,
                            'I' : self.callI,
                            'Q' : self.quit}
        self.siglist = list(self.dictsigcall.keys())

    def run(self):
        #print ("Starting")

        while self.boolKeepOnGoing:

            inputsingal = input("\nEnter Signal:")
            inputsingal = inputsingal.upper()

            if len(inputsingal) != 1 or inputsingal not in self.siglist: 
                print("Event not defined.") 
            else:
                self.dictsigcall[inputsingal]()

            time.sleep(.1)

        print ("Exiting " + self.name)

    def callA(self):
        self.chart.post_fifo(Event(signal=signals.A))

    def callB(self):
        self.chart.post_fifo(Event(signal=signals.B))

    def callC(self):
        self.chart.post_fifo(Event(signal=signals.C))

    def callD(self):
        self.chart.post_fifo(Event(signal=signals.D))

    def callE(self):
        self.chart.post_fifo(Event(signal=signals.E))

    def callF(self):
        self.chart.post_fifo(Event(signal=signals.F))

    def callG(self):
        self.chart.post_fifo(Event(signal=signals.G))

    def callH(self):
        self.chart.post_fifo(Event(signal=signals.H))

    def callI(self):
        self.chart.post_fifo(Event(signal=signals.I))

    def quit(self):
        self.boolKeepOnGoing = False

@spy_on
def s(demochart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):
        sys.stdout.write('s-Entry;')
        status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
        sys.stdout.write('s-Init;')
        status = demochart.trans(s11)
    elif(e.signal == signals.EXIT_SIGNAL):
        sys.stdout.write('s-Exit;')
        status = return_status.HANDLED
    elif(e.signal == signals.E):
        sys.stdout.write('s-E;')
        status = demochart.trans(s11)
    elif(e.signal == signals.I):
        if demochart.foo:
            demochart.scribble("settin foo to 0")
            demochart.foo = 0
        status = return_status.HANDLED
    else:
        demochart.temp.fun = demochart.top
        status = return_status.SUPER
    return status


@spy_on
def s1(demochart, e):
    status = return_status.UNHANDLED
    
    if(e.signal == signals.ENTRY_SIGNAL):    
        sys.stdout.write('s1-Entry;')
        status = return_status.HANDLED
    elif (e.signal == signals.INIT_SIGNAL):
        sys.stdout.write('s1-Init;')
        status = demochart.trans(s11)
    elif(e.signal == signals.EXIT_SIGNAL):
        sys.stdout.write('s1-Exit;')
        status = return_status.HANDLED
    elif(e.signal == signals.A):
        sys.stdout.write('s1-A;')
        status = demochart.trans(s1)
    elif(e.signal == signals.B):
        status = demochart.trans(s11)
    elif(e.signal == signals.C):
        status = demochart.trans(s2)
    elif(e.signal == signals.D):
        if demochart.foo == 0:
            demochart.foo = 1
            status = demochart.trans(s)
    elif(e.signal == signals.F):
        status = demochart.trans(s211)
    else:
        demochart.temp.fun = s
        status = return_status.SUPER
    return status   

@spy_on
def s11(demochart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):    
        sys.stdout.write('s11-Entry;')
        status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
        sys.stdout.write('s11-Exit;')
        status = return_status.HANDLED
    elif(e.signal == signals.D):
        if demochart.foo:
            demochart.scribble("settin foo to 0")
            demochart.foo = 0
            status = demochart.trans(s1)            
    elif(e.signal == signals.G):
        status = demochart.trans(s211)
    elif(e.signal == signals.H):
        status = demochart.trans(s)
    else:
        demochart.temp.fun = s1
        status = return_status.SUPER
    return status

@spy_on
def s2(demochart, e):
    status = return_status.UNHANDLED

    if(e.signal == signals.ENTRY_SIGNAL):    
        sys.stdout.write('s2-Entry;')
        status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
        sys.stdout.write('s2-Init;')
        status = demochart.trans(s211)
    elif(e.signal == signals.EXIT_SIGNAL):
        sys.stdout.write('s2-Exit;')
        status = return_status.HANDLED    
    elif(e.signal == signals.I):
        if not demochart.foo:
            demochart.scribble("settin foo to 1")
            demochart.foo = 1
        status = return_status.HANDLED
    elif(e.signal == signals.C):
        status = demochart.trans(s1)
    elif(e.signal == signals.F):
        status = demochart.trans(s11)
    else:
        demochart.temp.fun = s
        status = return_status.SUPER
    return status

@spy_on
def s21(demochart, e):
    status = return_status.UNHANDLED
    if(e.signal == signals.ENTRY_SIGNAL):    
        sys.stdout.write('s21-Entry;')
        import pdb; pdb.set_trace()
        status = return_status.HANDLED
    elif(e.signal == signals.INIT_SIGNAL):
        sys.stdout.write('s21-Init;')
        status = demochart.trans(s211)
    elif(e.signal == signals.EXIT_SIGNAL):
        sys.stdout.write('s21-Exit;')
        status = return_status.HANDLED 
    elif(e.signal == signals.A):
        status = demochart.trans(s21)
    elif(e.signal == signals.B):
        status = demochart.trans(s211)
    elif(e.signal == signals.G):
        status = demochart.trans(s11)
    else:
        demochart.temp.fun = s2
        status = return_status.SUPER
    return status

@spy_on
def s211(demochart, e):
    status = return_status.UNHANDLED
    
    if(e.signal == signals.ENTRY_SIGNAL):    
        sys.stdout.write('s211-Entry;')
        status = return_status.HANDLED
    elif(e.signal == signals.EXIT_SIGNAL):
        sys.stdout.write('s211-Exit;')
        status = return_status.HANDLED   
    elif(e.signal == signals.D):
        status = demochart.trans(s21)
    elif(e.signal == signals.H):
        status = demochart.trans(s)
    else:
        demochart.temp.fun = s21
        status = return_status.SUPER
    return status

if __name__ == "__main__":
    chart = DemoChart(name='demochart1')
    #chart.live_trace = True
    #chart.live_spy = True
    chart.start_at(s2)    
    
    hsmtester = HSMTesterThread(chart)
    hsmtester.start()
    
    
