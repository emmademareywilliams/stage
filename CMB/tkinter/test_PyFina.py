
from PyFina import getMeta, PyFina
import matplotlib.pylab as plt
import urllib.request as request
import datetime
import time


def retrieve(feed_nb, extension):
    file_name = "{}.{}".format(feed_nb, extension)
    url = "https://raw.githubusercontent.com/Open-Building-Management/PyFina/master/tests/datas/{}".format(file_name)
    request.urlretrieve(url, file_name)
    # feed_nb is linked to the data files (cf. THEMIS datasets where each variable (temperature, etc.)
    # has an attributed number)


#print("downloading some datas for testing....")
#retrieve(feed_nb, "dat")
#retrieve(feed_nb, "meta")
#input("downloads completed :-) press_any_key")

# feed storage on a standard emoncms server
feed_nb = 57
dir = "/Users/lisa/Documents/Emma/E3/DEUXIÈME ANNÉE/Stage CEREMA/GitHub/stage/RCmodel/phpfina_cerema2020"
#dir = "."
meta = getMeta(feed_nb,dir)
print(meta)
step = 3600
start = meta["start_time"]
window = 10*24*3600  # duration of the plotting (here 1 week)
length = meta["npoints"] * meta["interval"]  # time duration of the retrieved data
if window > length:
    window = length
nbpts = window // step
Text = PyFina(feed_nb, dir, start, step, nbpts)

localstart = datetime.datetime.fromtimestamp(start)
utcstart = datetime.datetime.utcfromtimestamp(start)
title = "starting on :\nUTC {}\n{} {}".format(utcstart, time.tzname[0], localstart)
xrange = Text.timescale()
plt.subplot(111)
plt.title(title)
plt.ylabel("outdoor temperature")
plt.xlabel("time in seconds")
plt.plot(xrange, Text)
plt.show()

