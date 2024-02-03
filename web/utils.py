import time
from werkzeug.utils import secure_filename
from os import path, remove


def is_allowed(filename, extensions):
    """ Функция проверки расширения файла """
    if path.splitext(filename.lower())[1] in extensions:
        return True


def get_filename(file):
    # безопасно извлекаем оригинальное имя файла
    filename = secure_filename(file.filename)
    return filename


def get_filepath(filename, paths_dict):
    return path.join(paths_dict['root'],
                     paths_dict['data_path'],
                     paths_dict[filename])


def check_file(file, period):
    modified_time = path.getmtime(file)
    return time.time() - modified_time > period


def clean_files(paths_dict):
    if path.isfile(get_filepath('data_file', paths_dict)):
        # try:
        #     print('GO')
        files_to_remove = ['data_file', 'res_file', 'metric_file']
        for filename in files_to_remove:
            remove(get_filepath(filename, paths_dict))


