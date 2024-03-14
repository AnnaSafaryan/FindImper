from rouge_metric import PyRouge


def prep_hyps(hyps_raw):
    return [[hyp] for hyp in hyps_raw]


def prep_refs(refs_raw):
    return [[[ref]] for ref in refs_raw]


def scoring(refs_raw, hyps_raw, round_n):
    hyps = prep_hyps(hyps_raw)
    refs = prep_refs(refs_raw)
    rouge = PyRouge(rouge_n=(1, 2), rouge_l=True, rouge_w=False,
                    rouge_s=False, rouge_su=True, skip_gap=1)
    scores = rouge.evaluate_tokenized(hyps, refs)

    return [{'name': name,
             'r': round(score['r'], round_n),
             'p': round(score['p'], round_n),
             'f': round(score['f'], round_n)
             } for name, score in scores.items()]
