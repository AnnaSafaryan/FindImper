from tqdm import tqdm
from razdel import sentenize, tokenize
from collections import defaultdict
from operator import add, sub


def if_store(line_lists):
    line_elems = set()
    for e in line_lists:
        if e:
            line_elems.update(e)
    return line_elems


def join_contr(sents):
    new_sents = []
    i = 0
    contr = '(нрзб.)'
    while i < len(sents):
        # если в строке что-то ещё есть
        if contr != sents[i]:
            # но не последнее
            if i != len(sents)-1:
                if sents[i].endswith(contr):
                    new_sents.append(sents[i] + " " + sents[i+1])
                    i += 1
                elif sents[i].endswith(contr[:-1]):
                    new_sents.append(sents[i]+sents[i+1])
                    i += 1
                else:
                    new_sents.append(sents[i])
            # последнее, но что-то было до
            elif len(sents) != 1:
                if new_sents[-1].endswith(contr):
                    new_sents[-1] = new_sents[-1] + ' ' + sents[-1]
                    i += 1
                elif new_sents[-1].endswith(contr[:-1]):
                    new_sents[-1] = new_sents[-1] + sents[-1]
                    i += 1
                else:
                    new_sents.append(sents[i])
            # последнее
            else:
                new_sents.append(sents[i])
        # в строке только сокращение
        else:
            new_sents.append(sents[i])
        i += 1
        # print(i, new_sents)
    return new_sents


def get_corpus(data):
    # TODO: регистр ни у одной модели не влияет?
    # TODO: отбирать по сложности
    return {'texts': {i: data_line['text'].lower() for i, data_line in data.items()},
            'imps': {i: data_line['imp'].lower() for i, data_line in data.items()}}


def tok_corpus(corpus):
    """
    corpus_toks = {
        'texts': {'1': [{'sent': 'иди поспи.',
                         'toks': ['иди', 'поспи', '.']},
                        {'sent': 'хочешь?',
                         'toks': ['хочешь', '?']}
                        ],
                  '2': [{'sent': 'да!', 'toks': ['да', '!']}]
                  },
        'imps': {'1': [['иди', 'поспи'], []],
                 '2': []
                 }
    }
    """
    corpus_toks = {'texts': defaultdict(list),
                   'imps': {}}
    for i in tqdm(corpus['texts'], desc='Токенизируем строки'):
        raw_sents = []  # предложения внутри реплики
        for sent_elem in sentenize(corpus['texts'][i]):  # принудительно делим по многоточию
            sent = sent_elem[-1]
            # print(sent)
            if '…' in sent:
                raw_sents.extend([s for s in sent.split('…') if s])
            elif '...' in sent:
                raw_sents.extend([s for s in sent.split('...') if s])
            else:
                raw_sents.append(sent)

        sents = join_contr(raw_sents)
        for sent in sents:
            toks = tokenize(sent)
            corpus_toks['texts'][i].append({'sent': sent, 'toks': toks})

        line_imps = corpus['imps'][i].split('.')
        sent_imps = [[]] * len(corpus_toks['texts'][i])
        ers = []
        if if_store(line_imps):  # если в столбце побуждений не пустая строка
            for sent in line_imps:
                if sent.strip():
                    num, imp = sent.split(':')
                    num = int(num.strip())-1  # в разметке реальные номера, а не с 0
                    imps = [w.strip() for w in imp.split(',') if w.strip() != '']
                    try:
                        sent_imps[num] = imps
                    except IndexError:
                        ers.append((len(sent_imps), num, sent, corpus['texts'][i]))
                        print(ers[-1])

            corpus_toks['imps'][i] = sent_imps
        else:
            corpus_toks['imps'][i] = sent_imps

        if ers:
            print('\nИСПРАВЬТЕ РАЗМЕТКУ!')
            exit(1)

    return corpus_toks


def prep_corpus(corpus, morph):
    """
    corpus_preps = {'1': [[{'word': 'иди', 'info': parse_tok, 'i: 0},
                           {'word': 'поспи', 'info': parse_tok, 'i: 1},
                           {'word': '.', 'info': parse_tok, 'i: 2}
                           ],
                          [{'word': 'хочешь', 'info': parse_tok, 'i: 0},
                           {'word': '?', 'info': parse_tok, 'i: 1}]
                          ]
                    }
    """

    corpus_preps = {}
    for i, line in tqdm(corpus['texts'].items(), desc='Предобрабатываем строки'):
        line_analysis = [morph.parse_sent(sent) for sent in line]
        corpus_preps[i] = line_analysis

    return corpus_preps


def get_words(analysis):
    # TODO: запихать в класс и переопределить принт?
    return [elem['word'] for elem in analysis]


def filter_words(part, i, filters):
    res = True
    tok = part[i]
    sides = {'left': sub, 'right': add}
    for side in sides:
        word = tok['word']
        if word in filters[side]:
            try:
                oper = sides[side]
                near_tok = part[oper(i, 1)]
                if near_tok['word'] in filters[side][word]:
                    res = False
            except IndexError:
                res = True
        else:
            res = True
    return res


def join_ka(imps, analysis):
    joined_imps = []
    # print(imps)
    # print([(a['i'], a['word']) for a in analysis])
    for imp in imps:
        # проверяем, нет ли дальше в предложении "-ка" или "-, ка"
        imp_i = imp[0]  # т.к. там отсчёт с 0
        try:  # если хватит токенов на один
            if analysis[imp_i + 1]['word'] == '-ка':
                joined_imps.append((imp[0], imp[1] + '-ка'))
            else:  # хватило на один, но не подошло
                try:  # если хватит токенов на два
                    if analysis[imp_i + 1]['word'] == '-' \
                            and analysis[imp_i + 2]['word'] == 'ка':
                        joined_imps.append((imp[0], imp[1] + '-ка'))
                    else:  # токенов хватило и на два, но не подошло
                        joined_imps.append(imp)
                except IndexError:  # не набралось токенов на два, но набралось на один и не подошло
                    joined_imps.append(imp)
        except IndexError:  # не набралось токенов даже на один
            joined_imps.append(imp)

    return joined_imps


def format_imps(imps_set):
    return [w[1] for w in sorted(list(imps_set))]


def format_res(res_imps, raw_data, fields):
    field2name = {'N': 'f_id',
                  'S': 'speaker',
                  'Text': 'text',
                  }

    res_dicts = []
    for line_imps, line_id in zip(res_imps, raw_data):
        if line_imps:
            line_res = '. '.join(
                [', '.join(sent_imps) for sent_imps in line_imps if sent_imps]
            )
        else:
            line_res = ''

        res_dict = {}
        for field in list(fields):
            if field == 'Imperative':
                res_dict[field] = line_res
            else:
                res_dict[field] = raw_data[line_id][field2name[field]]
        res_dicts.append(res_dict)

    return res_dicts


def format_metric(score_dicts):
    score_str = '{}:\t{}\t{}\t{}'
    return '\n'.join(
        [score_str.format(score_dict['name'],
                          score_dict['r'],
                          score_dict['p'],
                          score_dict['f'])
         for score_dict in score_dicts])

