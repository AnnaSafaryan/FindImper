import os
from flask import Flask, request, session, render_template, redirect, send_file, flash
from apscheduler.schedulers.background import BackgroundScheduler
from io import BytesIO
from zipfile import ZipFile
from os import listdir
from backend.main import search_imps
from utils import *
from config import *

import logging

# TODO: форматы в конфиг
logging.basicConfig(level=logging.INFO,
                    # filename="log_back.log", filemode="w",
                    datefmt='%d/%m/%Y %H:%M:%S',
                    format="%(asctime)s : %(levelname)s : %(message)s")

app = Flask(__name__)

app.secret_key = secret_key.encode()
app.config['UPLOAD_FOLDER'] = data_path
app.config['SCHEDULER_API_INTERVAL'] = check_time
app.config['PORT'] = port
app.config['DEBUG'] = debug


@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # print('start', request.values, request.files, request.url, sep='\n')

        file = request.files.get('file', None)
        if not file:
            # После перенаправления на страницу загрузки
            # покажем сообщение пользователю
            flash('Не могу прочитать файл', 'error')
            return redirect(request.url)

        else:
            filename = get_filename(file)

            if not filename:
                # Если файл не выбран, то браузер может
                # отправить пустой файл без имени.
                flash('Файл пустой!', 'error')
                return redirect(request.url)

            elif not is_allowed(filename, exts):
                flash('Неправильное расширение', 'error')
                return redirect(request.url)

            else:
                filename = get_filename(file)
                try:
                    file.save(path.join(data_path, filename))
                except FileNotFoundError:
                    os.mkdir(data_path)
                    file.save(path.join(data_path, filename))

                context = {
                    "filename": filename,
                    "method": method2name[request.values['method']],
                    # TODO: в интерфейс
                    "tok_forced": def_params['tok_forced'],
                    "prep_forced": def_params['prep_forced'],
                    "test": def_params['test'],
                    # "sm_func": request.values['smoothing'],
                    "rounding": request.values['rounding']
                }

                logging.info([context, verbose])

                try:
                    metrics, paths = search_imps(filename=context["filename"],
                                                 method=request.values['method'],
                                                 tok_forced=context["tok_forced"],
                                                 prep_forced=context["prep_forced"],
                                                 # sm_func=context["sm_func"],
                                                 rounding=int(context["rounding"]),
                                                 test=context["test"],
                                                 verbose=verbose,
                                                 )
                    if metrics:
                        # print(metrics)
                        context["metrics"] = [{'name': metric2name[metric['name']],
                                               'r': metric['r'],
                                               'p': metric['p'],
                                               'f': metric['f'],
                                               }
                                              for metric in metrics]
                    else:
                        context["metrics"] = metrics

                    session["paths"] = paths

                    return render_template('result.html', **context, page_name='/result')

                # TODO: отдельную страницу
                except IndexError:
                    flash('Ошибка разметки', 'error')
                    return redirect(request.url)

    return render_template('main.html', **params, **def_params, page_name='/')


@app.route('/result', methods=['GET', 'POST'])
def result():
    # print('res', request.values, request.files, request.url, sep='\n')

    choice = request.values['download']
    paths = session.get('paths')

    try:
        if choice == 'r':
            res_file = get_filepath('res_file', paths)
            return send_file(
                res_file,
                as_attachment=True,
                download_name=paths['res_file'])

        elif choice == 'm':
            res_file = get_filepath('res_file', paths)
            metric_file = get_filepath('metric_file', paths)

            stream = BytesIO()
            with ZipFile(stream, 'w') as zf:
                for file in [res_file, metric_file]:
                    zf.write(file, path.basename(file))
            stream.seek(0)

            return send_file(
                stream,
                as_attachment=True,
                download_name='{}.zip'.format(path.splitext(paths['res_file'])[0])
            )

        elif choice == '0':
            return redirect('/')

    except FileNotFoundError:
        return render_template('500.html', page_name='/500'), 500


@app.after_request
def clean(response):
    # TODO: ломает скачивание результата, но не архива
    # print(request.endpoint)
    paths = session.get('paths')
    if request.endpoint == "result":
        clean_files(paths)
        # except FileNotFoundError:
        #     redirect("/")

    return response


@app.errorhandler(500)
def not_found_error(error):
    return render_template('500.html', page_name='/500'), 500


@app.route('/faq')
def faq():
    return render_template('faq.html', page_name='faq')


@app.route('/about')
def about():
    return render_template('about.html', page_name='about')


def cleaning():
    for file in listdir(data_path):
        if path.splitext(file.lower())[1] in exts:
            filepath = path.join(app.config['UPLOAD_FOLDER'], file)
            if check_file(filepath, check_time):
                os.remove(filepath)


scheduler = BackgroundScheduler()
scheduler.add_job(func=cleaning, trigger="interval", seconds=check_time)
scheduler.start()

if __name__ == "__main__":
    app.run(port=app.config['PORT'], debug=app.config['DEBUG'])
