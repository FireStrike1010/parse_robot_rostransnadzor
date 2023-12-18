import sys
import downloader
import warnings
import pandas as pd
warnings.simplefilter(action='ignore', category=FutureWarning)

def all_files(files: dict) -> pd.DataFrame:
    names = list(files.keys())
    links = list(files.values())
    return pd.DataFrame(list(zip(names, links)), columns=['Название документа', 'Ссылка'])

def save_config(filepath: str, df_download: pd.DataFrame, df_all_files: pd.DataFrame, df_settings: pd.DataFrame) -> None:
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        df_download.to_excel(writer, 'Скачиваемые файлы', index=False)
        df_all_files.to_excel(writer, 'Доступные документы', index=False)
        df_settings.to_excel(writer, 'Настройки', index=False)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        print('...Попробуйте "download конфиг.xlsx" или воспользуйтесь "help" для сравки...')
    elif args[0] in ('-h', 'help'):
        print('''-l; -list --- список доступных документов для скачивания
    -d; -download путь_к_файлу_конфига (xlsx) --- скачивает документы по конфигу
    -c; -config --- создает примерный конфиг (xlsx) (Осторожно: перезаписывает config.xlsx)
    -h; help --- показывает данную справку''')
    elif args[0] in ('-l', '-list'):
        files = downloader.get_all_files()
        for i in files:
            print(f'Документ: "{i}"\nСсылка на скачивание: "{files[i]}"\n')
    elif args[0] in ('-c', '-config'):
        from downloader import get_all_files
        df_download = pd.DataFrame([['Лицензирование деятельности по перевозкам внутренним водным транспортом, морским транспортом опасных грузов', '~/Desktop', 'Лицензии по опасным грузам', True, '№ п/п;Лицензиат;ИНН;ОГРН;Дата предоставления/приказа;Номер;Лицензирующий орган', 50]], 
                                    columns=['Название документа', 'Сохранить в', 'Имя файла (можно оставить пустым)', 'Записать дату загрузки в название файла', 'Выбрать столбцы через точку с запятой (можно оставить пустым - выбрать все)', 'Выбрать кол-во строк от начала (можно оставить пустым - выбрать все)'])
        df_all_files = all_files(get_all_files)
        df_settings = pd.DataFrame([[3, 5, 'xlsx']], columns=['Время между попытками (секунды)', 'Кол-во попыток', 'Тип сохраняемых файлов (xlsx, csv, tsv)'])
        save_config('config.xlsx', df_download, df_all_files, df_settings)
    elif args[0] in ('-d', '-download'):
        args = ' '.join(args[1:])
        try:
            df_download = pd.read_excel(args, 'Скачиваемые файлы')
            df_settings = pd.read_excel(args, 'Настройки')
        except:
            print('Неверно указан путь к файлу конфига')
            exit(1)
        restart_time_s = df_settings['Время между попытками (секунды)']
        if len(restart_time_s) == 0:
            restart_time_s = 3
        else:
            restart_time_s = float(restart_time_s.iloc[0])
        restart_tries = df_settings['Кол-во попыток']
        if len(restart_tries) == 0:
            restart_tries = 5
        else:
            restart_tries = int(restart_tries.iloc[0])
        filetype = df_settings['Тип сохраняемых файлов (xlsx, csv, tsv)']
        if len(filetype) == 0 or str(filetype.iloc[0]) not in ('xlsx', 'csv', 'tsv'):
            filetype = 'xlsx'
        else:
            filetype = str(filetype.iloc[0])
        files = downloader.get_all_files(tries=restart_tries, sleep_time_s=restart_time_s)
        for i, doc in df_download.iterrows():
            name = doc['Имя файла (можно оставить пустым)']
            if name == None:
                name = doc['Название документа']
            write_date = str(doc['Записать дату загрузки в название файла']).lower()
            if write_date in ('true', 'y', 'yes', '+', '1', 'да'):
                write_date = True
            else:
                write_date = False
            file_name = downloader.create_file_name(name, write_date, filetype)
            link = files.get(doc['Название документа'])
            if link == None:
                print(f'Документ {doc["Название документа"]} не найден')
                continue
            path_to_save = doc['Сохранить в']
            if path_to_save == None:
                path_to_save = '~/Downloads'
            columns = doc['Выбрать столбцы через точку с запятой (можно оставить пустым - выбрать все)']
            if columns == None:
                columns = 'all'
            else:
                columns = list(str(columns).split(';'))
            length_from_start = doc['Выбрать кол-во строк от начала (можно оставить пустым - выбрать все)']
            if length_from_start == None:
                length_from_start = 'all'
            else:
                length_from_start = int(length_from_start)
            print(f"Загрузка: {doc['Название документа']}...")
            info = downloader.download_doc(link, path_to_file=path_to_save+'/'+file_name, columns=columns, length_from_start=length_from_start, tries=restart_tries, sleep_time_s=restart_time_s, filetype=filetype)
            print(f"Файл {file_name} успешно скачен в {path_to_save}\nСтолбцы: {info.get('columns')}, строки: {info.get('length', 0)}")
        save_config(args, df_download, all_files(files), df_settings)
    else:
        print('...Несуществующая команда, воспользуйтесь "help" для сравки...')