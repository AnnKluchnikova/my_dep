from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk)

import matplotlib.pyplot as plt
import tkinter.ttk as ttk
import tkinter as Tk

import random
import datetime

import matplotlib.dates as md

root = Tk.Tk()

root.title("RADMAC")

# Создаем фигуру и ставим вниз окна
plot = plt.Figure()
ax = plot.add_subplot(111)

x = [datetime.datetime.now() + datetime.timedelta(hours=i) for i in range(12)]
y = [i+random.gauss(0,1) for i,_ in enumerate(x)]

x_1 = [datetime.datetime.now() + datetime.timedelta(hours=i) for i in range(12)]
y_1 = [i+random.gauss(0,1) for i,_ in enumerate(x)]

ax.plot(x,y)
ax.plot(x_1,y_1)

plot.autofmt_xdate(rotation = 10)
tm_form = md.DateFormatter('%d/%m/%Y\n %H:%M')
ax.xaxis.set_major_formatter(tm_form)

canvas = FigureCanvasTkAgg(plot, master=root)
canvas.draw()

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()

canvas._tkcanvas.pack(side = Tk.BOTTOM, fill = Tk.BOTH, expand = True)
# ==============================

root.mainloop()