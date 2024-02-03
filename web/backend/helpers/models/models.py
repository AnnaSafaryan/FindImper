from ..data.data import filter_words, get_words


class Model:
    # TODO: утащить принты для фабрики классов с нлп.русвекторес
    def __init__(self, negs, stops, needs, filters):
        self.negs = negs
        self.stops = stops
        self.needs = needs
        self.filters = filters

    def is_neg_part(self, tok):
        pass

    def is_verb(self, tok):
        pass

    def is_imp(self, tok):
        pass


class RuleBasedModel(Model):
    def __init__(self, negs, stops, needs, filters):
        super().__init__(negs, stops, needs, filters)

    def is_conj(self, tok):
        pass

    def add_part(self, toks, parts, part_n=0):
        if toks != parts.get(part_n, []):  # если не продолжаем перебирать ту же часть
            part_n += 1
            parts[part_n] = toks
        return part_n, parts

    def split_sent_recursive(self, analysis, parts, part_n):
        # print('Статус: ', part_n, parts)
        words = get_words(analysis)
        # print(words)

        if ',' not in words:  # простое предложение
            part_n, parts = self.add_part(analysis, parts, part_n)
            # print(part_n, 'Просто', words)
            # print(parts)

        else:  # сложное или осложнённое предложение
            for i, tok in enumerate(analysis[:-1]):
                # ищем пару ", союз"
                if tok['word'] == ',':
                    next_tok = analysis[i + 1]
                    # проверяем следующий токен на союзность
                    # print(next_tok)
                    if self.is_conj(next_tok):
                        # print(tok, next_tok)
                        part_one = analysis[:i]
                        part_two = analysis[i + 1:]
                        part_n, parts = self.add_part(part_one, parts, part_n)
                        # print(part_n, 'Сложно', tuple([get_words(part_one), get_words(part_two)]))
                        # print(len(parts), [get_words(part) for part in parts.values()])
                        # запускаем рекурсию, чтобы поделить и хвост, если надо
                        parts = self.split_sent_recursive(part_two, parts, part_n)
                        return parts

                    else:  # осложнённое предложение TODO: или бессоюзное!
                        part_n, parts = self.add_part(analysis, parts, part_n)
                        # print(part_n, 'Сложно?', words)
                        # print(len(parts), [get_words(part) for part in parts.values()])
        return parts

    def split_sent(self, analysis):
        # TODO: делить прямую речь!
        parts = self.split_sent_recursive(analysis, parts={}, part_n=0)
        return parts

    def imp_part(self, part):
        # print(part)
        part_imps = []
        for i, tok in enumerate(part):
            tok_imp = self.is_imp(tok)  # распознаётся ли токен как повелительный
            # print(1, tok_imp, tok)

            # надо ли его присовокупить к повелительным, если уж начали собирать
            # если уже что-то начали собирать, а токен не повелительный
            if part_imps and not tok_imp:
                if self.is_verb(tok) and tok['word'] not in self.stops:  # глагол
                    tok_imp = True
                    # print(2, tok_imp, tok)
                    # TODO: искать точку остановки (инфинитив) не надо,
                    #  все глаголы в части -- одно наклонение?

            # Проверяем на "-ка"
            # хватит места на x токенов вперёд и дальше "-ка"
            if i + 2 < len(part) \
                    and part[i + 1] == '-' \
                    and part[i + 2] == 'кa':
                tok_imp = True
            elif i + 1 < len(part) and part[i + 1] == '-ка':
                tok_imp = True

            # фильтруем по окружению
            if tok_imp:
                tok_imp = filter_words(part, i, self.filters)

            if tok_imp:
                # отлавливаем отрицание перед токеном
                prev_tok = part[i - 1]
                # print(prev_tok['word'])
                # print(self.is_part(prev_tok))
                if self.is_neg_part(prev_tok):  # раньше была отрицательная частица
                    part_imps.append((prev_tok['i'], prev_tok['word']))  # вставляем её перед словом

                part_imps.append((tok['i'], tok['word']))

        return part_imps

    def imp_sent(self, sent_analysis):
        sent_parts = self.split_sent(sent_analysis)
        # print(len(sent_parts), [get_words(part) for part in sent_parts.values()])
        sent_imps = set()
        for part in sent_parts.values():
            sent_imps.update(self.imp_part(part))
        return sent_imps


class DepBasedModel(Model):
    def __init__(self, negs, stops, needs, filters):
        super().__init__(negs, stops, needs, filters)
        # TODO: перенести общее сюда?

    def is_root(self, tok):
        pass

    def imp_dep_recursive(self, head, dep_imps):
        """
        Цепляем все зависимые глаголы, отрицательные частицы, подчинительные союзы
        + побудительные маркеры для версии с корнями-глаголами
        """
        for ch in head['info']['children']:  # перебираем зависимые
            # глаголы, отрицательные частицы, нужные союзы, побудительные маркеры + нужное
            if self.is_verb(ch) or self.is_neg_part(ch) or self.is_imp(ch):
                dep_imps.append(ch)
            self.imp_dep_recursive(ch, dep_imps)

        return dep_imps

    def imp_head(self, sent):
        '''
        Вершины повелительного наклонения
        '''
        # print('imp head')
        method_imps = []  # работаем с нехэшируемыми словарями, поэтому без множеств
        imp_heads = []
        for tok in sent:
            # print(tok['i'], tok['word'], [ch for ch in tok['info']['children']])
            if self.is_imp(tok):
                # print('imp')
                imp_heads.append(tok)
        # print(get_words(imp_heads))
        method_imps.extend(imp_heads)
        for head in imp_heads:
            head_imps = self.imp_dep_recursive(head, dep_imps=[])
            for head_imp in head_imps:
                if head_imp not in method_imps:
                    method_imps.append(head_imp)
        return set([(tok['i'], tok['word']) for tok in method_imps])

    def verb_root(self, sent):
        '''
        Глаголы-корни с зависимыми побуждениями
        '''
        # print('verb root')
        method_imps = []
        imp_heads = []
        for tok in sent:
            # print(tok['i'], tok['word'], [ch for ch in tok['info']['children']])
            # у глагола-корня есть зависимые побуждения
            if self.is_verb(tok) and self.is_root(tok):
                for ch in tok['info']['children']:  # перебираем зависимые
                    # ищем повелительность
                    if self.is_imp(ch):
                        imp_heads.append(tok)
        # print(get_words(imp_heads))

        for head in imp_heads:
            head_imps = self.imp_dep_recursive(head, dep_imps=[])
            for head_imp in head_imps:
                if head_imp not in method_imps:
                    method_imps.append(head_imp)

        method_imps.extend(imp_heads)
        return set([(tok['i'], tok['word']) for tok in method_imps])

    def imp_sent(self, sent):
        # скорее захватим, чем пропустим, если методы предлагают разное
        sent_imps = self.imp_head(sent)
        sent_imps.update(self.verb_root(sent))
        return sent_imps
