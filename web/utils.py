import logging
import time
from werkzeug.utils import secure_filename
from os import path, remove


def is_allowed(filename, extensions):
    """ Функция проверки расширения файла"""
    if path.splitext(filename.lower())[1] in extensions:
        return True


def get_filename(file):
    """Безопасное извлечение оригинального имени файла"""
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
        names_to_remove = ['data_file', 'res_file', 'metric_file']
        files_to_remove = [get_filepath(filename, paths_dict) for filename in names_to_remove]
        for file in files_to_remove:
            if path.exists(file):
                logging.info('Cleaning {}'.format(file))
                remove(file)
