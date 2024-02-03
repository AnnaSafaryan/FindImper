from ..metrics.rouge import scoring as score_rouge
from ..metrics.bleu import scoring as score_bleu


def scoring(refs, hyps, round_n):
    refs_empt, hyps_empt = [], []
    refs_raw, hyps_raw = [], []
    for ref, hyp in zip(refs, hyps):
        if ref != 'None':
            refs_raw.append(ref)
            hyps_raw.append(hyp)
        else:
            refs_empt.append(ref)
            hyps_empt.append(hyp)

    metrics_rouge = score_rouge(refs_raw, hyps_raw, 3)  # recall
    metrics_bleu = score_bleu(refs_raw, hyps_raw, '0', 3)  # precision

    print(metrics_rouge)
    print(metrics_bleu)

