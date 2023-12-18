# parse_robot_rostransnadzor
Робот парсер позволяет скачивать и фильтровать разрешительные документы с сайта РОСТРАНСНАДЗОР (https://rostransnadzor.gov.ru).
Робот состоит из двух частей: downloader.py (API для работы с сайтом https://rostransnadzor.gov.ru) и app.py (скрипт для работы робота через консоль).
Также для работы робота необходим конфиг файл (.xlsx), который содержит в себе список необходимых для скачивания файлов и фильтров к ним
(его можно создать коммандой "app.py -config" и он появится рядом с app.py).


