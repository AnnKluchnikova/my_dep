"""
Программа для получения POST от точки доступа в виде json объекта
и отправки его с помощью pipe в процесс анализа этих данных
"""

# Скрипт самодостаточный, поэтому может быть собран в исполняемый файл
# pyinstaller -D -F -n http -c "http_server.py"

import json
from aiohttp import web

# Собственная библиотека для управления логированием
import my_logging as lg

# ==============================[Внешний класс]=================================

class WebServer():
# 
  async def _request_handler(self, request: web.Request):
  # 
    try:
    # 
      body = await request.json()

      if (__name__ == '__main__'):
      # 
        print(json.dumps(body, indent = 2))
      # 
      else:
        self.pipe.send(["ANALYZ", body])
    # 
    except Exception as exp:
    # 
      print("[WARNING] Failed to process request: {}".format(exp))
      return web.Response(status = 500)
    # 

    return web.Response()
  # 

  def __init__(self, serv_analyz_conn, log):
  # 
    self.log = log
    self.pipe = serv_analyz_conn
    self.app = web.Application()
    self.app.add_routes([web.post('/', self._request_handler)])
  # 

  # ---------------------[Методы для внешнего использования]----------------------

  def run(self, port, host):
  # 
    self.log._print(self.log.INFO, f"Start HTTP-server: \" http://{host}:{host}\"")
    web.run_app(self.app, port = port, host = host)
  # 

  # ------------------------------------------------------------------------------
# 

# ==============================================================================

if (__name__ == '__main__'):
# 
  '''
  Для проверки можно из другого терминала отправить:

  curl -X POST 192.168.1.1:9090  -d "{\"probe_requests\":\
  [{\"mac\":\"3A-B5-5E-D9-BB-B0\",\"timestamp\":\"946724234\",\
  \"type_bitmask\":4,\"ssid\":\"\"}]}"

  [ПРИМЕЧАНИЕ] Длинный пример может использоваться, чтобы проверить
               работоспособность всего приложения в целом
  '''
  log = lg._logging(lg.OFF)

  server = WebServer(None, log)
  server.run(9090, '192.168.1.1')
# 