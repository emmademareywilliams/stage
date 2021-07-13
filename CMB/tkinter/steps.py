import tkinter as tk
import matplotlib.pylab as plt
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from dateutil import tz

LOCTZ = tz.gettz('Europe/Paris')
print(LOCTZ)


######################## DEUXIEME POINT #########################
value = False

f = matplotlib.pyplot.figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)
a.plot([1,2,3,4,5], [1,2,3,4,5])
plt.show()


if value:
    window = tk.Tk()
    window.title("visualisation")
    frame = tk.Frame(window)

    canvas = FigureCanvasTkAgg(f, window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
# fill means the figure will fill the whole space of the figure
# expand means tht the figure will adapt itself to the format of the canvas if the user changes its shape

    bouton = tk.Button(window, text="quitter", command=window.destroy)
    bouton.pack()

    window.mainloop()
