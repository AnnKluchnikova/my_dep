"""
Головная программа, которая создает потоки для трех функциональных частей:
  для сервера, импортируя как SERVER
  для анализатора, импортируя как ANALYZER
  для графической оболочки, импортируя как GUI
"""
from multiprocessing import Process, Pipe
from http_server import WebServer as SERVER
from analyzer import DataAnalyzer as ANALYZER
from window import MainWindow as GUI
from sys import argv
from argparse import ArgumentParser
import my_logging as lg

def server_for_wap(serv_analyz_conn, log, port, host):
  server = SERVER(serv_analyz_conn, log)
  server.run(port, host)

def app_analyzer(analyz_serv_conn, analyz_win_conn, log):
  analizer = ANALYZER(analyz_serv_conn, analyz_win_conn, log)
  analizer.run()

def app_window(win_analyz_conn, log, time_update):
  window = GUI(win_analyz_conn, log, time_update)
  window.run()

def main():
  print("\nStart the app...\n")

  def keys_parser():
    parser = ArgumentParser()
    parser.add_argument ('-ur', '--updaterate', type=int)
    parser.add_argument ('-lm', '--logmask', type=int)
    parser.add_argument ('-mp', '--myport', type=int)
    parser.add_argument ('-mh', '--myhost')
    return parser

  parser = keys_parser()
  key_space = parser.parse_args(argv[1:])

  if key_space.logmask is None:
    log = lg._logging(lg.OFF)
  else:
    log = lg._logging(key_space.logmask)

  port = 9090
  host = '192.168.1.1'

  if key_space.myport is not None:
    port = key_space.myport
  if key_space.myhost is not None:
    host = key_space.myhost

  time_update = 60000

  if key_space.updaterate is not None:
    time_update = key_space.updaterate

  try:
    serv_analyz_conn, analyz_serv_conn = Pipe()
    analyz_win_conn, win_analyz_conn = Pipe()

    server_p = Process(target = server_for_wap, args = (serv_analyz_conn, log, port, host))
    analyzer_p = Process(target = app_analyzer, args = (analyz_serv_conn, analyz_win_conn, log))
    window_p = Process(target = app_window, args = (win_analyz_conn, log, time_update))

    server_p.start()
    analyzer_p.start()
    window_p.start()

    while True:
      live_analyz = analyzer_p.is_alive()
      live_win = window_p.is_alive()

      if (live_analyz == False):
        log._print(log.FATAL, "The analyzer stopped working")
        if True:
          raise KeyboardInterrupt

      if (live_win == False):
        log._print(log.FATAL, "The GUI stopped working")
        if True:
          raise KeyboardInterrupt
  except KeyboardInterrupt:
    print("\nShutting down the app...\n")

    if(server_p.is_alive() == True):
      server_p.terminate()
    if(analyzer_p.is_alive() == True):
      analyzer_p.terminate()
    if(window_p.is_alive() == True):
      window_p.terminate()

    serv_analyz_conn.close()
    analyz_serv_conn.close()

    analyz_win_conn.close()
    win_analyz_conn.close()

if __name__ == '__main__':
  main()