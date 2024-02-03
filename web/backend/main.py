# TODO: правилами отлавливать случаи:
#  Делю предложение на части по запятой перед союзом
#  слово + следующий глагол до инфинитива в этой части
#  точно не подчинительный?
#  сочинительные -- все императив?


def search_imps(filename,
                method,
                tok_forced,
                prep_forced,
                # sm_func,
                rounding,
                data_path='',
                test=False,
                verbose=True):
    # TODO: по умолчанию лучшая модель
    from tqdm import tqdm
    from backend.helpers.data.ling_data import stop_list, need_list, neg_list, filter_dict
    from backend.helpers.data.loaders import resolve_paths, intelly_read_file, load_toks, load_preps, write_res, \
        write_metrics
    from backend.helpers.data.data import get_words, join_ka, format_imps, \
        format_res
    from backend.helpers.models.model_builder import build_morph
    from backend.helpers.metrics.scoring import scoring

    model = build_morph(method)
    morph = model(neg_list, stop_list, need_list, filter_dict)
    if verbose:
        print(morph.name.upper())

    paths = resolve_paths(filename, data_path, morph.name)
    # print(paths)
    # TODO: Дважды храним тексты, проще в токс или препс внести метаданные
    raw_data, fields = intelly_read_file(paths)
    toks = load_toks(raw_data, paths, tok_forced)
    preps = load_preps(toks, morph, paths, prep_forced)
    res_imps = []
    score_data = {'refs': [], 'hyps': []}
    if 'Imperative' not in fields:
        test = False
        fields = tuple(list(fields) + ['Imperative'])

    for i, line in tqdm(preps.items(), desc='Анализируем строки', colour='green'):
        line_imps = [[]] * len(preps[i])
        for j, sent in enumerate(line):
            sent_imps_raw = morph.imp_sent(sent)
            if sent_imps_raw:
                sent_imps_joined = join_ka(sent_imps_raw, sent)
                sent_imps = format_imps(sent_imps_joined)
                line_imps[j] = sent_imps

            if test:
                if toks['imps'][i][j]:  # считаем метрики только без пустых списков
                    # TODO: засчитываются в метриках false positive?

                    score_data['refs'].append(toks['imps'][i][j])
                    score_data['hyps'].append(line_imps[j])

                    if verbose:
                        def verbose_error():
                            print(get_words(sent))
                            print(sent)
                            print(score_data['hyps'][-1], score_data['refs'][-1])
                            print()

                        try:
                            hyp_imps = set(score_data['hyps'][-1])
                            ref_imps = set(score_data['refs'][-1])
                            if verbose == 'all':
                                if hyp_imps != ref_imps:
                                    verbose_error()
                            if verbose == 'prec':
                                if hyp_imps - ref_imps:
                                    verbose_error()
                            if verbose == 'rec':
                                if ref_imps - hyp_imps:
                                    verbose_error()
                        except IndexError:  # пока ничего не добавили в refs
                            continue

        res_imps.append(line_imps)

    metrics = []
    if test:
        metrics = scoring(score_data['refs'], score_data['hyps'], int(rounding))
        # write_metrics(metrics, paths, verbose=verbose)
    res_dicts = format_res(res_imps, raw_data, fields)
    write_res(res_dicts, fields, paths)

    return metrics, paths
