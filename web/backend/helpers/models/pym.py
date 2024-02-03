from .models import RuleBasedModel
import pymorphy2


class Pym(RuleBasedModel):
    def __init__(self, negs, stops, needs, filter_dict):
        super().__init__(negs, stops, needs, filter_dict)
        self.analyzer = pymorphy2.MorphAnalyzer()
        self.verbs = {'VERB', 'INFN'}
        self.name = 'pym'

    def parse_tok(self, tok):
        res_toks = self.analyzer.parse(tok)
        res_tok = res_toks[0]  # по умолчанию берём первый разбор
        # для полноты берём тот разбор, где есть императив
        for res in res_toks:
            if res.tag.mood == 'impr':
                res_tok = res
        word = res_tok.word
        info = res_tok.tag
        # TODO: пунктуацию записывает как null, сделать тег
        return {'word': word.lower(),
                'info': {'pos': info.POS,
                         'mood': info.mood,
                         'tense': info.tense}
                }

    def parse_sent(self, prep_text):
        # print(prep_text)
        sent_analysis = []
        for i, tok in enumerate(prep_text['toks']):
            res_tok = self.parse_tok(tok)
            sent_analysis.append({
                'word': res_tok['word'].strip(),  # удаляем вайтспейсы
                'info': res_tok['info'],
                'i': i
            })
        return sent_analysis

    def is_conj(self, tok):
        """
        Проверяем токен на союзность
        """
        # TODO: потенциально определяем тип союза
        # TODO: нет разделения на сочинительные и подчинительные
        if tok['info']['pos'] == 'CONJ':
            return True

    def is_neg_part(self, tok):
        """
        Проверяем токен на отрицательную частицу
        """
        if tok['info']['pos'] == 'PRCL' and tok['word'] in self.negs:
            return True

    def is_verb(self, tok):
        """
        Проверяем токен на глагольность
        """
        if tok['info']['pos'] in self.verbs:
            return True

    def is_inf(self, tok):
        """
        Проверяем токен на инфинитивность
        """
        if tok['info']['pos'] == 'INFN':
            return True

    def is_imp(self, tok):
        """
        Проверяем токен на повелительность
        """
        if tok['info']['mood'] == 'impr' and tok['word'] not in self.stops:
            return True
        elif tok['word'].endswith('едь') or tok['word'].endswith('едьте'):
            return True
        #  TODO: прописать больше условий из ФСП?
        elif tok['info']['tense'] == 'pres' or tok['info']['tense'] == 'futr':
            return True
        elif tok['word'] in self.needs:
            return True
