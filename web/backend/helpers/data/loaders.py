from os import path
import csv
from json import load as jload, dump as jdump
from ..config import config
from .data import get_corpus, tok_corpus, prep_corpus, format_metric
import logging

# TODO: форматы в конфиг
logging.basicConfig(level=logging.INFO,
                    filename="log_back.log", filemode="w",
                    datefmt='%d/%m/%Y %H:%M:%S',
                    format="%(asctime)s : %(levelname)s : %(message)s")


def resolve_paths(filename, data_path, model_name):
    if data_path:
        if isinstance(data_path, list):
            new_data_path = path.join(*data_path)
        else:
            new_data_path = data_path
    else:
        new_data_path = config.get('Files and directories', 'data_path')

    name = path.splitext(filename.lower())[0]
    return {'root': config.get('Files and directories', 'root'),
            'data_path': new_data_path,
            'data_file': filename,
            'tok_file': '{}_tok.json'.format(name),
            'ers_file': '{}_ers.json'.format(name),
            'prep_file': '{}_{}_prep.json'.format(name, model_name),
            'res_file': '{}_{}_res.txt'.format(name, model_name),
            'metric_file': '{}_{}_metrics.txt'.format(name, model_name)  # TODO: почему не джсон?
            }


def convert_encoding(file, encoding='utf-8'):
    s = open(file, 'r').read().encode(encoding, errors="backslashreplace")
    # print(s)
    with open(file, 'wb') as f:
        f.write(s)


def read_file(file):
    # TODO: один текст -- одна строка без абзацев. Научиться распознавать и убирать автоматически?
    # TODO: может быть сплошной текст без разметки
    # убираем пустые строки
    lines = open(file, 'r', encoding='utf-8').readlines()
    with open(file, 'w', encoding='utf-8') as fw:
        fw.write(''.join([line for line in lines if line.strip()]))

    raw_data = {}
    with open(file, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter='\t')
        for i, row in enumerate(csvreader):
            raw_data[str(i)] = {'f_id': row.get('N', 0),
                                'speaker': row.get('S', ''),
                                # TODO: текст должен быть обязательно,
                                #  пустые строки надо убирать --
                                #  иначе неправильно посчитаем метрики
                                'text': row['Text'],
                                'imp': row.get('Imperative', '').strip()
                                }
        fields = tuple(row.keys())

    return raw_data, fields


def intelly_read_file(paths):
    file = path.join(paths['root'],
                     paths['data_path'],
                     paths['data_file']
                     )
    try:
        raw_data, fields = read_file(file)
    except UnicodeError:
        convert_encoding(file)
        raw_data, fields = read_file(file)

    return raw_data, fields


def load_toks(data, paths, tok_forced=False):
    tok_path = path.join(paths['root'],
                         paths['data_path'],
                         paths['tok_file'])
    ers_path = path.join(paths['root'],
                         paths['data_path'],
                         paths['ers_file'])
    if path.isfile(tok_path) and not tok_forced:
        logging.info('Загружаем дамп...')
        toks = jload(open(tok_path, encoding='utf-8'))
        ers = []  # ошибки токенизации не загружаем

    else:  # ничего ещё не токенизировали или принудительно обновляем всё
        toks, ers = tok_corpus(get_corpus(data))

        if ers:
            jdump(ers, open(ers_path, 'w', encoding='utf-8'), indent=4)
            logging.info('{} errors saved in {}'.format(len(ers), ers_path))
        else:
            jdump(toks, open(tok_path, 'w', encoding='utf-8'), indent=4)
            logging.info('{} lines saved in {}'.format(len(toks['texts']), tok_path))

    return toks, ers


def load_preps(toks, morph, paths,prep_forced=False):
    prep_path = path.join(paths['root'],
                          paths['data_path'],
                          paths['prep_file'])
    if path.isfile(prep_path) and not prep_forced:
        preps = jload(open(prep_path, encoding='utf-8'))

    else:  # ничего ещё не разбирали или принудительно обновляем всё
        preps = prep_corpus(toks, morph)
        jdump(preps, open(prep_path, 'w', encoding='utf-8'), indent=4)

    return preps


def write_res(res_dicts, fields, paths):
    file = path.join(paths['root'],
                     paths['data_path'],
                     paths['res_file']
                     )
    with open(file, 'w', encoding='utf-8', newline='') as csvfile:
        csvwriter = csv.DictWriter(csvfile, delimiter='\t', fieldnames=fields, restval='')
        csvwriter.writeheader()
        csvwriter.writerows(res_dicts)


def write_metrics(scores, paths, verbose):
    metric_path = path.join(paths['root'],
                            paths['data_path'],
                            paths['metric_file'])
    score_str = format_metric(scores)
    if verbose:
        print(score_str)

    with open(metric_path, 'w', encoding='utf-8') as f:
        f.write(score_str)
