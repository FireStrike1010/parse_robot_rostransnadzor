import requests
from datetime import datetime
from time import sleep


def get_all_files(tries: int = 5, sleep_time_s: int | float = 3) -> dict:
    '''Возвращает словарь всех разрешительных документов выдаваемых Ространснадзором -> {"Название документа" : "Ссылка на скачивание"}'''
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    mainurl = "https://rostransnadzor.gov.ru/deyatelnost/razresitelnye-dokumenty"
    addurl = "https://rostransnadzor.gov.ru"
    for i in range(tries):
        try:
            soup = requests.get(mainurl, headers=headers)
            break
        except:
            print(f"Отсутствует подключение к интернету, осталось попыток {tries - i}")
            sleep(sleep_time_s)
    else:
        return {}
    if soup.status_code != 200:
        print(f"Не удалось установить соединение с сервером, код ошибки: {soup.status_code}")
        return {}
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(soup.text, 'html.parser')
    links = [x.parent.find_all('a') for x in soup.findAll(class_='card-body card-body_type_document')]
    files = {}
    for i in links:
        link = i[1].get('href')
        if 'http://' not in link and 'https://' not in link:
            link = addurl + link
        name = i[0].get('title')
        files[name] = link
    del BeautifulSoup
    return files

def download_doc(link: str, path_to_file: str, columns: list | str = 'all', length_from_start: int | str = 'all', tries: int = 5, sleep_time_s: int | float = 3, filetype: str = 'xlsx') -> dict:
    '''Скачивает и фильтрует таблицу по столбцам и количеству строк от начала.
    Возвращает словарь метаданных: {"columns": список столбцов, "length": количество строк}'''
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    for i in range(tries):
        try:
            response = requests.get(link, headers=headers)
            break
        except:
            print(f"Отсутствует подключение к интернету, осталось попыток {tries - i}")
            sleep(sleep_time_s)
    else:
        return {}
    if response.status_code != 200:
        print(f"Не удалось установить соединение с сервером, код ошибки: {response.status_code}")
        return {}
    import pandas as pd
    for i in range(50):
        df = pd.read_excel(response.content, skiprows=i)
        if 'Unnamed: 1' not in list(df.columns):
            break
    if columns != 'all':
        df = df[columns]
    if length_from_start != 'all' and len(df) > length_from_start:
        df = df.iloc[:length_from_start]
    if filetype == 'xlsx':
        with pd.ExcelWriter(path_to_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, 'Документ', index=False)
    elif filetype == 'csv':
        df.to_csv(path_to_file)
    elif filetype == 'tsv':
        df.to_csv(path_to_file, sep='\t')
    return {'columns': list(df.columns), 'length': len(df)}

def create_file_name(name: str = '', write_date: bool = True, filetype: str = 'xlsx') -> str:
    '''Создает имя файлу по имени документа'''
    name = name.replace(' ', '_')
    if write_date:
        name = name + '_' + str(datetime.now().date())
    name = name + '.' + filetype
    return name