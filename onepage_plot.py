import numpy as np
import tkinter as Tk
import tkinter.ttk as ttk
import matplotlib.dates as md
from itertools import groupby
import matplotlib.pyplot as plt
from datetime import datetime as dt
from matplotlib.backends.backend_tkagg import (
  FigureCanvasTkAgg, NavigationToolbar2Tk)

# ==============================================================================

class OnePagePlote(ttk.Notebook):
# 
  def __init__(self, parent):
    ttk.Notebook.__init__(self, parent)

    self.plot_1 = RushHourPlot(self)
    self.add(self.plot_1, text = 'NEW')

    self.plot_2 = TypeOfUserPlot(self)
    self.add(self.plot_2, text = 'ONLINE')

    self.plot = MacStatusBarPlot(self)
    self.add(self.plot, text = 'STATUS')

    self.plot_3 = PiePlotes(self)
    self.add(self.plot_3, text = 'OTHER')

    self.pack(side = Tk.TOP, fill = Tk.BOTH, expand = True)
    self.bind("<<NotebookTabChanged>>", None)

# ---------------------[Методы для внешнего использования]----------------------

  def update_plot(self, data):
  # 
    mac_base = data.get('mac_base')
    if mac_base is None:
      mac_base = dict()

    sess_act = data.get('session_activ')
    if sess_act is None:
      sess_act = dict()

    self.plot_1.update_plot(mac_base)
    self.plot_2.update_plot(sess_act)
    self.plot_3.update_plot(mac_base)
    self.plot.update_plot(sess_act)
  # 

# ------------------------------------------------------------------------------
# 

# ==============================================================================

class RushHourPlot(Tk.Frame):
# 
# ---------------------[Методы для внешнего использования]----------------------

  def update_plot(self, data):
  # 
    def _parse_data(data):
    # 
      timestamps = list(info['first_time'] for mac, info in data.items())
      data = [dt.fromtimestamp(ts) for ts in timestamps]
      data.sort()

      return data
    # 

    n_bins = 24

    os_x = _parse_data(data)
    if (len(os_x) != 0):
    # 
      self.axs.clear()
      n, bins, patches = self.axs.hist(os_x, bins = n_bins)

      self.plot.autofmt_xdate(rotation = 10)
      tm_form = md.DateFormatter('%d/%m/%Y\n %H:%M')
      self.axs.xaxis.set_major_formatter(tm_form)

      for i in range(len(patches)):
        patches[i].set_facecolor(plt.cm.viridis(n[i]/max(n)))

      self.axs.grid(axis = 'y')
      self.axs.set_title('Discovering new devices', fontsize=15)
      self.axs.set_ylabel('MAC Quantity', fontsize=13)
      self.axs.set_xlabel('Data', fontsize=13)

      self.canvas.draw()
    # 
  # 

# ------------------------------------------------------------------------------

  def __init__(self, parent):
  # 
    Tk.Frame.__init__(self, parent)

    self.plot = plt.Figure()
    self.axs = self.plot.add_subplot(111)

    self.canvas = FigureCanvasTkAgg(self.plot, master=self)
    self.canvas.draw()

    toolbar = NavigationToolbar2Tk(self.canvas, self)
    toolbar.update()

    self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)
  # 
# 

# ==============================================================================

class PiePlotes(Tk.Frame):
# 
  def MacStatusPie(self, data):
  # 
    def _parse_data(data):
    # 
      labels = list()
      stat = list()

      data_list = list(info for mac, info in data.items())

      if (len(data_list) != 0):
      # 
        result = groupby(sorted(data_list, key=lambda x: x['status']),\
                                                    lambda x: x['status'])

        for key, count in result:
          labels.append(key)
          stat.append(len(list(count)))
      # 

      return stat, labels
    # 

    def _func(pct, stat):
    # 
      absolute = int(pct/100.*np.sum(stat))
      print("{:.1f}%\n({:d})".format(pct, absolute))
      return "{:.1f}%\n({:d})".format(pct, absolute)
    # 

    stat, labels = _parse_data(data)
    if (len(stat) != 0):
    # 
      self.axs1.clear()

      area, t, a = self.axs1.pie(stat,\
        autopct=lambda p : '{:.2f}%  ({:,.0f})'.format(p,p * sum(stat)/100),\
            textprops=dict(color="w"))

      self.axs1.legend(area, labels, loc="lower left",\
                       bbox_to_anchor=(0.85, 0, 0.5, 1))

      self.axs1.set_title('Ratio of MAC address statuses\nAll adresses: '\
                            +str(sum(stat)), fontsize=14)
    # 
  # 

  def TopVendorPie(self, data):
  # 
    def _parse_data(data):
    # 
      stat = list()
      recipe = list()
      list_stat = list()

      data_list = list(info for mac, info in data.items())

      if (len(data_list) != 0):
      # 
        result = groupby(sorted(data_list, key=lambda x: x['vendor']),\
                                                  lambda x: x['vendor'])

        # Считаем вендоров только по подтвержденным MAC
        for key, count in result:
        # 
          check_list = list(count)
          count_item = 0

          for item in check_list:
            if item['status'] == 'confirmed':
              count_item += 1

          list_stat.append((key, count_item))
        # 

        list_stat.sort(key=lambda i: i[1], reverse = True)

        every = sum(x[1] for x in list_stat)

        for item in list_stat[0:5]:
          recipe.append(item[0])
          stat.append(round(100 * item[1] / every, 1))

        tes = sum(x[1] for x in list_stat[3:len(list_stat)])

        recipe.append('Other')
        stat.append(round(100 * tes / every, 1))
      # 

      return stat, recipe
    # 

    stat, recipe = _parse_data(data)
    if (len(stat) != 0):
    # 
      self.axs2.clear()
      wedges, texts = self.axs2.pie(stat, wedgeprops=dict(width=0.5), startangle=-40)

      bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.6)
      kw = dict(arrowprops=dict(arrowstyle="-"),
                bbox=bbox_props, zorder=0, va="center")

      for i, p in enumerate(wedges):
      # 
        ang = (p.theta2 - p.theta1)/2. + p.theta1

        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        horiz = {-1: "right", 1: "left"}[int(np.sign(x))]
        connstyle = "angle,angleA=0,angleB={}".format(ang)

        kw["arrowprops"].update({"connectionstyle": connstyle})

        self.axs2.annotate(recipe[i] +' '+ '(' + str(stat[i]) + '%'+ ')',\
                            xy=(x, y),
                            xytext=(1.1*np.sign(x), 1.2*y),
                            horizontalalignment=horiz, **kw
                          )
      # 

      self.axs2.set_title('Vendor popularity', fontsize=15)
      self.canvas.draw()
    # 
  # 

# ---------------------[Методы для внешнего использования]----------------------

  def update_plot(self, data):
  # 
    self.MacStatusPie(data)
    self.TopVendorPie(data)
  # 

# ------------------------------------------------------------------------------

  def __init__(self, parent):
    Tk.Frame.__init__(self, parent)

    self.plot = plt.Figure()
    self.axs1 = self.plot.add_subplot(121)
    self.axs2 = self.plot.add_subplot(122)

    self.canvas = FigureCanvasTkAgg(self.plot, self)
    self.canvas.draw()

    toolbar = NavigationToolbar2Tk(self.canvas, self)
    toolbar.update()

    self.canvas._tkcanvas.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=True)
# 

# ==============================================================================

class TypeOfUserPlot(Tk.Frame):
# 
  def update_plot(self, data):
  # 
    def _parse_data(data):
    # 
      x = list()
      y_new = list()
      y_rep = list()

      for time, info in data.items():
      # 
        x.append(dt.fromtimestamp(time))
        y_new.append(info['new'])
        y_rep.append(info['all'] - (info['new'] + info['filt']))
      # 

      y = {'Again': y_rep, 'New': y_new}
      return x, y
    # 

    x, y = _parse_data(data)

    self.axs.clear()
    self.axs.stackplot(x, y.values(), labels = y.keys())

    self.axs.set_title('Online appearance statistics', fontsize=15)
    self.axs.set_ylabel('Devices quantity', fontsize=13)
    self.axs.set_xlabel('Data', fontsize=13)

    self.axs.legend(bbox_to_anchor=(1.1, 1.05), title = 'Types',
                     fancybox=True, shadow=True)

    self.plot.autofmt_xdate(rotation = 10)
    tm_form = md.DateFormatter('%d/%m/%Y\n %H:%M')
    self.axs.xaxis.set_major_formatter(tm_form)

    self.canvas.draw()
  # 

  def __init__(self, parent):
  # 
    Tk.Frame.__init__(self, parent)

    self.plot = plt.Figure()
    self.axs = self.plot.add_subplot(111)

    self.canvas = FigureCanvasTkAgg(self.plot, self)
    self.canvas.draw()

    toolbar = NavigationToolbar2Tk(self.canvas, self)
    toolbar.update()

    self.canvas._tkcanvas.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=True)
  # 
# 

# ==============================================================================

class MacStatusBarPlot(Tk.Frame):
# 
  def update_plot(self, data):
  # 
    x = list()

    rand = list()
    unconf = list()
    conf = list()

    for time, info in data.items():
    # 
      x.append(dt.fromtimestamp(time))

      stat = info.get('status_stat')

      conf.append(stat['conf'])
      rand.append(stat['rand'])
      unconf.append(info['new'] - (stat['conf'] + stat['rand']))
    # 

    y = {'Confirmed': conf, 'Random': rand, 'Unconfirmed': unconf}

    self.axs.clear()

    self.axs.stackplot(x, y.values(), labels = y.keys())

    self.axs.set_title('Revealed addresses statistics', fontsize=15)
    self.axs.set_ylabel('MAC quantity', fontsize=13)
    self.axs.set_xlabel('Data', fontsize=13)

    self.axs.legend(bbox_to_anchor=(1.1, 1.05), title = 'Status',
                     fancybox=True, shadow=True)

    self.plot.autofmt_xdate(rotation = 10)
    tm_form = md.DateFormatter('%d/%m/%Y\n %H:%M')
    self.axs.xaxis.set_major_formatter(tm_form)

    self.canvas.draw()
  # 

  def __init__(self, parent):
  # 
    Tk.Frame.__init__(self, parent)

    self.plot = plt.Figure()
    self.axs = self.plot.add_subplot(111)

    self.canvas = FigureCanvasTkAgg(self.plot, self)
    self.canvas.draw()

    toolbar = NavigationToolbar2Tk(self.canvas, self)
    toolbar.update()

    self.canvas._tkcanvas.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=True)
  # 
# 

# ==============================================================================
