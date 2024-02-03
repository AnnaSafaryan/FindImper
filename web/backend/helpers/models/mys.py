from ..models.models import RuleBasedModel
from pymystem3 import Mystem
import re


class Mys(RuleBasedModel):
    def __init__(self, negs, stops, needs, filter_dict):
        super().__init__(negs, stops, needs, filter_dict)
        self.analyzer = Mystem()
        self.name = 'mys'

    def parse_gr(self, gr):
        pos = re.findall(r'[A-Z]+=?', gr)[0].replace('=', '')
        mood = re.findall(r'\bпов\b', gr)
        if mood:
            mood = mood[0]
        else:
            mood = ''
        tense = re.findall(r'\bнепрош\b', gr)
        if tense:
            tense = tense[0]
        else:
            tense = ''
        more = []
        more.extend(re.findall(r'\bприч\b', gr))
        if more:
            more = more[0]
        else:
            more = ''
        return pos, mood, tense, more

    def parse_sent(self, prep_text):
        sent_analysis = []
        res_sent = self.analyzer.analyze(prep_text['sent'])
        for tok in res_sent:
            tok_text = tok['text'].strip()  # удаляем вайтспейсы, а то майстем считает их токенами
            if tok_text:
                try:
                    tok_analysis = tok['analysis'][0]['gr']
                except KeyError:  # у пунктуации нет разбора # TODO: указывать ей часть речи, если в спиксе?
                    tok_analysis = ''
                except IndexError:  # например, "нрзб"
                    # print(tok)
                    # print(tok['analysis'])
                    tok_analysis = ''
                if tok_analysis:
                    pos, mood, tense, more = self.parse_gr(tok_analysis)
                else:
                    pos, mood, tense, more = ('MISC', '', '', '')
                sent_analysis.append({
                    'word': tok_text.lower(),
                    'info': {'pos': pos,
                             'mood': mood,
                             'tense': tense,
                             'more': more},
                    'i': len(sent_analysis)
                })
        return sent_analysis

    def is_conj(self, tok):
        """
        Проверяем токен на союзность
        """
        # TODO: потенциально определяем тип союза
        # TODO: нет разделения на сочинительные и подчинительные
        try:
            if 'CONJ' in tok['info']['pos']:
                return True
        except IndexError:  # пустой разбор
            return False

    def is_neg_part(self, tok):
        """
        Проверяем токен на отрицательную частицу
        """
        try:
            if 'PART' in tok['info']['pos'] and tok['word'] in self.negs:
                return True
        except IndexError:  # пустой разбор
            return False

    def is_verb(self, tok):
        """
        Проверяем токен на глагольность и пропускаем причастия
        """
        # print(tok)
        # print('check')
        try:
            if tok['info']['pos'] == 'V' and 'прич' not in tok['info']['more']:
                return True
        except IndexError:  # пустой разбор
            return False

    def is_imp(self, tok):
        """
        Проверяем токен на повелительность
        """
        try:
            # TODO: объединить
            # TODO: перенести в отдельные функции (общие с пайморфи?)
            word = tok['word'].lower()
            if tok['info']['mood'] == 'пов' and tok['word'] not in self.stops:
                return True
            elif word.endswith('едь') or word.endswith('едьте'):
                return True
            #  TODO: прописать больше условий из ФСП?
            elif tok['info']['tense'] == 'непрош':
                return True
            elif word in self.needs:
                return True
        except IndexError:  # пустой разбор
            return False
