from nltk.translate.bleu_score import corpus_bleu, \
                                        modified_precision, \
                                        closest_ref_length, \
                                        brevity_penalty, \
                                        SmoothingFunction
from statistics import mean


def corpus_m_prec(refs_raw, hyps, n=1, need_prep=False):
    if need_prep:
        refs = prep_refs(refs_raw)
    else:
        refs = refs_raw
    scores = []
    for ref, hyp in zip(refs, hyps):
        m_prec = float(modified_precision(ref, hyp, n=n))
        scores.append(m_prec)
    return mean(scores)


def prep_refs(refs_raw):
    return [[ref] for ref in refs_raw]


def corpus_brev_pen(refs_raw, hyps, need_prep=False):
    if need_prep:
        refs = prep_refs(refs_raw)
    else:
        refs = refs_raw

    scores = []
    for ref, hyp in zip(refs, hyps):
        hyp_len = len(hyp)
        brev_pen = brevity_penalty(closest_ref_length(ref, hyp_len), hyp_len)
        scores.append(brev_pen)
    return mean(scores)


def scoring(refs_raw, hyps, sm_func, n):
    # print(refs_raw)
    # print(hyps)
    refs = prep_refs(refs_raw)

    # TODO: названия для сглаживаний
    sm2func = {'0': SmoothingFunction().method0,
               '1': SmoothingFunction().method1,
               '2': SmoothingFunction().method2,
               '3': SmoothingFunction().method3,
               '4': SmoothingFunction().method4,
               '5': SmoothingFunction().method5,
               '6': SmoothingFunction().method6,
               '7': SmoothingFunction().method7,
               }
    smoothing = sm2func[sm_func]

    bleu1 = corpus_bleu(refs, hyps, weights=(1, 0, 0, 0), smoothing_function=smoothing)
    bleu2 = corpus_bleu(refs, hyps, weights=(1/2, 1/2, 0, 0), smoothing_function=smoothing)
    # bleu3 = corpus_bleu(refs, hyps, weights=(1/3, 1/3, 1/3, 0), smoothing_function=smoothing)
    # bleu4 = corpus_bleu(refs, hyps, weights=(1/4, 1/4, 1/4, 1/4), smoothing_function=smoothing)

    m_prec = corpus_m_prec(refs, hyps, 1)

    brev_pen = corpus_brev_pen(refs, hyps)

    return [{'name': 'bleu_1', 'score': round(bleu1, n)},
            {'name': 'bleu_2', 'score': round(bleu2, n)},
            # {'name': 'bleu_3', 'score': round(bleu3, n)},
            # {'name': 'bleu_4', 'score': round(bleu4, n)},
            {'name': 'm_prec', 'score': round(m_prec, n)},
            {'name': 'brev_p', 'score': round(brev_pen, n)}
            ]
