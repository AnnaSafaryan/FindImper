from .models import DepBasedModel
import spacy
from ..config import config

# TODO: убрать ворнинги?

model_name = config.get('Preprocessing parameters', 'spa_name')


class Spa(DepBasedModel):
    def __init__(self, negs, stops, needs, filter_dict):
        super().__init__(negs, stops, needs, filter_dict)
        self.analyzer = spacy.load(model_name)  # TODO: попробовать другие модели
        self.verbs = {'VERB', 'AUX'}
        self.name = '{}_{}'.format('spa', model_name)

    def parse_tok(self, tok):
        return {'word': tok.text.lower(),
                'info': {'pos': tok.pos_,
                         'morph': str(tok.morph).split('|'),
                         'dep': tok.dep_,
                         'children': [self.parse_tok(ch) for ch in tok.children]
                         },
                'i': tok.i
                }

    def parse_sent(self, prep_text):
        sent_analysis = []
        res_sent = self.analyzer(prep_text['sent'])
        for tok in res_sent:
            sent_analysis.append(self.parse_tok(tok))
        return sent_analysis

    def is_verb(self, tok):
        """
        Проверяем токен на глагольность
        """
        if tok['info']['pos'] in self.verbs:
            return True

    def is_neg_part(self, tok):
        """
        Проверяем токен на отрицательную частицу
        """
        if tok['info']['pos'] == 'PART' and tok['word'] in self.negs:
            return True

    def is_sconj(self, tok):
        """
        Проверяем токен на подчинительно-союзность
        """
        if tok['info']['pos'] == 'SCONJ':
            # and tok.text.lower() in self.needs:
            return True

    def is_root(self, tok):
        """
        Проверяем токен на корневость
        """
        if tok['info']['dep'] == 'ROOT':
            return True

    def is_imp(self, tok):
        """
        Проверяем токен на повелительность
        """
        if ('Mood=Imp' in tok['info']['morph'] and tok['word'] not in self.stops) \
                or tok['word'] in self.needs:
            return True


