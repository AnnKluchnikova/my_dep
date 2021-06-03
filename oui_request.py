'''
Программа предназначена для автоматизации загрузки официальной базы OUI
и приведение ее к нужному виду для удобства использования

[ПРИМЕЧАНИЕ] Официальная база - это посто текстовый файл со стандартным текстом
             Для работы приложения (конкретно внутреннего фильтра) необходимо
             иметь удобную для парсинга базу. Соответсвенно было решено
             переписать официальную базу в json формат оставив только hex
             уникального идентификатора и название организации, для которой был
             выделен этот диапазон
'''
import urllib.request
import shutil
import json
import os

def _oui_request(url, src_file):
# 
  '''
  Получение данных об OUI с указанного адреса (url) и запись их в локальный файл

  [ПРИМЕЧАНИЕ] Локальный файл будет создан и заполнен данными, а после обработки
               удален. Такое временное хранение в файле необходимо, так как
               объем данных очень большой, а парсить их в виде python строки
               очень не удобно
  '''
  # TODO Вставить исключения на urllib.request.urlopen
  with urllib.request.urlopen(url) as response,\
       open(src_file, 'wb') as out_file:
  # 
    shutil.copyfileobj(response, out_file)
  # 

  return True
# 

def _create_OUI_db(src_file, dst_file):
# 
  # Объек, в который будут записываться нужные данные
  oui = list()

  try:
  # 
    with open(src_file, "r") as read_file:
    # 
      for line in read_file:
      # 
        '''
        В файле много пустых строк и прочего, что сразу же нужно игнорировать
        Поэтому ищем строки, которые имеют миним 16 символов, что соответствует
        началу строки /00-D0-EF   (hex)/
        '''
        if len(line) < 16:
          continue

        '''
        Убедимся, что на вход пришла строка с hex записью,
        в которой разделителями являются '-'
        '''
        if (line[2] == '-' and line[5] == '-'):
        # 
          org = line[16:].strip()
          oui.append(dict(hex = line[0:8], org = org))
        # 
      # 
    # 
  # 
  except FileNotFoundError:
    return False

  '''
  Запишем полученные данные в новый файл,
  на который позже будет ссылаться приложение
  '''
  with open(dst_file, 'w') as write_file:
    json.dump(oui, write_file, indent=2)

  # Удалим уже ненужный текстовый файл для временного хранения
  os.remove(src_file)

  return True
# 

# ==========================[Импортируемая функция]=============================

def get_path_to_OUI_db(log):
# 
  src_file = "oui.txt"
  dst_file = "oui.json"
  url = "http://standards-oui.ieee.org/oui/oui.txt"

  # Проверим, есть ли уже в папке нужный файл
  if(os.path.isfile(dst_file) == True):
  # 
    log._print(log.INFO, f"Path to the OUI database: ./{dst_file}")
    return dst_file
  # 

  with open(src_file, "wb"):
    log._print(log.INFO, "Please wait a few seconds...\n"
              "       The OUI database is being loaded to make the app work")

  if (_oui_request(url, src_file) != True):
  # 
    log._print(log.ERROR, "Failed to load the OUI database\n"
          f"        from the \"{url}\" resource\n")
    return None
  # 

  if (_create_OUI_db(src_file, dst_file) != True):
  # 
    log._print(log.ERROR, "Failed to load the OUI database\n")
    return None
  # 

  log._print(log.INFO, "OUI database loaded successfully\n"
             f"       Path: ./{dst_file}")
  return dst_file
# 

# ==============================================================================

if (__name__ == '__main__'):
# 
  get_path_to_OUI_db()
# 
