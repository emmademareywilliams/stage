import tkinter as tk
import Pmw

from PyFina import getMeta, PyFina
import struct
import numpy as np
import matplotlib.pylab as plt
import matplotlib
import datetime
import time
from dateutil import tz

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

LOCTZ = tz.gettz('Europe/Paris')
dir = "/home/ludivine/github/stage/CMB/Data/phpfina"

"""
Global variables
"""

# monthDict = {month: number of days}
monthDict = {}
for k in range(1,13):
    if k<=7:
        if k%2 == 1:
            monthDict[k] = 31
        else:
            monthDict[k] = 30
    if k>=8:
        if k%2 == 1:
            monthDict[k] = 30
        else:
            monthDict[k] = 31
monthDict[2] = 28

monthDictLit = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5:'May', 6:'June', 7: 'July',
                8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

pumpOff = {}


"""
General functions used later on
"""

def getMetas(nb,dir=dir):
    """
    read meta given a feed number
    print (interval,starting timestamp)
    """
    f=open("{}/{}.meta".format(dir,nb),"rb")
    f.seek(8,0)
    hexa = f.read(8)
    aa= bytearray(hexa)
    if len(aa)==8:
      decoded=struct.unpack('<2I', aa)
    print(decoded)
    f.close()
    return decoded


def secondToHumanTime(sec, fmt="%m-%d \n %H: %M: %z", tz=LOCTZ):
    """
    equivalent between number of seconds and date readable by a human

    sec: unix number giving the starting time of the experiment
    tz: time zone object
    returns the corresponding date (format dd/ mm/ yyyy  h: m: s)
    """
    return datetime.date.fromtimestamp(sec).strftime(fmt)


def HumanTimetoUnix(datetime):
    """
    inverse function of secondToHumanTime, aka gives the Unix time stamp associated with a given dates

    datetime: datetime object corresponding to a date (yyyy - mm - dd)
    returns a Unix number (int)
    """
    return int(time.mktime(datetime.timetuple()))


def getStart(feednb):
    """
    returns the starting timestamp associated with a given feed number
    """
    meta = getMeta(feednb,dir)
    start = meta["start_time"]
    return start


def resetPumpOff():
    """
    each time we click on the "Enter new values" button, the dictionnary is reinitialised so that we can enter a
    new time period during which the pump is not operating
    """
    pumpOff = {"startday": None, "startmonth": None, "starthour": None, "endday": None, "endmonth": None, "endhour": None}

#resetPumpOff()


def modifyData(feednb, data):
    """
    used to change the values of the pump operation (modification of the .dat file)

    feednb: feed number (will be 42 since we only want to modify the pump operation data)
    data: dict as defined by pumpOff, which corresponds to the period of time during which
    the pump is not functionning
    """
    datetimeStart = datetime.datetime.strptime('2021 {} {} {}:00'.format(data["startmonth"], data["startday"], data["starthour"]), '%Y %m %d %H:%M')
    datetimeEnd = datetime.datetime.strptime('2021 {} {} {}:00'.format(data["endmonth"], data["endday"], data["endhour"]), '%Y %m %d %H:%M')
    starttimeoff = HumanTimetoUnix(datetimeStart)
    endtimeoff = HumanTimetoUnix(datetimeEnd)

    interval, beginning = getMetas(feednb)
    newvalues = []
    firststepoff = int((starttimeoff - beginning)/interval)
    laststepoff = int((endtimeoff - beginning)/interval)
    currentstep = int((time.time()- beginning)/interval)
    for i in range(firststepoff):
        newvalues.append(1)
    for i in range(firststepoff, laststepoff):
        newvalues.append(0)
    for i in range(laststepoff, currentstep):
        newvalues.append(1)

    # the new values (null) are written in the .dat file:
    # WARNING: when opening a file with the "r+" mode, we delete the data of the file! Thus we must rewrite
    # the information contained in the file
    f = open("{}/{}.dat".format(dir,feednb),"wb")
    #d = f.readlines()
    #f.seek(0)
    #for i in d:
        #if i != "line you want to remove...":
            #f.write(i)
    #f.seek(0)
    format = "<{}".format("f"*len(newvalues))
    bin = struct.pack(format,*newvalues)
    f.write(bin)
    f.close()

exampleData = {"startday": 10, "startmonth": 2, "starthour": 10, "endday": 10, "endmonth": 2, "endhour": 14}
modifyData(42, exampleData)


def resetData(feednb):
    """
    resets the data in its original state
    feednb: feed number (will be 42)
    """
    interval, starttime = getMetas(feednb)
    now = time.time()
    duration = now - starttime
    nbpoints = int(duration / interval)
    oldvalues = np.ones(nbpoints)

    f=open("{}/{}.dat".format(dir,feednb),"wb")
    format="<{}".format("f"*len(oldvalues))
    bin=struct.pack(format,*oldvalues)
    f.write(bin)
    f.close()

#resetData(42)

"""
FIRST STEP
    --> the data from the dat file are retrieved and plotted in a matplotlib graph
"""

def graphPyfina(feednb, frame, Text=False):
    """
    creates the matplotlib graph representing the data corresponding to the feed number

    feednb: int that is the flux number we want to get on the graph
    frame: object tk.Frame aka frame in which the graphs are going to be printed
    """
    meta = getMeta(feednb,dir)
    step = 3600
    start = meta["start_time"]
    window = 10*24*3600  # duration of the plotting (here 1 week)
    length = meta["npoints"] * meta["interval"]  # time duration of the retrieved data
    if window > length:
        window = length
    nbpts = window // step
    data = PyFina(feednb, dir, start, step, nbpts)
    if Text:
        dataText = PyFina(5, dir, start, step, nbpts)
        # we want to print the outter temperature in the same graph

    f = matplotlib.pyplot.figure(figsize=(4,2), dpi=100)
    a = f.add_subplot(111)
    xrange = data.timescale()
    xhour = xrange /step
    xhuman = [secondToHumanTime(x + start) for x in xrange]
    if feednb == 42:
        plt.ylabel("pump operation")
        plt.ylim(0,2)
    else:
        plt.ylabel("temperature")
    plt.xlabel("time (time step = {} s)".format(step))
    plt.xticks(xrange, xhuman, rotation=0, fontsize=5)
    a.xaxis.set_major_locator(plt.MaxNLocator(10))
    a.plot(xrange, data)
    if Text:
        a.plot(xrange, dataText, label="Text")
        plt.legend(loc='upper right', bbox_to_anchor=(1, 1.2), ncol=3)

    canvas = FigureCanvasTkAgg(f, root)
    canvas.draw()
    if feednb == 42:
        rownb=2
    # fill means the figure will fill the whole space of the window
    # expand means that the figure will adapt itself to the format of the canvas if the user changes its shape
    else:
        rownb=1
    canvas.get_tk_widget().grid(row=rownb, columnspan=4, padx=5, pady=5)

    #toolbar = NavigationToolbar2Tk(canvas, root)
    #toolbar.update()
    canvas._tkcanvas.grid()

"""
WIDGET FUNCTIONS
    --> commands that are called when the widgets are been used
"""

def quitter():
    root.quit()     # stops mainloop
    root.destroy()


def getStartDay():
    """
    day is the value (int) returned by the combobox once the user has entered the day they want
    updates the dictionnary pumpOff according to those values
    """
    pumpOff['startday'] = startdayCombo.get()

def getStartMonth():
    pumpOff['startmonth'] = startmonthCombo.get()

def getStartHour():
    pumpOff['starthour'] = starthourCombo.get()

def getEndDay():
    pumpOff['endday'] = day

def getEndMonth(month):
    pumpOff['endmonth'] = month

def getEndHour(hour):
    pumpOff['endhour'] = hour


"""
SECOND STEP
    --> the tkinter interface is created and configured
"""

root = tk.Tk()
root.title("visualisation")
root.geometry("1900x1000")
# the window is full screen
frame = tk.Frame(root)

start = getStart(22)
localstart = datetime.datetime.fromtimestamp(start)
utcstart = datetime.datetime.utcfromtimestamp(start)
title = tk.Label(root, text="starting on :\nUTC {}\n{} {}".format(utcstart, time.tzname[0], localstart))
title.grid(row=0, column=2)

graphPyfina(19, frame, Text=True)
graphPyfina(42, frame)


# Widgets configuration:

fen = Pmw.initialise(root)
texte1 = tk.Label(fen, text="Start time:")
texte2 = tk.Label(fen, text="End time:")

# configuration of the comboboxes
date, clock = str(localstart).split(' ')
year, month, day = date.split('-')
hour, minute, second = clock.split(':')

limitday = monthDict[int(month)]
months = [int(month)]
days = [int(day)]
i = 0
for k in range(1,10):
    if int(day)+k == limitday +1:
        i=1
        days.append(i)
        months.append(int(month)+1)
    else:
        i = i+1
        if int(day)+k > limitday:
            days.append(i)
        else:
            days.append(int(day)+i)
hours = (k for k in range(1,25))

startdayCombo = Pmw.ComboBox(fen, labelpos = 'nw',
                       label_text = 'day',
                       scrolledlist_items = days,
                       listheight = 150,
                       selectioncommand = getStartDay)
#startdayCombo.bind("<<ComboboxSelected>>", getStartDay)

startmonthCombo = Pmw.ComboBox(fen, labelpos = 'nw',
                       label_text = 'month',
                       scrolledlist_items = months,
                       listheight = 150,
                       selectioncommand = getStartMonth)
startmonthCombo.bind("<<ComboboxSelected>>", getStartMonth)

starthourCombo = Pmw.ComboBox(fen, labelpos = 'nw',
                       label_text = 'hour',
                       scrolledlist_items = hours,
                       listheight = 150,
                       selectioncommand = getStartHour)
starthourCombo.bind("<<ComboboxSelected>>", getStartHour)

enddayCombo = Pmw.ComboBox(fen, labelpos = 'nw',
                       label_text = 'day',
                       scrolledlist_items = days,
                       listheight = 150,
                       selectioncommand = getEndDay)
enddayCombo.bind("<<ComboboxSelected>>", getEndDay)

endmonthCombo = Pmw.ComboBox(fen, labelpos = 'nw',
                       label_text = 'month',
                       scrolledlist_items = months,
                       listheight = 150,
                       selectioncommand = getEndMonth)
endmonthCombo.bind("<<ComboboxSelected>>", getEndMonth)

endhourCombo = Pmw.ComboBox(fen, labelpos = 'nw',
                       label_text = 'hour',
                       scrolledlist_items = hours,
                       listheight = 150,
                       selectioncommand = getEndHour)
endhourCombo.bind("<<ComboboxSelected>>", getEndHour)


texte1.grid(row =3, column =1)
startdayCombo.grid(row =4, column =1, padx=5)
startmonthCombo.grid(row =4, column =2, padx=5)
starthourCombo.grid(row =4, column =3, padx=0)

texte2.grid(row =5, column =1)
enddayCombo.grid(row =6, column =1, padx=5)
endmonthCombo.grid(row =6, column =2, padx=5)
endhourCombo.grid(row =6, column =3, padx=0)

apply = tk.Button(fen, text='Apply')
apply.grid(column=1, row=7)

bouton = tk.Button(fen, text="Exit", command=quitter)
bouton.grid(column=2, row=7)

print(pumpOff)

root.mainloop()
time.sleep(10)
